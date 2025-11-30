import streamlit as st

st.title("Meeting Scheduler Agent")
st.write("Welcome to the Meeting Scheduler Agent Streamlit App!")

# Example: Display a list of meetings (replace with real data fetching)
meetings = [
    {"title": "Team Sync", "time": "10:00 AM"},
    {"title": "Client Call", "time": "2:00 PM"},
]

st.header("Upcoming Meetings")
for meeting in meetings:
    st.subheader(meeting["title"])
    st.write(f"Time: {meeting['time']}")

# You can add more features, like scheduling a meeting, user login, etc.
