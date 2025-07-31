import streamlit as st
import pandas as pd
import os
from datetime import datetime

# File path
DATA_FILE = 'payments.csv'

# Load or create dataset
def load_data():
    if not os.path.exists(DATA_FILE):
        df = pd.DataFrame(columns=[
            "Apartment", "Name", 
            "Maintenance Paid", "Water Paid", 
            "Maintenance Date", "Water Date"
        ])
        df.to_csv(DATA_FILE, index=False)
    df = pd.read_csv(DATA_FILE)
    df['Apartment'] = df['Apartment'].astype(str)  # Force Apartment as string
    return df

# Save updates to file
def save_data(df):
    df.to_csv(DATA_FILE, index=False)

# App title
st.title("🏠 Apartment Bill Payment Tracker")

# Load data
df = load_data()

# Show message if empty
if df.empty:
    st.info("No payment records yet. Be the first to update!")

# Floor to apartment mapping
floor_flats = {
    "Ground": ["G1", "G2", "G3", "G4", "G5"],
    "1st": ["101", "102", "103", "104", "105"],
    "2nd": ["201", "202", "203", "204", "205"],
    "3rd": ["301", "302", "303", "304", "305"],
    "4th": ["401", "402", "403", "404", "405"],
}

# -------- Update Section --------
st.header("✅ Update Your Payment Status")

floor = st.selectbox("Select Floor", list(floor_flats.keys()))
apt = st.selectbox("Select Apartment", floor_flats[floor])

name = st.text_input("Enter your Name")
bill_type = st.radio("Which bill did you pay?", ["Maintenance", "Water"])

if st.button("Mark as Paid"):
    if not name:
        st.warning("Please enter your name.")
    else:
        apt_str = apt.strip().upper()
        name = name.strip()
        today = datetime.today().strftime('%Y-%m-%d')

        row = df[df['Apartment'].str.upper() == apt_str]

        if row.empty:
            new_entry = {
                "Apartment": apt_str,
                "Name": name,
                "Maintenance Paid": "Yes" if bill_type == "Maintenance" else "No",
                "Water Paid": "Yes" if bill_type == "Water" else "No",
                "Maintenance Date": today if bill_type == "Maintenance" else "",
                "Water Date": today if bill_type == "Water" else ""
            }
            df = df.append(new_entry, ignore_index=True)
            st.success(f"✅ Payment recorded for Apartment {apt_str}")
        else:
            index = row.index[0]
            if bill_type == "Maintenance":
                df.at[index, "Maintenance Paid"] = "Yes"
                df.at[index, "Maintenance Date"] = today
            else:
                df.at[index, "Water Paid"] = "Yes"
                df.at[index, "Water Date"] = today
            st.success(f"✅ Payment updated for Apartment {apt_str}")

        save_data(df)
        st.rerun()

# -------- Admin View Section --------
st.header("📋 View All Payment Records")
st.dataframe(df)

# -------- Unpaid Filter Section --------
with st.expander("🔍 Show Unpaid Residents"):
    bill_filter = st.selectbox("Choose Bill Type", ["Maintenance Paid", "Water Paid"])
    unpaid_df = df[df[bill_filter] != "Yes"]
    st.dataframe(unpaid_df)
