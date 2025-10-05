import streamlit as st
import pandas as pd
from datetime import datetime
import mysql.connector
import hashlib

conn = mysql.connector.connect(
    host="localhost",      
    user="root",           
    password="root", 
)
cursor = conn.cursor()
new_database = "CREATE DATABASE IF NOT EXISTS projectdb"
cursor.execute(new_database)
cursor.execute("USE projectdb")


st.title("Client Query Management System")

name_1 = st.text_input("**Enter your username**")
Password_1 = st.text_input("**Enter your password**")
Role_1 = st.selectbox('**Select your role**',["None","client","Support"])

hash_password = hashlib.sha256(Password_1.encode()).hexdigest()

Login_page = st.button("**Login**")
New_user = st.button("**New User**")


cursor.execute("""CREATE TABLE IF NOT EXISTS Users(
                name VARCHAR(20),
                Password TEXT,
                ROLE TEXT)""")


cursor.execute("""CREATE TABLE IF NOT EXISTS clientdetails(
               name VARCHAR(20),
               query_id_number VARCHAR(7),
               Email TEXT,
               Number int,
               heading TEXT,
               description TEXT)""")
conn.commit()
# To add Priority column using date raised cloumn
def priority():
    df = pd.read_csv(r"C:\Users\SAMBANDAM\Documents\VSCODE\synthetic_client_queries.csv")

    start_date_1 = datetime(2025,1,1)
    end_date_1 = datetime(2025,3,31)
    start_date_2 = datetime(2025,3,31)
    end_date_2 = datetime(2025,7,1)
    start_date_3 = datetime(2025,7,1)
    end_date_3 = datetime(2025,9,20)

    for i, date in enumerate(df['date_raised']):
        date = pd.to_datetime(date)
        if start_date_1 < date <= end_date_1:
            df.loc[i, 'priority'] = 1
        elif start_date_2 < date <= end_date_2:
            df.loc[i, 'priority'] = 2
        elif start_date_3 < date <= end_date_3:
            df.loc[i, 'priority'] = 3
        else:
            df.loc[i, 'priority'] = 4

    df.to_csv(r"C:\Users\SAMBANDAM\Documents\VSCODE\synthetic_client_queries.csv", index=False)

capture_date = None
capture_time = None
# To save client data(new)
def client_entry(cilent_name,cilent_Email, Number, Query1, Query2, capture_date):
    if cilent_name and cilent_Email and Number and Query1 and Query2:
       df = pd.read_csv(r"C:\Users\SAMBANDAM\Documents\VSCODE\synthetic_client_queries.csv")
       last_query = df['query_id'].iloc[-1]
       last_id_number = last_query[1:5]
       new_query_number = int(last_id_number) + 1
       last_query_id = 'Q' + str(new_query_number)
       new_data = {
            'query_id': last_query_id,
            'client_email': cilent_Email,
            'client_mobile': Number,
            'query_heading': Query1,
            'query_description': Query2,
            'status':  'opened',
            'date_raised': capture_date}
       new_row = pd.DataFrame([new_data]) 
       df = pd.concat([df,new_row],axis=0) 
       df.to_csv(r"C:\Users\SAMBANDAM\Documents\VSCODE\synthetic_client_queries.csv", index=False)
       cursor.execute("""
            INSERT INTO clientdetails(name, query_id_number, Email, Number, heading, description) 
            VALUES (%s, %s, %s, %s, %s, %s)""", 
            (cilent_name, last_query_id, cilent_Email, Number, Query1, Query2))
       conn.commit()  
    else:
        return None
#To view client page details
def client_page():
    if Role_1 == "client":
        st.title("Client Query Page")
        background_image = "https://www.shutterstock.com/image-photo/contact-us-concept-show-icon-600nw-2557141425.jpg"
        st.markdown(
            f"""
            <style>
            .stApp {{
                background-image: url("{background_image}");
                background-size: cover;
                background-repeat: no-repeat;
                background-attachment: fixed;
            }}
            </style>
            """, unsafe_allow_html=True)
        cilent_name = st.text_input("**Enter your name**", key="client_name_input")
        cilent_Email = st.text_input("**Enter your Email ID**", key="client_email_input")
        Number = st.text_input("**Enter your Mobile Number**", key="client_number_input")
        Query1 = st.text_input("**Enter your Query Heading**", key="client_heading_input")
        Query2 = st.text_input("**Enter your Query Description**", key="client_des_input")

        if st.button("**submit**", key="submit_button_1"):
            datetime_calc = datetime.now()
            capture_date = datetime_calc.date()
            st.write("Successfully submitted")
            st.write(f"**Query_created_time: {datetime_calc}**")
            st.write("**Status = open**")
            client_entry(cilent_name, cilent_Email, Number, Query1, Query2, capture_date)
        if st.button("**Assign priority**"):
               priority()
#To view support page details
def support_page():
    if Role_1 == "Support":
        st.title("Support Dashboard")
        st.markdown(
            f"""
            <style>
            .stApp {{
                background-image: url("https://img.freepik.com/premium-vector/abstract-technology-background_41981-652.jpg?semt=ais_incoming&w=740&q=80");
                background-size: cover;
                background-repeat: no-repeat;
                background-attachment: fixed;
            }}
            </style>
            """, unsafe_allow_html=True)
        
        df = pd.read_csv(r"C:\Users\SAMBANDAM\Documents\VSCODE\synthetic_client_queries.csv")
        st.write(df)
        st.write(df.tail(1))

        Column_filter = st.multiselect(
            "**Select the columns you want to view:**",
            ["query_id", "client_email", "client_mobile", "query_heading", "query_description",
             "status", "date_raised", "date_closed", "priority"])
        if Column_filter:
            st.write(df[Column_filter])
        closure_query = st.text_input("**Enter your query id**", key="query_id_status")
        
        if closure_query:
            closure_status = st.selectbox("**Enter your current status**", ["open","inprogress", "closed"])
        
        if st.button("**submit**", key="submit_button_2"):
            capture_time = datetime.now().time()
            st.write(f"**Query_status:{closure_status}, {capture_time}**")
        
        if st.button("**New data**"):
            cursor.execute('SELECT * FROM clientdetails')
            data = cursor.fetchall()
            column_names = ['name', 'user_id', 'Email', 'Number', 'heading', 'description']
            df_new = pd.DataFrame(data, columns=column_names)
            st.write(df_new)

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_role' not in st.session_state:
    st.session_state.user_role = None


if Login_page:
    cursor.execute("SELECT * FROM Users WHERE name = %s AND Password = %s AND ROLE = %s",
                   (name_1, hash_password, Role_1))
    result = cursor.fetchone()
    if result:
        st.success("**Login Successful**")
        st.session_state.logged_in = True
        st.session_state.user_role = Role_1
    else:    
        st.warning("Invalid username/password/role")
elif New_user:
    cursor.execute("SELECT * FROM Users WHERE name = %s AND role = %s", (name_1, Role_1))
    existing_user = cursor.fetchone()

    if existing_user:
        st.warning("User already exists. Please login instead.")
    else:
        cursor.execute("INSERT INTO Users(name, password, role) VALUES (%s, %s, %s)", (name_1, hash_password, Role_1))
        conn.commit()
        st.success("New user registered successfully!")
        st.session_state.logged_in = True
        st.session_state.user_role = Role_1
    
if st.session_state.logged_in == True:
    if st.session_state.user_role == "client":
        client_page()
    elif st.session_state.user_role == "Support":
        support_page()