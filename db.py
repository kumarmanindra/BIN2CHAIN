
import streamlit as st

try:
    import mysql.connector
    from mysql.connector import Error
except ImportError:
    mysql = None
    Error = Exception
else:
    mysql = mysql.connector


def mysql_is_configured():
    """Check whether MySQL credentials are available."""
    try:
        return (
            mysql is not None
            and "mysql" in st.secrets
            and all(
                key in st.secrets["mysql"]
                for key in ("host", "port", "database", "user", "password")
            )
        )
    except Exception:
        return False


def get_connection():
    """Connect to MySQL only when credentials are configured."""
    if not mysql_is_configured():
        return None

    try:
        return mysql.connect(
            host=st.secrets["mysql"]["host"],
            port=int(st.secrets["mysql"]["port"]),
            database=st.secrets["mysql"]["database"],
            user=st.secrets["mysql"]["user"],
            password=st.secrets["mysql"]["password"],
            connection_timeout=5
        )
    except (Error, KeyError, TypeError, ValueError) as error:
        st.warning(f"MySQL is unavailable. JSON demo mode can be used. Details: {error}")
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
        if cursor:
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
        if cursor:
            cursor.close()
        connection.close()


def execute_query(query, params=None):
    """Execute a MySQL insert, update or delete."""
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
        if cursor:
            cursor.close()
        connection.close()


def test_connection():
    """Test MySQL only when configured."""
    connection = get_connection()

    if connection is None:
        st.info("MySQL is not configured. Use JSON demo mode.")
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
        if cursor:
            cursor.close()
        connection.close()
