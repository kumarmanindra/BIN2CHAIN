import streamlit as st
from db import test_connection

st.title("BIN2CHAIN - MySQL Connection Test")

if st.button("Test MySQL Connection"):
    if test_connection():
        st.success("Database connection is working!")
    else:
        st.error("Database connection failed.")