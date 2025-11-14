# app.py
# app.py
import streamlit as st

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Unity Hub",
    page_icon="🚀",
    layout="wide"
)

# --- FAKE DATABASE & USER AUTHENTICATION ---
# In a real app, you would use a database. For this demo, we'll use session state.
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
    st.session_state['username'] = ''
    st.session_state['page'] = 'login'

# A simple dictionary to act as our user database
if 'users' not in st.session_state:
    st.session_state['users'] = {"admin": "password"} # Example user

def login_page():
    """Displays the login page."""
    st.title("Welcome to Unity Hub")
    st.subheader("Please log in to continue")

    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")

        if submitted:
            if username in st.session_state.users and st.session_state.users[username] == password:
                st.session_state['logged_in'] = True
                st.session_state['username'] = username
                st.rerun() # CHANGED: from st.experimental_rerun()
            else:
                st.error("Invalid username or password")
    
    if st.button("Don't have an account? Sign Up"):
        st.session_state['page'] = 'signup'
        st.rerun() # CHANGED: from st.experimental_rerun()

def signup_page():
    """Displays the signup page."""
    st.title("Create a New Account")
    
    with st.form("signup_form"):
        new_username = st.text_input("Choose a Username")
        new_password = st.text_input("Choose a Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        signup_submitted = st.form_submit_button("Sign Up")

        if signup_submitted:
            if new_username and new_password and confirm_password:
                if new_password == confirm_password:
                    if new_username in st.session_state.users:
                        st.error("Username already exists. Please choose another one.")
                    else:
                        st.session_state.users[new_username] = new_password
                        st.success("Account created successfully! Please log in.")
                        st.session_state['page'] = 'login'
                        st.rerun() # CHANGED: from st.experimental_rerun()
                else:
                    st.error("Passwords do not match.")
            else:
                st.warning("Please fill out all fields.")

# --- PAGE DEFINITIONS (These functions remain the same) ---

def dashboard():
    st.title(f"Welcome to your Dashboard, {st.session_state['username']}!")
    st.write("This is where you'll see an overview of your activity, tasks, and group updates.")
    st.info("💡 **Next Step:** We can build this out to show key metrics, notifications, or recent activity.")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Active Tasks", "5", "1")
    col2.metric("Groups Joined", "3", "2")
    col3.metric("Wallet Balance", "1,250 UC", "150")

def groups():
    st.title("Your Groups")
    st.write("Here you can find groups, join them, or recruit new members.")
    st.info("💡 **Next Step:** We can add functionality to create a new group, list existing groups, and manage members.")
    st.header("My Groups")
    st.write("- Project Phoenix")
    st.write("- Marketing Team")
    st.write("- Weekend Hackers")
    if st.button("Recruit New Member"):
        st.success("Recruitment link copied to clipboard!")

def tasks():
    st.title("Task Management")
    st.write("Manage your individual and group tasks here.")
    st.info("💡 **Next Step:** We can build a to-do list where you can add, edit, and check off tasks.")
    task = st.text_input("Add a new task:")
    if st.button("Add Task"):
        if task: st.write(f"Task '{task}' added!")
        else: st.warning("Please enter a task.")
    st.header("Current Tasks")
    st.checkbox("Design the new dashboard UI")
    st.checkbox("Upload final project report")
    st.checkbox("Contact new recruits")

def wallet():
    st.title("Digital Wallet")
    st.write("Manage your digital currency, view transactions, and connect your bank cards.")
    st.warning("🔒 **Important:** This is a conceptual demo. Do not enter real financial information.")
    st.info("💡 **Next Step:** We can design an interface for sending/receiving currency and viewing transaction history.")
    st.subheader("Balance: 1,250 Unity Coin (UC)")
    st.button("Send Currency")
    st.button("Receive Currency")

def profile():
    st.title("Your Profile & Verification")
    st.write("Upload your ID and manage your personal information.")
    st.warning("🔒 **Important:** This is a conceptual demo. Do not upload real documents.")
    st.info("💡 **Next Step:** We can add file uploaders for documents and forms for personal details.")
    st.subheader("Verification Status: Not Verified")
    uploaded_id = st.file_uploader("Upload your ID (e.g., Driver's License)")
    if uploaded_id: st.success("ID uploaded successfully! Awaiting verification.")
    st.text_input("Bank Card Number", placeholder="**** **** **** 1234")


# --- MAIN APP LOGIC ---

if not st.session_state['logged_in']:
    if st.session_state['page'] == 'login':
        login_page()
    elif st.session_state['page'] == 'signup':
        signup_page()
else:
    # --- SIDEBAR NAVIGATION ---
    st.sidebar.title(f"Hello, {st.session_state['username']}!")
    st.sidebar.markdown("---")
    page_options = {
        "Dashboard": dashboard,
        "Groups": groups,
        "Tasks": tasks,
        "Wallet": wallet,
        "Profile & Verification": profile
    }
    selection = st.sidebar.radio("Go to", list(page_options.keys()))
    if st.sidebar.button("Logout"):
        st.session_state['logged_in'] = False
        st.session_state['page'] = 'login'
        st.rerun() # CHANGED: from st.experimental_rerun()
    page_to_display = page_options[selection]
    page_to_display()