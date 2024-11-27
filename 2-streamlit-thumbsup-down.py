import streamlit as st
import sqlite3

# Initialize SQLite database
conn = sqlite3.connect("feedback.db")
cursor = conn.cursor()

# Create a table to store votes if it doesn't exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS feedback (
    thumbs_up INTEGER DEFAULT 0,
    thumbs_down INTEGER DEFAULT 0,
    neutral INTEGER DEFAULT 0
)
""")
conn.commit()

# Function to initialize votes in the database
def initialize_votes():
    cursor.execute("SELECT * FROM feedback")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO feedback (thumbs_up, thumbs_down, neutral) VALUES (0, 0, 0)")
        conn.commit()

# Function to get current vote counts
def get_votes():
    cursor.execute("SELECT thumbs_up, thumbs_down, neutral FROM feedback")
    return cursor.fetchone()

# Function to update votes
def update_vote(column):
    cursor.execute(f"UPDATE feedback SET {column} = {column} + 1")
    conn.commit()

# Function to reset votes
def reset_votes():
    cursor.execute("UPDATE feedback SET thumbs_up = 0, thumbs_down = 0, neutral = 0")
    conn.commit()
    st.session_state["has_voted"] = False  # Allow voting again for all users

# Initialize votes in the database
initialize_votes()

# App state management
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "has_voted" not in st.session_state:
    st.session_state["has_voted"] = False
if "show_login" not in st.session_state:
    st.session_state["show_login"] = False

# Admin login modal
def admin_login_modal():
    st.write("**Admin Login**")
    username = st.text_input("Username", key="username")
    password = st.text_input("Password", type="password", key="password")
    if st.button("Login"):
        if username == "admin" and password == "admin":
            st.session_state["logged_in"] = True
            st.session_state["show_login"] = False
            st.success("Login successful!")
        else:
            st.error("Invalid username or password.")

# Add a discreet login button in the top-right corner
with st.container():
    col1, col2 = st.columns([9, 1])
    with col2:
        if st.button("🔒"):
            st.session_state["show_login"] = not st.session_state["show_login"]

# Show login modal if toggled
if st.session_state["show_login"]:
    st.write("---")
    admin_login_modal()
    st.write("---")

# Main app
st.title("How are you doing?")

votes = get_votes()  # Get current votes (real-time update for all users)

# Voting section for non-admin users
if not st.session_state["logged_in"]:
    if not st.session_state["has_voted"]:
        st.write("")  # Add empty spacing to center-align the buttons
        st.write("")
        col1, col2, col3 = st.columns([1, 1, 1])

        with col1:
            if st.button("👍", use_container_width=True, key="thumbs_up_button"):
                update_vote("thumbs_up")
                st.session_state["has_voted"] = True
        with col2:
            if st.button("😐", use_container_width=True, key="neutral_button"):
                update_vote("neutral")
                st.session_state["has_voted"] = True
        with col3:
            if st.button("👎", use_container_width=True, key="thumbs_down_button"):
                update_vote("thumbs_down")
                st.session_state["has_voted"] = True
    else:
        st.success("You have already voted. Thank you!")

# Admin dashboard
if st.session_state["logged_in"]:
    st.header("Admin Dashboard")
    st.write("This section is only visible to the admin.")

    # Display feedback summary (real-time)
    votes = get_votes()  # Fetch the latest vote counts
    st.subheader("Feedback Summary")
    st.write(f"👍 Thumbs Up: {votes[0]}")
    st.write(f"👎 Thumbs Down: {votes[1]}")
    st.write(f"😐 Neutral: {votes[2]}")

    # Admin controls
    st.subheader("Admin Controls")
    if st.button("Reset Votes"):
        reset_votes()
        st.success("Votes have been reset. Everyone can vote again!")
