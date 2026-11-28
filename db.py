
import streamlit as st
import mysql.connector
from mysql.connector import Error


def get_connection():
    """Create and return a MySQL database connection."""
    try:
        return mysql.connector.connect(
            host=st.secrets["mysql"]["host"],
            port=int(st.secrets["mysql"]["port"]),
            database=st.secrets["mysql"]["database"],
            user=st.secrets["mysql"]["user"],
            password=st.secrets["mysql"]["password"]
        )

    except (Error, KeyError, TypeError, ValueError) as error:
        st.error(f"Database connection failed: {error}")
        return None


def fetch_all(query, params=None):
    """Fetch multiple records from MySQL."""
    connection = get_connection()

    if connection is None:
        return []

    cursor = None

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query, params or ())
        return cursor.fetchall()

    except Error as error:
        st.error(f"Database read error: {error}")
        return []

    finally:
        if cursor is not None:
            cursor.close()
        connection.close()


def fetch_one(query, params=None):
    """Fetch one record from MySQL."""
    connection = get_connection()

    if connection is None:
        return None

    cursor = None

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query, params or ())
        return cursor.fetchone()

    except Error as error:
        st.error(f"Database read error: {error}")
        return None

    finally:
        if cursor is not None:
            cursor.close()
        connection.close()


def execute_query(query, params=None):
    """Insert, update or delete records in MySQL."""
    connection = get_connection()

    if connection is None:
        return False

    cursor = None

    try:
        cursor = connection.cursor()
        cursor.execute(query, params or ())
        connection.commit()
        return True

    except Error as error:
        connection.rollback()
        st.error(f"Database operation failed: {error}")
        return False

    finally:
        if cursor is not None:
            cursor.close()
        connection.close()


def test_connection():
    """Check whether BIN2CHAIN can connect to MySQL."""
    connection = get_connection()

    if connection is None:
        return False

    cursor = None

    try:
        cursor = connection.cursor()
        cursor.execute("SELECT DATABASE()")
        database_name = cursor.fetchone()[0]

        st.success(f"MySQL connected successfully: {database_name}")
        return True

    except Error as error:
        st.error(f"MySQL test failed: {error}")
        return False

    finally:
        if cursor is not None:
            cursor.close()
        connection.close()
