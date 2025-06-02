import streamlit as st
import mysql.connector
import pandas as pd
from streamlit_ace import st_ace
from streamlit_option_menu import option_menu
import matplotlib.pyplot as plt
import os

# --- Page Configuration ---
st.set_page_config(page_title="Xploria Data Explorer", layout="wide")

# --- CSS Styling ---
st.markdown("""
    <style>
        html, body, [class*="css"] {
            background-color: #0E1117;
            color: white;
            font-family: 'Segoe UI', sans-serif;
        }
        .main {
            background-color: #0E1117;
        }
        .block-container {
            padding: 2rem 2rem;
        }
        h1 {
            font-size: 36px !important;
            font-weight: 800;
            color: #00AEEF;
            margin-bottom: 10px;
        }
        .section-header {
            font-size: 22px;
            font-weight: 700;
            color: #00BFFF;
            margin-top: 25px;
            margin-bottom: 10px;
        }
        .stButton>button {
            background-color: #007ACC;
            color: white;
            border-radius: 5px;
            padding: 8px 16px;
            font-weight: 600;
            border: none;
        }
        .stButton>button:hover {
            background-color: black;
            color: white;
        }
    </style>
""", unsafe_allow_html=True)

# --- MySQL Connection ---
def get_connection():
    try:
        return mysql.connector.connect(
            host=os.environ.get("DB_HOST", "sql5.freesqldatabase.com"),
            user=os.environ.get("DB_USER", "sql5782627"),
            password=os.environ.get("DB_PASS", "l9JXWgGqPz"),
            database=os.environ.get("DB_NAME", "sql5782627")
        )
    except mysql.connector.Error as e:
        st.error(f"Database connection error: {e}")
        return None

conn = get_connection()


# --- Sidebar Navigation Menu ---
with st.sidebar:
    selected_option = option_menu(
        menu_title="Xploria Navigation",
        options=["Xploria Overview", "Database Tables", "SQL Query Editor", "Database Designer", "Analytics & Insights"],
        icons=["house-fill", "table", "terminal", "database", "bar-chart-line-fill"],
        menu_icon="grid-fill",
        default_index=0,
        styles={
            "container": {"padding": "10px", "background-color": "#1f1f1f"},
            "icon": {"color": "white", "font-size": "18px"},  
            "nav-link": {
                "font-size": "16px",
                "text-align": "left",
                "margin": "4px 0",
                "--hover-color": "#2a2a2a",
            },
            "nav-link-selected": {"background-color": "#007ACC", "color": "white"},
        },
    )

# --- Page: Overview ---
if selected_option == "Xploria Overview":
    st.markdown("<h1>Xploria Data Explorer</h1>", unsafe_allow_html=True)
    st.markdown("""
    Welcome to the **Xploria Data Explorer** - a streamlined interface built to manage and analyze data 
    scraped from the Xploria website.

    ### Application Workflow:
    1. **Scraping**: Data is programmatically scraped from Xploria using web scraping scripts.
    2. **Storage**: Scraped data is stored in a MySQL database (`Faisal_Data`).
    3. **Exploration**: This Streamlit dashboard connects to the database, offering:
       - On-demand access to tables
       - SQL query execution
       - Database Designer
       - Dashboard analytics and insights

    This platform is ideal for data analysts, engineers, and product teams seeking to interactively explore, validate, and visualize live Xploria data.
    """)

# --- Page: Table Explorer ---
elif selected_option == "Database Tables":
    st.markdown("<h1>Database Table Viewer</h1>", unsafe_allow_html=True)
    if conn:
        cursor = conn.cursor()
        cursor.execute("SHOW TABLES")
        tables = [t[0] for t in cursor.fetchall()]
        table_name = st.selectbox("Select a table", tables)

        if st.button("Load Table Data"):
            try:
                df = pd.read_sql(f"SELECT * FROM `{table_name}` LIMIT 100", conn)
                st.dataframe(df, use_container_width=True)
                st.caption(f"Showing top 100 rows from **{table_name}**")
            except Exception as e:
                st.error(f"Error fetching data: {e}")
    else:
        st.warning("Unable to connect to MySQL database.")



