import streamlit as st
import pandas as pd
from main import config
from app.services import list_s3, get_s3_file
from app.utils import get_s3_filename, get_file_extension, clear_session_cache
import app.dp_actions as actions
from inspect import getmembers, isfunction

config()
session = st.session_state["data_preparation"] if "data_preparation" in st.session_state else None

st.title("Data Preparation")

# Data preparation for selected data
def process_df(df: pd.DataFrame):
    try:
        st.markdown("**Steps**")
        if "steps" in session:
            steps = session["steps"]
            for i in range(len(steps)):
                st.markdown(f"- {steps[i]["column"]}: {steps[i]["action"]}")
                if "delimiter" in steps[i]:
                    st.markdown(f"{"&nbsp;" * 8}Delimiter: {steps[i]["delimiter"]}")
                    st.markdown(f"{"&nbsp;" * 8}Split Limit: {steps[i]["split_limit"]}")
                if "group_column" in steps[i]:
                    st.markdown(f"{"&nbsp;" * 8}Group column: {steps[i]["group_column"]}")
                if "date_format" in steps[i]:
                    st.markdown(f"{"&nbsp;" * 8}Date Format: {steps[i]["date_format"]}")
                if "phone_format" in steps[i]:
                    st.markdown(f"{"&nbsp;" * 8}Phone Format: {steps[i]["phone_format"]}")

                if st.button("❌ Remove", key=f"remove-step-{i}"):
                    session["steps"].pop(i)
                    st.rerun()
        else:
            st.write("No steps were assigned to the preparation process.")
        with st.popover("➕ Add step"):
            column = st.selectbox("Column", df.columns, index=None)
            action = st.selectbox("Action", actions.list_actions(), index=None, disabled = not column)
            params = actions.add_action_parameters(action, df.columns.drop(column)) if column else None
            if st.button("Create step", disabled = not column or not action):
                if "steps" not in session:
                    session["steps"] = []
                step_dict = {"column":column, "action":action}
                if params:
                    step_dict.update(params)
                session["steps"].append(step_dict)
                st.rerun()

        st.markdown("**Preview**")
        df_before_rows, df_before_cols = df.shape
        medians = None
        if "steps" in session:
            for step in session["steps"]:
                match step["action"]:
                    case "Remove column":
                        df = actions.remove_column(df, step["column"])
                    case "Split column":
                        df = actions.split_column(df, step["column"], step["delimiter"], step["split_limit"])
                    case "Remove rows with empty values":
                        df = actions.remove_empty_rows(df, step["column"])
                    case "Fill empty values with zeroes":
                        df = actions.fill_empty_values_with_zeroes(df, step["column"])
                    case "Fill empty values with the median of a group column":
                        df, medians = actions.fill_empty_values_with_median(df, step["column"], step["group_column"])
                    case "Format dates":
                        df[step["column"]] = actions.format_dates(df, step["column"], step["date_format"])
                    case "Format phone numbers":
                        df[step["column"]] = actions.format_phone_number(df, step["column"], step["phone_format"])
        st.dataframe(df, hide_index=True)
        st.button('Export Data', type='primary')

        df_after_rows, df_after_cols = df.shape
        st.markdown("**File Structure after Processing**")
        st.write(pd.DataFrame(
            [
                [df_before_rows, df_after_rows],
                [df_before_cols, df_after_cols]
            ],
            index=['Row Count', 'Column Count'],
            columns=['Before', 'After']
        ))
        if medians is not None:
            st.markdown("**Obtained Medians**")
            st.dataframe(medians)
        session["dataframe"] = df
    except Exception as e:
        st.error(f"An error has occurred: {e}")


# Data selection
with st.spinner("Retrieving data..."):
    if "data_preparation" not in st.session_state:
        list = list_s3("input")
        if list:
            list = pd.DataFrame(list)
            list["Name"] = list["Key"].apply(get_s3_filename)
            st.session_state["data_preparation"] = {
                "data_list": list["Name"].tolist(),
                "selected_data": None
            }
    if "data_preparation" in st.session_state:
        session = st.session_state["data_preparation"]
        data_list = session["data_list"]
        if session["selected_data"]:
            index = data_list.index(session["selected_data"])
        else:
            index = None
        select_df = st.selectbox("Choose a data file:", data_list, index)
        if select_df and select_df != session["selected_data"]:
            file = get_s3_file(select_df, "input")
            match get_file_extension(select_df):
                case "csv": 
                    session["dataframe"] = pd.read_csv(file)
                case "json": 
                    session["dataframe"] = pd.read_json(file)
            session["selected_data"] = select_df
            if "steps" in session:
                del session["steps"]
            st.rerun()
        if "dataframe" in session:
            process_df(session["dataframe"])
    else:
        st.write("You have not imported any data")