import streamlit as st 
import sqlite3
from datetime import date

st.set_page_config(
    page_title= "Clinic Appointment",
    page_icon="[:)]"
)

conn = sqlite3.connect("clinnic.db")
cursor = conn.cursor()

cursor.execute(""
    CREATE TABLE IF NOT EXISTS appointments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_name TEXT NOT NULL,
        contact TEXT NOT NULL,
        doctor TEXT NOT NULL,
        appointment_date TEXT NOT NULL,
        appointment_time TEXT NOT NULL,
        reason TEXT NOT NULL,
        UNIQUE(doctor, appointment_date, appointment_time)
        )
    ""),

conn.commit()

st.title("Clinic Appointment")
st.write("Book appointment on clinic easily")
st.subheader("Appointment booking")
with st.form("Appointment form"):
    patient_name = st.text_input("Your Name?")
    contact = st.text_input("Contact info here:")
    
    doctor = st.selectbox(
        "Please select your hero",
        ["Dr.Yin", "Dr.Miya", "Dr.Yu Zhong"],
        index=0,
        accept_new_options= False,
        key="doctor_select"
    ) 
    appointment_date = st.date_input(
        "Appointment Date",
        min_value= date.today()
    )
    appointment_time = st.selectbox(
        "Appointment Time",
        ["8:00am to 10:00am", "1:00pm to 5:00pm"]
    )
    reason = st.selectbox(
        "Reason of your visit?",
        ["General checkup", "Consultation"]
    )
    submit = st.form_submit_button("Book my Appointment")
    if submit:
        if not patient_name.strip():
            st.error("Please enter your name")
    elif not patient_name.replace("","").__str__():
        st.error("Nah uh letters only")
    elif not contact.strip():
        st.error("Please enter your name")
    elif not contact.isdigit():
        st.error("Numbers only please")
    elif len(contact)!= 11:
        st.error("Contact number must be 11 digit")
    elif len(patient_name)!= 28:
            st.error("Your name is very long ")
            try:
                cursor.execute("""
                INSERT INTO appointments
                (patient_name, contact, doctor, appointment_date, appointment_time, reason)
                VALUES (?,?,?,?,?,?)""",(
                    patient_name.strip(),
                    contact.strip(),
                    doctor,
                    str(appointment_date),
                    appointment_time,
                    reason       
                )
                )
                conn.commit()
                st.success("Booked Successfully")
            except sqlite3.IntegrityError:
                st.error(
                    "You picked the wrong timing for that doctor for thy is already has an appointment in your desired time date"
                )
                
st.divider()
st.subheader("Booked Appointment")

cursor.execute("""
    SELECT id, patient_name, contact, doctor, appointment_date, appointment_time, reason
    FROM appointments
    ORDER BY appointment_date, appointment_time
    """
)
appointments = cursor.fetchall()
if appointments:
    st.dataframe(
        appointments,
        column_config={
            "1": st.column_config.NumberColumn("ID"),
        },
        use_container_width= True
    )
else:
    st.info("You are in luck for there is no appointment yet in this time and date")
    
conn.close()