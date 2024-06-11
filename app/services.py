import boto3
import streamlit as st
import os

s3 = boto3.client('s3', 
    aws_access_key_id = os.getenv("aws_access_key_id"),
    aws_secret_access_key = os.getenv("aws_secret_access_key"), 
    region_name="sa-east-1"
)
bucket = "datablue-workspaces"

def list_s3(path):
    response = s3.list_objects_v2(
        Bucket = bucket,
        Prefix = f"{st.session_state["workspace"]}/{path}"
    )
    return response["Contents"] if "Contents" in response else None

def upload_s3(files, path):
    for file in files:
        s3.put_object(
            Body = file,
            Bucket = bucket,
            Key = f"{st.session_state["workspace"]}/{path}/{file.name}"
        )

def delete_s3(files, path):
    objects = map(lambda filename: {
        "Key": f"{st.session_state["workspace"]}/{path}/{filename}"
    }, files)
    s3.delete_objects(
        Bucket = bucket,
        Delete = {
            "Objects": list(objects)
        }
    )

def get_s3_file(filename, path):
    response = s3.get_object(
        Bucket = bucket,
        Key = f"{st.session_state["workspace"]}/{path}/{filename}"
    )
    return response["Body"] if "Body" in response else None

def get_s3_download_url(key):
    return s3.generate_presigned_url("get_object", Params={
        "Bucket": bucket,
        "Key": key
    })