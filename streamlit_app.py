from sqlite.db_creator import insert_csv_to_sqlite
import sqlite3
import pandas as pd
import streamlit as st
import os

DB_PATH = "transjakarta.db"
TABLE_NAME = "transjakarta"
CSV_PATH = "/Users/raihanwibowo/Documents/maira/kuliah/TRIALGUI1/TransJakarta_cleaned - fix.csv"

# ==========================
# Load and Prepare Data
# ==========================
if not os.path.exists(DB_PATH):
    insert_csv_to_sqlite(CSV_PATH)

# Load data from DB
conn = sqlite3.connect(DB_PATH)
print(f"successfully connect to the database {TABLE_NAME}")

df = pd.read_sql_query(f"SELECT * FROM {TABLE_NAME}", conn)
df = df.dropna(subset=['payUserID'])
df['payUserID'] = df['payUserID'].apply(lambda x: str(int(float(x)))).str.strip()
users_df = df[['payUserID', 'typeCard', 'userName', 'userSex', 'userBirthYear']].drop_duplicates()

# Streamlit UI
st.title("🚍 TransJakarta Travel Tracker")

if 'page' not in st.session_state:
    st.session_state.page = 'login'

if 'user_id' not in st.session_state:
    st.session_state.user_id = None

# Login Page
if st.session_state.page == 'login':
    st.header("🔐 Login Pengguna")
    user_input = st.text_input("Masukkan PayUserID")
    login = st.button("Login")
    register = st.button("Register")

    if login:
        if user_input in users_df['payUserID'].values:
            st.session_state.user_id = user_input
            st.session_state.page = 'main_menu'
        else:
            st.warning("PayUserID tidak ditemukan. Silakan registrasi.")

    if register:
        st.session_state.page = 'register'

# Register Page
elif st.session_state.page == 'register':
    st.header("📝 Registrasi Pengguna Baru")
    new_id = st.text_input("PayUserID")
    type_card = st.selectbox("Jenis Kartu", sorted(df['typeCard'].dropna().unique()))
    name = st.text_input("Nama")
    sex = st.selectbox("Jenis Kelamin", ["Laki-laki", "Perempuan"])
    birth_year = st.number_input("Tahun Lahir", min_value=1900, max_value=2025, value=2000)
    daftar = st.button("Daftar")
    kembali = st.button("Kembali")

    if daftar:
        if not (new_id.isdigit() and len(new_id) == 12):
            st.warning("PayUserID harus terdiri dari 12 digit angka.")
        elif new_id in users_df['payUserID'].values:
            st.warning("PayUserID sudah terdaftar.")
        else:
            conn.execute(f"INSERT INTO {TABLE_NAME} (payUserID, typeCard, userName, userSex, userBirthYear) VALUES (?, ?, ?, ?, ?)",
                         (new_id, type_card, name, sex, birth_year))
            conn.commit()
            st.success("Registrasi berhasil!")
            st.session_state.page = 'login'

    if kembali:
        st.session_state.page = 'login'

# Main Menu
elif st.session_state.page == 'main_menu':
    user = users_df[users_df['payUserID'] == st.session_state.user_id].iloc[0]
    st.success(f"👋 Selamat datang, {user['userName']}!")
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Cek Riwayat"):
            st.session_state.page = 'history'
    with col2:
        if st.button("Cari Kode Koridor"):
            st.session_state.page = 'corridor'
    with col3:
        if st.button("Logout"):
            st.session_state.page = 'login'
            st.session_state.user_id = None

# History Page
elif st.session_state.page == 'history':
    st.header("📜 Riwayat Perjalanan")
    user = users_df[users_df['payUserID'] == st.session_state.user_id].iloc[0]
    user_data = pd.read_sql_query("SELECT transID, routeID, transDate, tapInTime, tapOutTime, duration, direction FROM transjakarta WHERE payUserID = ?", conn, params=(st.session_state.user_id,))

    st.info(
    f"""
    **Nama:** {user['userName']}  
    **Tipe Kartu:** {user['typeCard']}  
    **Jenis Kelamin:** {user['userSex']}  
    **Tahun Lahir:** {user['userBirthYear']}
    """
)

    if user_data.empty:
        st.info("Tidak ada riwayat perjalanan.")
    else:
        st.dataframe(user_data)

    if st.button("Kembali"):
        st.session_state.page = 'main_menu'

# Corridor Page
elif st.session_state.page == 'corridor':
    st.header("🛣️ Cari Kode Koridor")
    selected = st.selectbox("Pilih Rute", sorted(df['routeName'].dropna().unique()))
    if st.button("Cari"):
        matched = df[df['routeName'] == selected]
        if not matched.empty:
            st.success(f"✅ Kode Koridor: {matched.iloc[0]['corridorID']}")
        else:
            st.warning("Kode rute tidak ditemukan.")

    if st.button("Kembali"):
        st.session_state.page = 'main_menu'
