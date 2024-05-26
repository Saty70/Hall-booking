import sqlite3
from datetime import datetime
import streamlit as st
from tabulate import tabulate

VALID_HALLS = ['Saraswati', 'Ganga', 'Yamuna', 'Kaveri']

def create_database():
    conn = sqlite3.connect('hall_booking.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hall_name TEXT NOT NULL,
            date TEXT NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def book_hall(hall_name, date, start_time, end_time):
    if hall_name not in VALID_HALLS:
        return f"Invalid hall name. Choose from {', '.join(VALID_HALLS)}."
    
    if not validate_datetime(date, start_time, end_time):
        return "Invalid date or time. Please provide a future date and time in the format YYYY-MM-DD, HH:MM."

    conn = sqlite3.connect('hall_booking.db')
    cursor = conn.cursor()
    
    date_str = date.strftime('%Y-%m-%d')
    start_time_str = start_time.strftime('%H:%M')
    end_time_str = end_time.strftime('%H:%M')
    
    # Check for overlapping bookings
    cursor.execute('''
        SELECT * FROM bookings WHERE hall_name=? AND date=? AND 
        (start_time < ? AND end_time > ?)
    ''', (hall_name, date_str, end_time_str, start_time_str))
    
    if cursor.fetchone():
        conn.close()
        return "Time slot not available."
    
    # Insert new booking
    created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute('''
        INSERT INTO bookings (hall_name, date, start_time, end_time, created_at)
        VALUES (?, ?, ?, ?, ?)
    ''', (hall_name, date_str, start_time_str, end_time_str, created_at))
    
    conn.commit()
    conn.close()
    return "Booking successful."

def cancel_booking(hall_name, date, start_time, end_time):
    conn = sqlite3.connect('hall_booking.db')
    cursor = conn.cursor()
    
    date_str = date.strftime('%Y-%m-%d')
    start_time_str = start_time.strftime('%H:%M')
    end_time_str = end_time.strftime('%H:%M')
    
    cursor.execute('''
        DELETE FROM bookings WHERE hall_name=? AND date=? AND start_time=? AND end_time=?
    ''', (hall_name, date_str, start_time_str, end_time_str))
    
    if cursor.rowcount == 0:
        conn.close()
        return "No booking found to cancel."
    
    conn.commit()
    conn.close()
    return "Booking cancelled."

def update_booking(old_hall_name, old_date, old_start_time, old_end_time, new_hall_name, new_date, new_start_time, new_end_time):
    cancel_result = cancel_booking(old_hall_name, old_date, old_start_time, old_end_time)
    if cancel_result == "Booking cancelled.":
        return book_hall(new_hall_name, new_date, new_start_time, new_end_time)
    else:
        return "Update failed: " + cancel_result

def check_availability(hall_name, date, start_time, end_time):
    if hall_name not in VALID_HALLS:
        return f"Invalid hall name. Choose from {', '.join(VALID_HALLS)}."

    if not validate_datetime(date, start_time, end_time):
        return "Invalid date or time. Please provide a future date and time in the format YYYY-MM-DD, HH:MM."

    conn = sqlite3.connect('hall_booking.db')
    cursor = conn.cursor()
    
    date_str = date.strftime('%Y-%m-%d')
    start_time_str = start_time.strftime('%H:%M')
    end_time_str = end_time.strftime('%H:%M')
    
    cursor.execute('''
        SELECT * FROM bookings WHERE hall_name=? AND date=? AND 
        (start_time < ? AND end_time > ?)
    ''', (hall_name, date_str, end_time_str, start_time_str))
    
    if cursor.fetchone():
        conn.close()
        return "Hall is not available."
    
    conn.close()
    return "Hall is available."

def display_bookings():
    conn = sqlite3.connect('hall_booking.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM bookings')
    bookings = cursor.fetchall()
    
    conn.close()
    
    if not bookings:
        return "No bookings found."
    
    headers = ["ID", "Hall Name", "Date", "Start Time", "End Time", "Created At"]
    table = tabulate(bookings, headers, tablefmt="pretty")
    return table

def validate_datetime(date, start_time, end_time):
    try:
        now = datetime.now()
        start_datetime = datetime.combine(date, start_time)
        end_datetime = datetime.combine(date, end_time)

        if start_datetime <= now:
            st.error(f"Start time {start_datetime} is not in the future.")
            return False
        if end_datetime <= start_datetime:
            st.error(f"End time {end_datetime} is not after start time {start_datetime}.")
            return False

        return True
    except ValueError:
        st.error("Incorrect date or time format.")
        return False

create_database()

st.title("Hall Booking System")

menu = ["Book a Hall", "Cancel a Booking", "Update a Booking", "Check Availability", "Display All Bookings"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Book a Hall":
    st.subheader("Book a Hall")
    hall_name = st.selectbox("Select Hall", VALID_HALLS)
    date = st.date_input("Select Date", min_value=datetime.today().date())
    start_time = st.time_input("Start Time")
    end_time = st.time_input("End Time")
    if st.button("Book"):
        result = book_hall(hall_name, date, start_time, end_time)
        st.success(result)

elif choice == "Cancel a Booking":
    st.subheader("Cancel a Booking")
    hall_name = st.selectbox("Select Hall", VALID_HALLS)
    date = st.date_input("Select Date")
    start_time = st.time_input("Start Time")
    end_time = st.time_input("End Time")
    if st.button("Cancel"):
        result = cancel_booking(hall_name, date, start_time, end_time)
        st.success(result)

elif choice == "Update a Booking":
    st.subheader("Update a Booking")
    st.write("Enter old booking details")
    old_hall_name = st.selectbox("Select Old Hall", VALID_HALLS, key='old_hall')
    old_date = st.date_input("Select Old Date", key='old_date')
    old_start_time = st.time_input("Old Start Time", key='old_start_time')
    old_end_time = st.time_input("Old End Time", key='old_end_time')
    
    st.write("Enter new booking details")
    new_hall_name = st.selectbox("Select New Hall", VALID_HALLS, key='new_hall')
    new_date = st.date_input("Select New Date", key='new_date')
    new_start_time = st.time_input("New Start Time", key='new_start_time')
    new_end_time = st.time_input("New End Time", key='new_end_time')
    
    if st.button("Update"):
        result = update_booking(old_hall_name, old_date, old_start_time, old_end_time, new_hall_name, new_date, new_start_time, new_end_time)
        st.success(result)

elif choice == "Check Availability":
    st.subheader("Check Availability")
    hall_name = st.selectbox("Select Hall", VALID_HALLS)
    date = st.date_input("Select Date")
    start_time = st.time_input("Start Time")
    end_time = st.time_input("End Time")
    if st.button("Check"):
        result = check_availability(hall_name, date, start_time, end_time)
        st.success(result)

elif choice == "Display All Bookings":
    st.subheader("All Bookings")
    bookings = display_bookings()
    st.text(bookings)
