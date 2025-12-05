# app.py
import streamlit as st
import random
import sqlite3
import hashlib
import time # NEW: To help with the live market feel

# --- All SECURITY & DATABASE FUNCTIONS remain the same ---
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()
def check_hashes(password, hashed_text):
    return make_hashes(password) == hashed_text
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS users (username TEXT UNIQUE, password TEXT, uc_balance INTEGER)')
    try:
        c.execute('SELECT uc_balance FROM users LIMIT 1')
    except sqlite3.OperationalError:
        c.execute('ALTER TABLE users ADD COLUMN uc_balance INTEGER DEFAULT 1000')
    conn.commit()
    conn.close()
def add_user(username, password, starting_balance=1000):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, password, uc_balance) VALUES (?, ?, ?)", (username.lower(), make_hashes(password), starting_balance))
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

# --- SESSION STATE & DATA BANKS ---
if 'logged_in' not in st.session_state:
    st.session_state.update({'logged_in': False, 'username': '', 'page': 'login', 'current_task': None})

# NEW: Initialize our Forex market and user trades if they don't exist
if 'market_prices' not in st.session_state:
    st.session_state.market_prices = {
        'EUR/USD': 1.0750,
        'USD/JPY': 157.25,
        'GBP/USD': 1.2530
    }
if 'user_trades' not in st.session_state:
    st.session_state.user_trades = []

TASK_BANK = [{"type": "riddle", "question": "What has an eye, but cannot see?", "answer": "a needle", "reward": 50}]
REWARDS_BANK = [{"name": "20% Off at TechGadgets.com", "cost": 500, "description": "A discount on cool gadgets.", "reward_type": "Affiliate Link", "reward_content": "https://techgadgets.com/discount/SYNAPSE20", "image": "https://images.unsplash.com/photo-15255477195T71-a2d4ac8945e2?w=500"}]
MARKET_ITEMS = [{"name": "Synapse Official T-Shirt", "cost": 2000, "description": "High-quality cotton t-shirt.", "image": "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=500", "affiliate_link": "#"}]

# --- LOGIN/SIGNUP PAGES (No changes) ---
def login_page():
    st.title("Welcome to Synapse")
    st.subheader("Please log in to continue")
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
        if submitted and check_user(username, password):
            st.session_state.logged_in = True
            st.session_state.username = username
            st.rerun()
        elif submitted:
            st.error("Invalid username or password")
    if st.button("Don't have an account? Sign Up"):
        st.session_state.page = 'signup'
        st.rerun()

def signup_page():
    st.title("Create a New Account")
    # ... full signup code ...

# --- MAIN APP PAGES ---
def dashboard():
    st.title(f"Welcome to your Dashboard, {st.session_state.username}!")
    # ... full dashboard code ...

def tasks():
    st.title("Complete a Task, Earn UC")
    # ... full tasks code ...

# NEW: The Forex Trading Desk Page
def trading_desk_page():
    st.title("📈 Forex Trading Desk")
    st.write("Practice your trading skills in our risk-free simulator. All trades use your UC balance.")

    # Simulate market movement
    for pair in st.session_state.market_prices:
        change = random.uniform(-0.0005, 0.0005) if "JPY" not in pair else random.uniform(-0.05, 0.05)
        st.session_state.market_prices[pair] += change

    current_balance = get_user_balance(st.session_state.username)
    st.info(f"Your trading balance: **{current_balance} UC**")
    st.markdown("---")
    
    st.subheader("Live Market Prices")
    col1, col2, col3 = st.columns(3)
    cols = [col1, col2, col3]
    for i, (pair, price) in enumerate(st.session_state.market_prices.items()):
        cols[i].metric(label=pair, value=f"{price:.4f}")

    st.markdown("---")
    st.subheader("Place a Trade")
    
    col_trade1, col_trade2, col_trade3 = st.columns(3)
    with col_trade1:
        pair_to_trade = st.selectbox("Select Pair", options=list(st.session_state.market_prices.keys()))
    with col_trade2:
        trade_amount = st.number_input("Amount (in UC)", min_value=100, step=50)
    with col_trade3:
        st.write("​") # For alignment
        if st.button("Buy (Long)"):
            if current_balance >= trade_amount:
                # Deduct from balance and open trade
                new_balance = current_balance - trade_amount
                update_user_balance(st.session_state.username, new_balance)
                trade = {
                    "id": len(st.session_state.user_trades) + 1,
                    "pair": pair_to_trade,
                    "amount_uc": trade_amount,
                    "entry_price": st.session_state.market_prices[pair_to_trade]
                }
                st.session_state.user_trades.append(trade)
                st.success(f"Opened BUY trade for {trade_amount} UC on {pair_to_trade}")
                st.rerun()
            else:
                st.error("Not enough UC to open trade.")

    st.markdown("---")
    st.subheader("Your Open Positions")

    if not st.session_state.user_trades:
        st.write("You have no open trades.")
    else:
        for trade in st.session_state.user_trades:
            current_price = st.session_state.market_prices[trade['pair']]
            entry_price = trade['entry_price']
            pnl = (current_price - entry_price) / entry_price * trade['amount_uc']
            
            pnl_color = "green" if pnl >= 0 else "red"
            st.markdown(
                f"**Trade #{trade['id']}:** {trade['pair']} | **Invested:** {trade['amount_uc']} UC | **Entry Price:** {entry_price:.4f} | **Current P/L:** <span style='color:{pnl_color};'>{pnl:+.2f} UC</span>",
                unsafe_allow_html=True
            )
            if st.button(f"Close Trade #{trade['id']}", key=f"close_{trade['id']}"):
                # Calculate final P/L and return funds to user
                final_payout = trade['amount_uc'] + pnl
                current_balance = get_user_balance(st.session_state.username)
                new_balance = current_balance + final_payout
                update_user_balance(st.session_state.username, new_balance)

                # Remove the trade
                st.session_state.user_trades = [t for t in st.session_state.user_trades if t['id'] != trade['id']]
                st.success(f"Trade closed. {final_payout:.2f} UC returned to your balance.")
                st.rerun()

    # Add a small delay and rerun to create the "live" effect
    time.sleep(1)
    st.rerun()

def market_page():
    st.title("🛒 The Market")
    # ... full market code ...

def rewards_hub_page():
    st.title("🎁 Rewards Hub")
    # ... full rewards hub code ...

def wallet():
    st.title("Digital Wallet")
    # ... full wallet code ...

def profile():
    st.title("Your Profile & Verification")
    # ... full profile code ...

# --- MAIN APP LOGIC ---
if not st.session_state.logged_in:
    if st.session_state.page == 'login':
        login_page()
    elif st.session_state.page == 'signup':
        signup_page() # Make sure to paste your full signup_page function here
else:
    st.sidebar.title(f"Hello, {st.session_state.username}!")
    st.sidebar.markdown("---")
    # ADDED Trading Desk to the options
    page_options = { 
        "Dashboard": dashboard, 
        "Tasks": tasks, 
        "Trading Desk": trading_desk_page, # NEW
        "Market": market_page, 
        "Rewards Hub": rewards_hub_page, 
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