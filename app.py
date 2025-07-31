import streamlit as st
import pandas as pd
import os
from datetime import datetime

# ---------- Optional: Background Image ----------
# To enable background image, uncomment below and add your own image URL or base64
st.sidebar.title("🏢 Apartment Panel")
st.sidebar.image(
    "https://lh3.googleusercontent.com/gps-cs-s/AC9h4nrx719vUkWKcW38hhdm5ZPaBPjaZgOg33QRoFdvKLY4mfN2UkMn4LOJm91vDsR1U83WyzYYIVtpqWX6YeeFLlfAtEi4xwyHBh8L0Wa2R0fEx6byZb83idWgNNZT2ACyrHddvHS0=s1360-w1360-h1020-rw",
    caption="Our Apartment", 
    use_column_width=True

)
st.sidebar.markdown("**📍 Address:**")
st.sidebar.write("Manikonda, Hyderabad")
st.sidebar.markdown(
    "📍 **Address:**  \n"
    "[View Location on Google Maps](https://maps.app.goo.gl/cCAwT2zTzdzNgKub9)"
)
# st.markdown(page_bg_img, unsafe_allow_html=True)

# ---------- Constants ----------
DATA_FILE = 'payments.csv'
floor_flats = {
    "Ground": ["G1", "G2", "G3", "G4", "G5"],
    "1st": ["101", "102", "103", "104", "105"],
    "2nd": ["201", "202", "203", "204", "205"],
    "3rd": ["301", "302", "303", "304", "305"],
    "4th": ["401", "402", "403", "404", "405"],
}

# ---------- Data Handling ----------
def load_data():
    if not os.path.exists(DATA_FILE):
        df = pd.DataFrame(columns=[
            "Apartment", "Name",
            "Maintenance Paid", "Water Paid",
            "Maintenance Date", "Water Date"
        ])
        df.to_csv(DATA_FILE, index=False)
    df = pd.read_csv(DATA_FILE)
    df['Apartment'] = df['Apartment'].astype(str)
    return df

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

# ---------- UI ----------
st.title("🏠 Apartment Bill Payment Tracker")

df = load_data()

if df.empty:
    st.info("No payment records yet. Be the first to update!")

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
        today = datetime.today()
        current_month = today.strftime('%Y-%m')
        today_str = today.strftime('%Y-%m-%d')

        row = df[df['Apartment'].str.upper() == apt_str]

        if row.empty:
            # New entry
            new_entry = {
                "Apartment": apt_str,
                "Name": name,
                "Maintenance Paid": "Yes" if bill_type == "Maintenance" else "No",
                "Water Paid": "Yes" if bill_type == "Water" else "No",
                "Maintenance Date": today_str if bill_type == "Maintenance" else "",
                "Water Date": today_str if bill_type == "Water" else ""
            }
            df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
            st.success(f"✅ Payment recorded for Apartment {apt_str}")
        else:
            index = row.index[0]
            paid_col = "Maintenance Paid" if bill_type == "Maintenance" else "Water Paid"
            date_col = "Maintenance Date" if bill_type == "Maintenance" else "Water Date"

            paid_status = df.at[index, paid_col]
            paid_date_raw = df.at[index, date_col]

            if isinstance(paid_date_raw, str) and paid_status == "Yes":
                try:
                    paid_date = datetime.strptime(paid_date_raw, "%Y-%m-%d")
                    if paid_date.strftime("%Y-%m") == current_month:
                        st.warning(f"⚠️ You have already paid your {bill_type} bill for this month on {paid_date_raw}.")
                        st.stop()
                except:
                    pass  # skip if date is malformed

            # If not paid this month, update
            df.at[index, paid_col] = "Yes"
            df.at[index, date_col] = today_str
            st.success(f"✅ Payment updated for Apartment {apt_str}")


# -------- Admin View Section --------
st.header("📋 View All Payment Records")
st.dataframe(df)

# -------- Filter for Unpaid --------
with st.expander("🔍 Show Unpaid Residents"):
    bill_filter = st.selectbox("Choose Bill Type", ["Maintenance Paid", "Water Paid"])
    unpaid_df = df[df[bill_filter] != "Yes"]
    st.dataframe(unpaid_df)