# 3. SQL Query Editor
elif selected_option == "SQL Query Editor":
    st.markdown("<h1>SQL Query Editor</h1>", unsafe_allow_html=True)
    st.markdown("""
    Use the editor below to write and execute your custom SQL queries against the connected MySQL database.
    You may enter multiple SQL statements separated by semicolons (`;`). Select which query to run from the dropdown.
    """)

    # Use Ace Editor for SQL input
    sql_input = st_ace(
        placeholder="Write your SQL queries here...",
        language="sql",
        theme="tomorrow_night_bright",  
        font_size=16,
        tab_size=4,
        show_gutter=True,
        show_print_margin=False,
        wrap=True,
        auto_update=True,
        key="ace_editor",
        min_lines=10,
        height=250,
    )

    if sql_input and sql_input.strip():
        queries = [q.strip() for q in sql_input.split(";") if q.strip()]
        selected_query = st.selectbox("Select query to execute:", queries)

        if st.button("Execute Query"):
            if conn:
                try:
                    result_df = pd.read_sql(selected_query, conn)
                    st.dataframe(result_df, use_container_width=True)
                    st.success("Query executed successfully.")
                except Exception as e:
                    st.error(f"Query execution error: {e}")
            else:
                st.warning("Database connection is not established.")
    else:
        st.info("Enter one or more SQL queries above to begin.")


# 4. Database Designer
elif selected_option == "Database Designer":
    st.markdown("<h1>Database Designer</h1>", unsafe_allow_html=True)
    
    designer_tabs = st.tabs(["Create Database", "Create Table", "Insert Data"])

    # --- Tab 1: Create Database ---
    with designer_tabs[0]:
        st.subheader("Create New Database")
        new_db = st.text_input("Enter database name:")
        if st.button("Create Database"):
            try:
                temp_conn = mysql.connector.connect(
                    host="localhost",
                    user="root",
                    password="Faisal$123"
                )
                temp_cursor = temp_conn.cursor()
                temp_cursor.execute(f"CREATE DATABASE {new_db}")
                temp_conn.commit()
                st.success(f"Database `{new_db}` created successfully!")
            except Exception as e:
                st.error(f"Error creating database: {e}")

    # --- Tab 2: Create Table ---
    with designer_tabs[1]:
        st.subheader("Create Table in Current DB")
        table_name = st.text_input("Enter table name:")
        columns_input = st.text_area("Define columns (e.g., id INT PRIMARY KEY, name VARCHAR(50))")
        if st.button("Create Table"):
            if conn:
                try:
                    cursor = conn.cursor()
                    cursor.execute(f"CREATE TABLE {table_name} ({columns_input})")
                    conn.commit()
                    st.success(f"Table `{table_name}` created successfully!")
                except Exception as e:
                    st.error(f"Error creating table: {e}")
            else:
                st.warning("No database connection.")

    # --- Tab 3: Insert Data ---
    with designer_tabs[2]:
        st.subheader("Insert Data into Table")
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("SHOW TABLES")
                tables = [t[0] for t in cursor.fetchall()]
                selected_table = st.selectbox("Choose a table to insert into:", tables)
                col_info = []

                if selected_table:
                    cursor.execute(f"DESCRIBE {selected_table}")
                    col_info = cursor.fetchall()
                    values = []
                    for col in col_info:
                        val = st.text_input(f"Enter value for '{col[0]}' ({col[1]}):")
                        values.append(val)

                    if st.button("Insert Record"):
                        placeholders = ", ".join(["%s"] * len(values))
                        columns = ", ".join([col[0] for col in col_info])
                        insert_query = f"INSERT INTO {selected_table} ({columns}) VALUES ({placeholders})"
                        try:
                            cursor.execute(insert_query, values)
                            conn.commit()
                            st.success("Record inserted successfully.")
                        except Exception as e:
                            st.error(f"Insert failed: {e}")
            except Exception as e:
                st.error(f"Could not fetch tables: {e}")
        else:
            st.warning("Database connection not established.")

# Step 5: Dashbaord & Analytics
elif selected_option == "Analytics & Insights":
    st.markdown("<h1>Analytics & Insights</h1>", unsafe_allow_html=True)
    if conn:
        cursor = conn.cursor()
        cursor.execute("SHOW TABLES")
        tables = [t[0] for t in cursor.fetchall()]
        row_counts = []

        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM `{table}`")
                count = cursor.fetchone()[0]
                row_counts.append(count)
            except:
                row_counts.append(0)

        df_summary = pd.DataFrame({"Table": tables, "Rows": row_counts}).sort_values(by="Rows", ascending=False)
        st.markdown("<h3>Database Overview</h3>", unsafe_allow_html=True)
        st.dataframe(df_summary, use_container_width=True)

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Row Count per Table**")
            st.bar_chart(df_summary.set_index('Table')['Rows'])

        with col2:
            st.markdown("**Tools by Rating (if available)**")
            try:
                rating_df = pd.read_sql("""
                    SELECT rating_stars, COUNT(*) as count
                    FROM CategoryAI
                    GROUP BY rating_stars
                """, conn)
                st.bar_chart(rating_df.set_index('rating_stars')['count'])
            except:
                st.info("Rating data not available. Check `CategoryAI` table structure.")
    else:
        st.warning("Database connection failed. Please check credentials.")
