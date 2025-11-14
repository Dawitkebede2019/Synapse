# app.py
# app.py
import streamlit as st
import random
import sqlite3
import hashlib # NEW: Library for secure hashing

# --- SECURITY FUNCTIONS ---
# NEW: Function to turn a plain password into a secure hash
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

# NEW: Function to check if a submitted password matches the stored hash
def check_hashes(password, hashed_text):
    if make_hashes(password) == hashed_text:
        return True
    return False

# --- DATABASE SETUP ---
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT UNIQUE,
            password TEXT
        )
    ''')
    conn.commit()
    conn.close()

def add_user(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    try:
        # CHANGED: We now save the HASH, not the plain password
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", 
                  (username.lower(), make_hashes(password)))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def check_user(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    # CHANGED: We select the stored password (which is a hash) for this user
    c.execute("SELECT password FROM users WHERE username = ?", (username.lower(),))
    data = c.fetchone()
    conn.close()
    
    if data:
        # CHANGED: Compare the typed password's hash with the stored hash
        stored_password_hash = data[0]
        if check_hashes(password, stored_password_hash):
            return True
    return False

init_db()

# --- PAGE CONFIG ---
st.set_page_config(page_title="Synapse", page_icon="🚀", layout="wide")

# --- SESSION STATE INITIALIZATION ---
if 'logged_in' not in st.session_state:
    st.session_state.update({
        'logged_in': False, 'username': '', 'page': 'login',
        'uc_balance': 100, 'current_task': None
    })

# --- TASK BANK ---
TASK_BANK = [
    {
        "type": "riddle",
        "question": "I have cities, but no houses. I have mountains, but no trees. I have water, but no fish. What am I?",
        "answer": "a map",
        "reward": 50
    },
    {
        "type": "logic",
        "question": "What number comes next in the sequence? 2, 5, 11, 23, ___",
        "answer": "47",
        "reward": 75
    },
    {
        "type": "creative",
        "question": "Describe the color blue to someone who is blind.",
        "answer": None,
        "reward": 100
    },
    {
        "type": "pattern",
        "question": "Look at the pattern: O, T, T, F, F, S, S, E, ___. What letter comes next?",
        "answer": "n",
        "reward": 125
    }
]

# --- LOGIN/SIGNUP PAGES ---
def login_page():
    st.title("Welcome to Synapse")
    st.subheader("Please log in to continue")
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
        if submitted:
            if check_user(username, password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.rerun()
            else:
                st.error("Invalid username or password")
    if st.button("Don't have an account? Sign Up"):
        st.session_state.page = 'signup'
        st.rerun()

def signup_page():
    st.title("Create a New Account")
    with st.form("signup_form"):
        new_username = st.text_input("Choose a Username")
        new_password = st.text_input("Choose a Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        signup_submitted = st.form_submit_button("Sign Up")
        if signup_submitted:
            if new_username and new_password and confirm_password:
                if new_password == confirm_password:
                    if add_user(new_username, new_password):
                        st.success("Account created successfully! Please log in.")
                        st.session_state.page = 'login'
                        st.rerun()
                    else:
                        st.error("Username already exists. Please choose another one.")
                else:
                    st.error("Passwords do not match.")
            else:
                st.warning("Please fill out all fields.")

# --- MAIN APP PAGES ---
def dashboard():
    st.title(f"Welcome to your Dashboard, {st.session_state.username}!")
    st.write("This is where you'll see an overview of your activity, tasks, and group updates.")
    col1, col2, col3 = st.columns(3)
    col1.metric("Active Tasks", "1", " ")
    col2.metric("Groups Joined", "3", " ")
    col3.metric("Wallet Balance", f"{st.session_state.uc_balance} UC", " ")

def groups():
    st.title("Your Groups")
    st.write("Here you can find groups, join them, or recruit new members.")
    st.header("My Groups")
    st.write("- Project Phoenix")
    st.write("- Marketing Team")
    st.write("- Weekend Hackers")
    if st.button("Recruit New Member"):
        st.success("Recruitment link copied to clipboard!")

def tasks():
    st.title("Complete a Task, Earn UC")
    if not st.session_state.current_task:
        st.session_state.current_task = random.choice(TASK_BANK)
    task = st.session_state.current_task
    st.subheader(f"Your Task (Reward: {task['reward']} UC)")
    st.info(task['question'])
    with st.form("task_form"):
        user_answer = st.text_area("Your Answer")
        submitted = st.form_submit_button("Submit Answer")
        if submitted:
            if user_answer:
                is_correct = False
                if task['type'] == 'creative' or user_answer.strip().lower() == task.get('answer', '').lower():
                    is_correct = True
                if is_correct:
                    reward = task['reward']
                    st.session_state.uc_balance += reward
                    st.success(f"Correct! You've earned {reward} UC. Your new balance is {st.session_state.uc_balance} UC.")
                    st.balloons()
                    st.session_state.current_task = None
                else:
                    st.error("That's not quite right. Try again!")
            else:
                st.warning("Please submit an answer.")

def wallet():
    st.title("Digital Wallet")
    st.write("Manage your digital currency, view transactions, and connect your bank cards.")
    st.header(f"Current Balance: {st.session_state.uc_balance} UC")
    st.button("Send Currency")
    st.button("Receive Currency")

def profile():
    st.title("Your Profile & Verification")
    st.write("Upload your ID and manage your personal information.")
    st.warning("🔒 **Important:** This is a conceptual demo. Do not upload real documents.")
    st.subheader("Verification Status: Not Verified")
    uploaded_id = st.file_uploader("Upload your ID (e.g., Driver's License)")
    if uploaded_id: st.success("ID uploaded successfully! Awaiting verification.")
    st.text_input("Bank Card Number", placeholder="**** **** **** 1234")

# --- MAIN APP LOGIC ---
if not st.session_state.logged_in:
    if st.session_state.page == 'login':
        login_page()
    elif st.session_state.page == 'signup':
        signup_page()
else:
    st.sidebar.title(f"Hello, {st.session_state.username}!")
    st.sidebar.markdown("---")
    page_options = { "Dashboard": dashboard, "Groups": groups, "Tasks": tasks, "Wallet": wallet, "Profile & Verification": profile }
    selection = st.sidebar.radio("Go to", list(page_options.keys()))
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.page = 'login'
        st.rerun()
    page_to_display = page_options[selection]
    page_to_display()