import sqlite3
import hashlib

# Inicializa as tabelas
def create_tables():
    conn = sqlite3.connect('app.db')
    c = conn.cursor()
    
    # Tabela de usuários
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    
    # Tabela de workspaces
    c.execute('''
        CREATE TABLE IF NOT EXISTS workspaces (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            name TEXT NOT NULL,
            FOREIGN KEY (username) REFERENCES users (username)
        )
    ''')
    
    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def add_user(username, name, password):
    conn = sqlite3.connect('app.db')
    c = conn.cursor()
    c.execute('INSERT INTO users (username, name, password) VALUES (?, ?, ?)', (username, name, hash_password(password)))
    conn.commit()
    conn.close()

def authenticate(username, password):
    conn = sqlite3.connect('app.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, hash_password(password)))
    user = c.fetchone()
    conn.close()
    return user

def create_workspace(username, workspace_name):
    conn = sqlite3.connect('app.db')
    c = conn.cursor()
    c.execute('INSERT INTO workspaces (username, name) VALUES (?, ?)', (username, workspace_name))
    conn.commit()
    conn.close()

def remove_workspace(username, workspace_name):
    conn = sqlite3.connect('app.db')
    c = conn.cursor()
    c.execute('DELETE FROM workspaces WHERE username = ? AND name = ?', (username, workspace_name))
    conn.commit()
    conn.close()


def list_workspaces(username):
    conn = sqlite3.connect('app.db')
    c = conn.cursor()
    c.execute('SELECT name FROM workspaces WHERE username = ?', (username,))
    workspaces = c.fetchall()
    conn.close()
    return [workspace[0] for workspace in workspaces]

# Inicializa as tabelas
create_tables()