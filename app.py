# app.py
# app.py
import streamlit as st
import random # NEW: We need this to pick random tasks

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Synapse",
    page_icon="🚀",
    layout="wide"
)

# --- FAKE DATABASE & USER AUTHENTICATION ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
    st.session_state['username'] = ''
    st.session_state['page'] = 'login'
    st.session_state['uc_balance'] = 100 # NEW: Starting UC balance for a new user
    st.session_state['current_task'] = None # NEW: To hold the user's current task

if 'users' not in st.session_state:
    st.session_state['users'] = {"admin": "password"}

# NEW: A bank of tasks for the app to generate
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
        "answer": None,  # Creative tasks have no single correct answer
        "reward": 100
    },
    {
        "type": "pattern",
        "question": "Look at the pattern: O, T, T, F, F, S, S, E, ___. What letter comes next?",
        "answer": "n", # One, Two, Three, Four, Five, Six, Seven, Eight, Nine
        "reward": 125
    }
]

# --- LOGIN/SIGNUP PAGES (remain the same) ---
def login_page():
    st.title("Welcome to Synapse")
    st.subheader("Please log in to continue")
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
        if submitted:
            if username in st.session_state.users and st.session_state.users[username] == password:
                st.session_state['logged_in'] = True
                st.session_state['username'] = username
                st.rerun()
            else:
                st.error("Invalid username or password")
    if st.button("Don't have an account? Sign Up"):
        st.session_state['page'] = 'signup'
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
                    if new_username in st.session_state.users:
                        st.error("Username already exists.")
                    else:
                        st.session_state.users[new_username] = new_password
                        st.success("Account created successfully! Please log in.")
                        st.session_state['page'] = 'login'
                        st.rerun()
                else:
                    st.error("Passwords do not match.")
            else:
                st.warning("Please fill out all fields.")

# --- MAIN APP PAGES ---

def dashboard():
    st.title(f"Welcome to your Dashboard, {st.session_state['username']}!")
    st.write("This is where you'll see an overview of your activity, tasks, and group updates.")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Active Tasks", "1", " ") # User always has one active task
    col2.metric("Groups Joined", "3", " ")
    # NEW: Display the live UC balance from session state
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

# NEW: The completely rebuilt, interactive Tasks page!
def tasks():
    st.title("Complete a Task, Earn UC")

    # Assign a new task if the user doesn't have one
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
                # For creative tasks, any answer is "correct"
                if task['type'] == 'creative':
                    is_correct = True
                # For other tasks, check the answer (case-insensitive)
                elif user_answer.strip().lower() == task['answer'].lower():
                    is_correct = True

                if is_correct:
                    reward = task['reward']
                    st.session_state.uc_balance += reward
                    st.success(f"Correct! You've earned {reward} UC. Your new balance is {st.session_state.uc_balance} UC.")
                    st.balloons()
                    # Clear the current task so a new one is assigned
                    st.session_state.current_task = None
                else:
                    st.error("That's not quite right. Try again, or get a new task.")
                    # Optional: Add a button to skip the task
                    # if st.button("Get New Task"):
                    #     st.session_state.current_task = None
                    #     st.rerun()
            else:
                st.warning("Please submit an answer.")


def wallet():
    st.title("Digital Wallet")
    st.write("Manage your digital currency, view transactions, and connect your bank cards.")
    # NEW: Display the live UC balance and changed name back to UC
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
if not st.session_state['logged_in']:
    if st.session_state['page'] == 'login':
        login_page()
    elif st.session_state['page'] == 'signup':
        signup_page()
else:
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
        st.rerun()
    page_to_display = page_options[selection]
    page_to_display()