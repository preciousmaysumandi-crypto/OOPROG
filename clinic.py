import streamlit as st
import sqlite3
import re
from datetime import date
st.set_page_config(layout="wide")
st.markdown("""
    <style>
    .block_container {
        max-width: 100%; !important;
        padding-left; 3rem !important;
        padding-right; 3rem !important;
    }
    </style>
""", unsafe_allow_html=True)
    
    

# PAGE CONFIGURATION
st.set_page_config(
    page_title="Clinic Appointment System",
    page_icon="🏥",
    layout="centered"
)

# CUSTOM CSS STYLING
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        width: 100%;
        background-color: #0d6efd;
        color: white;
        font-weight: bold;
        border-radius: 8px;
        padding: 0.5rem;
        border: none;
    }
    .stButton>button:hover {
        background-color: #0b5ed7;
        color: white;
    }
    div.stAlert {
        border-radius: 8px;
    }
    .metric-card {
        background-color: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# DATABASE CLASS
class Database:
    def __init__(self, database_name="clinnic.db"):
        self.database_name = database_name
        self.create_table()

    def connect(self):
        connection = sqlite3.connect(self.database_name)
        connection.execute("PRAGMA foreign_keys = ON")
        connection.row_factory = sqlite3.Row
        return connection

    def create_table(self):
        with self.connect() as connection:
            connection.execute("""
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
            """)
            connection.commit()

    def execute(self, query, values=()):
        with self.connect() as connection:
            cursor = connection.execute(query, values)
            connection.commit()
            return cursor.lastrowid

    def fetch_all(self, query, values=()):
        with self.connect() as connection:
            rows = connection.execute(query, values).fetchall()
            return [dict(row) for row in rows]

# Initialize Database object
db = Database("clinnic.db")

# HEADER SECTION
st.title("CarePlus Clinic Management")
st.markdown("Easily schedule and manage your medical appointments with our expert specialists.")
st.markdown("---")

# APPOINTMENT BOOKING FORM
col_left, col_right = st.columns([2, 1])
col1, col2 = st.columns([1, 1], gap="medium")

with col_left:
    st.subheader("Book an Appointment")
    with st.form("Appointment form"):
        patient_name = st.text_input("Full Name", placeholder="Enter your full name")
        contact = st.text_input("Contact Number", placeholder="09XXXXXXXXX (11 digits)")
        
        doctor = st.segmented_control(
            "Select Doctor / Specialist",
            ["Dr. Angela", "Dr. Estes", "Dr. Floryn"],
            default="Dr. Angela"
        ) 
        
        appointment_date = st.date_input(
            "Appointment Date",
            min_value=date.today()
        )
        
        appointment_time = st.segmented_control(
            "Appointment Time Slot",
            ["8am-9am", "9am-10am","10am-11am","1pm-2pm", "2pm-3pm", "3pm-4pm"]
        )
        
        booked_data = db.fetch_all(
            """
            SELECT appointment_time FROM appointments
            WHERE doctor = ? AND appointment_date = ?
            """,
            (doctor, appointment_date),
                        )
        
        booked_slots = [row[0] for row in booked_data]
        
        all_slots = [
            "8am-9am",
            "9am-10am",
            "10am-11am",
            "1pm-2pm",
            "2pm-3pm",
            "3pm-4pm",
        ]
        time_options = [
            f"{slot} (unavailable)" if slot in booked_slots 
            else f"{slot}(available)"
            for slot in all_slots
        ]
        
        selected_time_display = st.segmented_control(
            "Appointment Time Slot", time_options
        )
        
        appointment_time = (
            selected_time_display.split("(")[0] if selected_time_display else None
        )
        
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            submit = st.form_submit_button("Confirm Booking")

        if submit:
            # Validation checks
            if patient_name.isdigit():
                st.error("Please enter a valid name.")
            elif not contact.strip():
                st.error("Please enter your contact information.")
            elif not contact.isdigit():
                st.error("Contact number must contain numbers only.")
            elif len(contact) != 11:
                st.error("Contact number must be exactly 11 digits.")
            else:
                try:
                    db.execute("""
                        INSERT INTO appointments
                        (patient_name, contact, doctor, appointment_date, appointment_time, reason)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        patient_name.strip(),
                        contact.strip(),
                        doctor,
                        str(appointment_date),
                        appointment_time,
                        reason       
                    ))
                    st.success("Appointment Booked Successfully!")
                except sqlite3.IntegrityError:
                    st.error("This time slot is already booked for this doctor. Please choose a different date, time, or specialist.")

with col_right:
    st.subheader("Clinic Guidelines")
    st.info("""
    * **Arrival:** Please arrive 10 minutes before your scheduled slot.
    * **Contact Info:** Ensure your 11-digit mobile number is correct for SMS updates.
    * **No Rescheduling:** If you were not able to come and meet with our doctor/specialist, our clinic will not reschedule your appointment for the reason that our doctors/specialists are busy healing patients from the battlefield. So if you want, you must book another appointment in order to meet our doctor/specialist.
    """)

# VIEW BOOKED APPOINTMENTS SECTION
st.markdown("---")

appointments = db.fetch_all("""
    SELECT id, patient_name, contact, doctor, appointment_date, appointment_time, reason
    FROM appointments
    ORDER BY appointment_date, appointment_time
""")

if appointments:
    import pandas as pd
    
    df = pd.DataFrame(
        appointments,
        columns=[
            "id",
            "patient_name",
            "contact",
            "doctor",
            "appointment_date",
            "appointment_time",
            "reason",
        ],
    )
    
    st.subheader("All Scheduled Appointments")
    
    filter_col1, filter_col2 = st.columns(2)
    
    with filter_col1:
        doctors = ["ALL DOCTORS/SPECIALIST"] + sorted(df["doctor"].unique())
        selected_doctor = st.selectbox("Filter by Doctor/Specialist", doctors)
    
    with filter_col2:
        search_query = st.text_input(
            "Search Patient Name or Contact", placeholder="Type to search...")
        
    filtered_df = df.copy()
    if selected_doctor != "ALL DOCTORS/ESPECIALIST":
        filtered_df = filtered_df[filtered_df["doctor"] == selected_doctor]
        
    if search_query:
        filtered_df = filtered_df[
            filtered_df["patient_name"].str.contains(search_query, case=False, na=False) |
            filtered_df["contact"]
            .astype(str)
            .str.contains(search_query, case=False, na=False)
        ]            
        
    if not filtered_df.empty:
        st.dataframe(
            filtered_df,
            column_config={
                "id": "ID",
                "patient_name": "Patient Name",
                "contact": "Contact Number",
                "doctor": "Doctor / Specialist",
                "appointment_date": "Appointment Date",
                "appointment_time": "Appointment Time Slot",
                "reason": "Reason for Visit",
            },
            use_container_width=True,
            hide_index=True,
        )     
    else:
        st.info("No matching appointments found.")
else:
    st.info("No appointments booked yet. Be the first to schedule one today!")            
        
