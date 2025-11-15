# app.py
# app.py
import streamlit as st
import random
import sqlite3
import hashlib

# --- SECURITY FUNCTIONS ---
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

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
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username.lower(), make_hashes(password)))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def check_user(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT password FROM users WHERE username = ?", (username.lower(),))
    data = c.fetchone()
    conn.close()
    if data:
        return check_hashes(password, data[0])
    return False

init_db()

# --- PAGE CONFIG ---
st.set_page_config(page_title="Synapse", page_icon="🚀", layout="wide")

# --- SESSION STATE INITIALIZATION ---
if 'logged_in' not in st.session_state:
    st.session_state.update({
        'logged_in': False, 'username': '', 'page': 'login',
        'uc_balance': 1000, 'current_task': None # Start with 1000 UC to make testing the store easier
    })

# --- DATA BANKS ---
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
    }
]
REWARDS_BANK = [
    {
        "name": "1-Month Streaming Service Subscription",
        "cost": 1500,
        "description": "Enjoy a month of ad-free movies and shows on your favorite platform.",
        "reward_type": "Discount Code",
        "reward_content": "STREAM2024-XYZ",
        "image": "https://images.unsplash.com/photo-1574375927938-d5a98e8ffe85?w=500"
    },
    {
        "name": "20% Off at TechGadgets.com",
        "cost": 500,
        "description": "Get a 20% discount on your next purchase of cool gadgets and electronics.",
        "reward_type": "Affiliate Link",
        "reward_content": "https://techgadgets.com/discount/SYNAPSE20",
        "image": "https://images.unsplash.com/photo-1525547719571-a2d4ac8945e2?w=500"
    },
    {
        "name": "$10 Gift Card for 'The Coffee Stop'",
        "cost": 1000,
        "description": "Treat yourself to your favorite coffee or snack at The Coffee Stop.",
        "reward_type": "Gift Card Code",
        "reward_content": "TCS-GIFT-1234-5678",
        "image": "https://images.unsplash.com/photo-1511920183353-8b2c42d5d8a9?w=500"
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
    col1.metric("Active Tasks", "1" if st.session_state.current_task else "0", " ")
    col2.metric("Groups Joined", "3", " ")
    col3.metric("Wallet Balance", f"{st.session_state.uc_balance} UC", " ")

def groups():
    st.title("Your Groups")
    st.write("Here you can find groups, join them, or recruit new members.")
    st.header("My Groups")
    st.write("- Project Phoenix")
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
            if user_answer.strip().lower() == task.get('answer', '').lower():
                reward = task['reward']
                st.session_state.uc_balance += reward
                st.success(f"Correct! You've earned {reward} UC.")
                st.balloons()
                st.session_state.current_task = None
            else:
                st.error("That's not quite right. Try again!")

def store_page():
    st.title("🎁 Rewards Store")
    st.write("Use your earned UC to redeem exclusive rewards and discounts!")
    st.info(f"Your current balance: **{st.session_state.uc_balance} UC**")
    st.markdown("---")

    for i, item in enumerate(REWARDS_BANK):
        col1, col2 = st.columns([1, 2])
        with col1:
            st.image(item["image"], use_column_width=True)
        with col2:
            st.subheader(item["name"])
            st.write(f"**Cost: {item['cost']} UC**")
            st.write(item["description"])
            if st.button(f"Redeem Now", key=f"redeem_{i}"):
                if st.session_state.uc_balance >= item['cost']:
                    st.session_state.uc_balance -= item['cost']
                    st.success(f"Success! You redeemed '{item['name']}'.")
                    st.info(f"Your {item['reward_type']}: **{item['reward_content']}**")
                    st.rerun()
                else:
                    st.error("You do not have enough UC to redeem this item.")
        st.markdown("---")

def wallet():
    st.title("Digital Wallet")
    st.header(f"Current Balance: {st.session_state.uc_balance} UC")
    st.button("Send Currency")
    st.button("Receive Currency")

def profile():
    st.title("Your Profile & Verification")
    st.write("Upload your ID and manage your personal information.")
    st.subheader("Verification Status: Not Verified")
    # ... rest of profile code ...

# --- MAIN APP LOGIC ---
if not st.session_state.logged_in:
    if st.session_state.page == 'login':
        login_page()
    elif st.session_state.page == 'signup':
        signup_page()
else:
    st.sidebar.title(f"Hello, {st.session_state.username}!")
    st.sidebar.markdown("---")
    page_options = {
        "Dashboard": dashboard,
        "Groups": groups,
        "Tasks": tasks,
        "Store": store_page,
        "Wallet": wallet,
        "Profile & Verification": profile
    }
    selection = st.sidebar.radio("Go to", list(page_options.keys()))
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.page = 'login'
        st.rerun()
    page_to_display = page_options[selection]
    page_to_display()