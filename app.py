# app.py
# app.py
import streamlit as st
import random
import sqlite3
import hashlib

# --- SECURITY & DATABASE FUNCTIONS ---
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    return make_hashes(password) == hashed_text

# CHANGED: Updated the database initialization
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    # Create table if it doesn't exist
    c.execute('CREATE TABLE IF NOT EXISTS users (username TEXT UNIQUE, password TEXT, uc_balance INTEGER)')
    
    # NEW: Check if the uc_balance column exists, and add it if it doesn't.
    # This is a safe way to update the database without deleting it.
    try:
        c.execute('SELECT uc_balance FROM users LIMIT 1')
    except sqlite3.OperationalError:
        c.execute('ALTER TABLE users ADD COLUMN uc_balance INTEGER DEFAULT 1000')

    conn.commit()
    conn.close()

# CHANGED: Add user with a starting balance
def add_user(username, password, starting_balance=1000):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, password, uc_balance) VALUES (?, ?, ?)", 
                  (username.lower(), make_hashes(password), starting_balance))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def check_user(username, password):
    # ... (no change in logic)
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT password FROM users WHERE username = ?", (username.lower(),))
    data = c.fetchone()
    conn.close()
    if data:
        return check_hashes(password, data[0])
    return False

# NEW: Functions to get and update the user's balance from the database
def get_user_balance(username):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT uc_balance FROM users WHERE username = ?", (username.lower(),))
    data = c.fetchone()
    conn.close()
    return data[0] if data else 0

def update_user_balance(username, new_balance):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("UPDATE users SET uc_balance = ? WHERE username = ?", (new_balance, username.lower()))
    conn.commit()
    conn.close()

init_db()

# --- PAGE CONFIG ---
st.set_page_config(page_title="Synapse", page_icon="🚀", layout="wide")

# --- SESSION STATE INITIALIZATION ---
if 'logged_in' not in st.session_state:
    st.session_state.update({'logged_in': False, 'username': '', 'page': 'login', 'current_task': None})

# --- DATA BANKS (No changes) ---
TASK_BANK = [{"type": "riddle", "question": "What has an eye, but cannot see?", "answer": "a needle", "reward": 50}]
REWARDS_BANK = [{"name": "20% Off at TechGadgets.com", "cost": 500, "description": "A discount on cool gadgets.", "reward_type": "Affiliate Link", "reward_content": "https://techgadgets.com/discount/SYNAPSE20", "image": "https://images.unsplash.com/photo-1525547719571-a2d4ac8945e2?w=500"}]
MARKET_ITEMS = [{"name": "Synapse Official T-Shirt", "cost": 2000, "description": "High-quality cotton t-shirt.", "image": "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=500", "affiliate_link": "#"}]

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
        # ... full signup code ...
        pass # Placeholder

# --- MAIN APP PAGES ---
def dashboard():
    st.title(f"Welcome to your Dashboard, {st.session_state.username}!")
    # CHANGED: Get balance from database
    current_balance = get_user_balance(st.session_state.username)
    col1, col2, col3 = st.columns(3)
    col1.metric("Active Tasks", "1" if st.session_state.current_task else "0")
    col2.metric("Groups Joined", "3")
    col3.metric("Wallet Balance", f"{current_balance} UC")

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
                # CHANGED: Get and update balance from database
                current_balance = get_user_balance(st.session_state.username)
                new_balance = current_balance + reward
                update_user_balance(st.session_state.username, new_balance)
                st.success(f"Correct! You've earned {reward} UC.")
                st.balloons()
                st.session_state.current_task = None
            else:
                st.error("That's not quite right. Try again!")

def market_page():
    st.title("🛒 The Market")
    # CHANGED: Get balance from database
    current_balance = get_user_balance(st.session_state.username)
    st.info(f"Your current balance: **{current_balance} UC**")
    st.markdown("---")
    for i, item in enumerate(MARKET_ITEMS):
        col1, col2 = st.columns([1, 2])
        with col1:
            # FIXED: from use_container_width=True to width='stretch'
            st.image(item["image"], width='stretch')
        with col2:
            st.subheader(item["name"])
            st.write(f"**Cost: {item['cost']} UC**")
            if st.button(f"Buy Now", key=f"buy_{i}"):
                if current_balance >= item['cost']:
                    # CHANGED: Update balance in database
                    new_balance = current_balance - item['cost']
                    update_user_balance(st.session_state.username, new_balance)
                    st.success(f"Purchase successful! Your order for '{item['name']}' has been placed.")
                    st.rerun()
                else:
                    st.error("You do not have enough UC.")
        st.markdown("---")

def rewards_hub_page():
    st.title("🎁 Rewards Hub")
    # CHANGED: Get balance from database
    current_balance = get_user_balance(st.session_state.username)
    st.info(f"Your current balance: **{current_balance} UC**")
    st.markdown("---")
    for i, item in enumerate(REWARDS_BANK):
        col1, col2 = st.columns([1, 2])
        with col1:
            # FIXED: from use_container_width=True to width='stretch'
            st.image(item["image"], width='stretch')
        with col2:
            st.subheader(item["name"])
            st.write(f"**Cost: {item['cost']} UC**")
            if st.button(f"Redeem Now", key=f"redeem_{i}"):
                if current_balance >= item['cost']:
                    # CHANGED: Update balance in database
                    new_balance = current_balance - item['cost']
                    update_user_balance(st.session_state.username, new_balance)
                    st.success(f"Success! You redeemed '{item['name']}'.")
                    st.info(f"Your {item['reward_type']}: **{item['reward_content']}**")
                    st.rerun()
                else:
                    st.error("You do not have enough UC.")
        st.markdown("---")

def wallet():
    st.title("Digital Wallet")
    # CHANGED: Get balance from database
    current_balance = get_user_balance(st.session_state.username)
    st.header(f"Current Balance: {current_balance} UC")
    st.button("Send Currency")
    st.button("Receive Currency")

def profile():
    # ... profile code ...
    pass # Placeholder

# --- MAIN APP LOGIC ---
if not st.session_state.logged_in:
    # ... login/signup logic ...
    pass # Placeholder
else:
    st.sidebar.title(f"Hello, {st.session_state.username}!")
    st.sidebar.markdown("---")
    page_options = { "Dashboard": dashboard, "Tasks": tasks, "Market": market_page, "Rewards Hub": rewards_hub_page, "Wallet": wallet, "Profile & Verification": profile }
    selection = st.sidebar.radio("Go to", list(page_options.keys()))
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()
    page_to_display = page_options[selection]
    page_to_display()