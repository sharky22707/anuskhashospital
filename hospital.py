import streamlit as st
import sqlite3
import random
import string
import pandas as pd
from datetime import datetime


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="FinGuard AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# DATABASE
# ============================================================

DB_NAME = "fraud_detection.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def create_database():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_id TEXT UNIQUE,
            amount REAL,
            location TEXT,
            transaction_type TEXT,
            transaction_time INTEGER,
            international INTEGER,
            new_device INTEGER,
            risk_score INTEGER,
            risk_level TEXT,
            result TEXT,
            reasons TEXT,
            timestamp TEXT
        )
    """)

    conn.commit()
    conn.close()


create_database()


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown("""
<style>

.stApp {
    background:
        radial-gradient(circle at top left, #172554 0%, transparent 30%),
        radial-gradient(circle at top right, #312e81 0%, transparent 25%),
        #020617;
    color: #f8fafc;
}

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

header {
    visibility: hidden;
}


/* Main Header */

.main-title {
    font-size: 44px;
    font-weight: 850;
    text-align: center;
    color: #f8fafc;
    margin-top: 5px;
    margin-bottom: 2px;
}

.subtitle {
    text-align: center;
    color: #94a3b8;
    margin-bottom: 30px;
}


/* Cards */

.card {
    background: rgba(15, 23, 42, 0.82);
    border: 1px solid rgba(148, 163, 184, 0.14);
    border-radius: 18px;
    padding: 22px;
    box-shadow: 0 12px 35px rgba(0,0,0,0.25);
    margin-bottom: 18px;
}

.card-title {
    font-size: 19px;
    font-weight: 750;
    margin-bottom: 15px;
}


/* Metrics */

.metric {
    background: rgba(15,23,42,0.8);
    border: 1px solid rgba(148,163,184,0.12);
    border-radius: 16px;
    padding: 18px;
    text-align: center;
}

.metric-number {
    font-size: 29px;
    font-weight: 800;
}

.metric-label {
    color: #94a3b8;
    font-size: 13px;
    margin-top: 4px;
}


/* Result */

.high {
    background: rgba(127,29,29,0.25);
    border: 1px solid rgba(248,113,113,0.45);
    border-radius: 18px;
    padding: 25px;
    text-align: center;
}

.medium {
    background: rgba(120,53,15,0.25);
    border: 1px solid rgba(251,191,36,0.45);
    border-radius: 18px;
    padding: 25px;
    text-align: center;
}

.low {
    background: rgba(20,83,45,0.25);
    border: 1px solid rgba(74,222,128,0.45);
    border-radius: 18px;
    padding: 25px;
    text-align: center;
}

.score {
    font-size: 48px;
    font-weight: 900;
}


/* Buttons */

.stButton > button {
    border-radius: 10px;
    min-height: 42px;
    font-weight: 700;
}


/* Sidebar */

section[data-testid="stSidebar"] {
    background: #020617;
    border-right: 1px solid rgba(148,163,184,0.12);
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# SETTINGS
# ============================================================

if "high_threshold" not in st.session_state:
    st.session_state.high_threshold = 60

if "medium_threshold" not in st.session_state:
    st.session_state.medium_threshold = 30


# ============================================================
# TRANSACTION ID
# ============================================================

def generate_transaction_id():

    while True:

        transaction_id = (
            "TXN-"
            + ''.join(random.choices(string.ascii_uppercase, k=4))
            + "-"
            + ''.join(random.choices(string.digits, k=6))
        )

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT transaction_id FROM transactions WHERE transaction_id=?",
            (transaction_id,)
        )

        exists = cursor.fetchone()

        conn.close()

        if not exists:
            return transaction_id


# ============================================================
# FRAUD DETECTION ENGINE
# ============================================================

def detect_fraud(
    amount,
    location,
    transaction_type,
    transaction_time,
    international,
    new_device
):

    score = 0
    reasons = []

    # -----------------------------------------
    # Amount
    # -----------------------------------------

    if amount > 100000:

        score += 40
        reasons.append(
            "Very high transaction amount"
        )

    elif amount > 50000:

        score += 25
        reasons.append(
            "High transaction amount"
        )

    elif amount > 25000:

        score += 10
        reasons.append(
            "Moderately high transaction amount"
        )


    # -----------------------------------------
    # Location
    # -----------------------------------------

    if location == "Unknown":

        score += 25
        reasons.append(
            "Unknown transaction location"
        )

    elif location == "International":

        score += 20
        reasons.append(
            "International transaction"
        )


    # -----------------------------------------
    # Time
    # -----------------------------------------

    if transaction_time < 6:

        score += 20
        reasons.append(
            "Transaction during unusual hours"
        )

    elif transaction_time >= 22:

        score += 10
        reasons.append(
            "Late-night transaction"
        )


    # -----------------------------------------
    # Transaction type
    # -----------------------------------------

    if transaction_type == "Online Transfer":

        score += 15
        reasons.append(
            "Online transfer requires additional verification"
        )

    elif transaction_type == "ATM Withdrawal":

        score += 5
        reasons.append(
            "ATM withdrawal detected"
        )


    # -----------------------------------------
    # International flag
    # -----------------------------------------

    if international:

        score += 15
        reasons.append(
            "International transaction flag enabled"
        )


    # -----------------------------------------
    # New device
    # -----------------------------------------

    if new_device:

        score += 20
        reasons.append(
            "Transaction from a new device"
        )


    score = min(score, 100)


    # -----------------------------------------
    # Risk classification
    # -----------------------------------------

    if score >= st.session_state.high_threshold:

        level = "HIGH"
        result = "Fraud Detected"

    elif score >= st.session_state.medium_threshold:

        level = "MEDIUM"
        result = "Suspicious Transaction"

    else:

        level = "LOW"
        result = "Safe Transaction"


    if not reasons:

        reasons.append(
            "No suspicious indicators detected"
        )


    return result, level, score, reasons


# ============================================================
# DATABASE FUNCTIONS
# ============================================================

def save_transaction(
    transaction_id,
    amount,
    location,
    transaction_type,
    transaction_time,
    international,
    new_device,
    score,
    risk_level,
    result,
    reasons
):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO transactions (
            transaction_id,
            amount,
            location,
            transaction_type,
            transaction_time,
            international,
            new_device,
            risk_score,
            risk_level,
            result,
            reasons,
            timestamp
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (

        transaction_id,
        amount,
        location,
        transaction_type,
        transaction_time,
        int(international),
        int(new_device),
        score,
        risk_level,
        result,
        " | ".join(reasons),
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    ))

    conn.commit()
    conn.close()


def get_transactions():

    conn = get_connection()

    df = pd.read_sql_query(
        """
        SELECT *
        FROM transactions
        ORDER BY id DESC
        """,
        conn
    )

    conn.close()

    return df


def delete_transaction(transaction_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM transactions WHERE transaction_id=?",
        (transaction_id,)
    )

    conn.commit()
    conn.close()


def clear_database():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM transactions")

    conn.commit()
    conn.close()


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown("## 🛡️ FinGuard AI")

    st.caption(
        "Financial Fraud Detection Platform"
    )

    st.divider()

    page = st.radio(
        "Navigation",
        [
            "📊 Dashboard",
            "🔍 Analyze Transaction",
            "📜 Transaction History",
            "📈 Analytics",
            "⚙️ Settings"
        ]
    )

    st.divider()

    st.markdown("### Risk Engine")

    st.markdown(
        "🟢 LOW — Normal"
    )

    st.markdown(
        "🟡 MEDIUM — Suspicious"
    )

    st.markdown(
        "🔴 HIGH — Potential Fraud"
    )

    st.divider()

    st.caption(
        "Rule-based fraud detection system"
    )


# ============================================================
# LOAD DATA
# ============================================================

df = get_transactions()


# ============================================================
# DASHBOARD
# ============================================================

if page == "📊 Dashboard":

    st.markdown(
        '<div class="main-title">🛡️ FinGuard AI</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitle">'
        'Financial Fraud Detection & Risk Monitoring Dashboard'
        '</div>',
        unsafe_allow_html=True
    )


    total = len(df)

    high = len(
        df[df["risk_level"] == "HIGH"]
    ) if total else 0

    medium = len(
        df[df["risk_level"] == "MEDIUM"]
    ) if total else 0

    low = len(
        df[df["risk_level"] == "LOW"]
    ) if total else 0


    total_amount = (
        df["amount"].sum()
        if total
        else 0
    )


    # ---------------------------------------------
    # Metrics
    # ---------------------------------------------

    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:

        st.markdown(
            f"""
            <div class="metric">
                <div class="metric-number">{total}</div>
                <div class="metric-label">
                    Total Transactions
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with c2:

        st.markdown(
            f"""
            <div class="metric">
                <div class="metric-number">🟢 {low}</div>
                <div class="metric-label">
                    Safe
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with c3:

        st.markdown(
            f"""
            <div class="metric">
                <div class="metric-number">🟡 {medium}</div>
                <div class="metric-label">
                    Suspicious
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with c4:

        st.markdown(
            f"""
            <div class="metric">
                <div class="metric-number">🔴 {high}</div>
                <div class="metric-label">
                    High Risk
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with c5:

        st.markdown(
            f"""
            <div class="metric">
                <div class="metric-number">
                    ₹{total_amount:,.0f}
                </div>
                <div class="metric-label">
                    Amount Monitored
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )


    st.write("")


    # ---------------------------------------------
    # Dashboard Charts
    # ---------------------------------------------

    left, right = st.columns(2)


    with left:

        st.markdown(
            "### 📊 Risk Distribution"
        )

        if total:

            chart_data = pd.DataFrame({
                "Risk Level": [
                    "LOW",
                    "MEDIUM",
                    "HIGH"
                ],
                "Transactions": [
                    low,
                    medium,
                    high
                ]
            })

            st.bar_chart(
                chart_data.set_index(
                    "Risk Level"
                )
            )

        else:

            st.info(
                "No transactions yet. Analyze a transaction to populate the dashboard."
            )


    with right:

        st.markdown(
            "### 💰 Transaction Amounts"
        )

        if total:

            amount_data = df[
                ["timestamp", "amount"]
            ].copy()

            amount_data["timestamp"] = pd.to_datetime(
                amount_data["timestamp"]
            )

            amount_data = amount_data.set_index(
                "timestamp"
            )

            st.line_chart(
                amount_data["amount"]
            )

        else:

            st.info(
                "Transaction analytics will appear here."
            )


    # ---------------------------------------------
    # Recent transactions
    # ---------------------------------------------

    st.markdown("### 🕒 Recent Transactions")

    if total:

        recent = df.head(8)[
            [
                "transaction_id",
                "amount",
                "location",
                "transaction_type",
                "risk_score",
                "risk_level",
                "timestamp"
            ]
        ]

        st.dataframe(
            recent,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info(
            "No transaction records available."
        )


# ============================================================
# ANALYZE TRANSACTION
# ============================================================

elif page == "🔍 Analyze Transaction":

    st.title("🔍 Analyze Transaction")

    st.caption(
        "Enter transaction information and run the fraud detection engine."
    )


    left, right = st.columns(2)


    with left:

        st.markdown(
            "### 💳 Transaction Details"
        )

        amount = st.number_input(
            "Transaction Amount (₹)",
            min_value=0.0,
            value=5000.0,
            step=500.0
        )

        location = st.selectbox(
            "Transaction Location",
            [
                "India",
                "International",
                "Unknown"
            ]
        )

        transaction_type = st.selectbox(
            "Transaction Type",
            [
                "UPI",
                "ATM Withdrawal",
                "Online Transfer",
                "Card Payment"
            ]
        )


    with right:

        st.markdown(
            "### ⚙️ Additional Information"
        )

        transaction_time = st.slider(
            "Transaction Time",
            0,
            23,
            12
        )

        international = st.checkbox(
            "✈️ International Transaction"
        )

        new_device = st.checkbox(
            "📱 New Device"
        )


    st.write("")


    if st.button(
        "🚀 Analyze Transaction",
        use_container_width=True
    ):

        result, level, score, reasons = detect_fraud(
            amount,
            location,
            transaction_type,
            transaction_time,
            international,
            new_device
        )


        transaction_id = generate_transaction_id()


        save_transaction(
            transaction_id,
            amount,
            location,
            transaction_type,
            transaction_time,
            international,
            new_device,
            score,
            level,
            result,
            reasons
        )


        st.success(
            "Transaction successfully analyzed and stored."
        )


        # Result
        if level == "HIGH":

            st.markdown(
                f"""
                <div class="high">
                    <div class="score">
                        🔴 {score}/100
                    </div>
                    <h2>HIGH RISK</h2>
                    <p>
                        Potential fraudulent activity detected.
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )


        elif level == "MEDIUM":

            st.markdown(
                f"""
                <div class="medium">
                    <div class="score">
                        🟡 {score}/100
                    </div>
                    <h2>MEDIUM RISK</h2>
                    <p>
                        Transaction requires additional verification.
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )


        else:

            st.markdown(
                f"""
                <div class="low">
                    <div class="score">
                        🟢 {score}/100
                    </div>
                    <h2>LOW RISK</h2>
                    <p>
                        No major suspicious activity detected.
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )


        st.progress(
            score / 100
        )


        # Information
        c1, c2, c3 = st.columns(3)

        with c1:

            st.metric(
                "Transaction ID",
                transaction_id
            )

        with c2:

            st.metric(
                "Risk Level",
                level
            )

        with c3:

            st.metric(
                "Amount",
                f"₹{amount:,.0f}"
            )


        st.markdown(
            "### 🧠 Detection Reasons"
        )

        for reason in reasons:

            st.warning(
                f"⚠️ {reason}"
            )


        st.markdown(
            "### 🔐 Recommendation"
        )

        if level == "HIGH":

            st.error(
                "Hold the transaction and perform additional identity verification."
            )

        elif level == "MEDIUM":

            st.warning(
                "Request additional authentication such as OTP or 2FA."
            )

        else:

            st.success(
                "Transaction appears normal and can proceed."
            )


# ============================================================
# TRANSACTION HISTORY
# ============================================================

elif page == "📜 Transaction History":

    st.title("📜 Transaction History")

    df = get_transactions()


    if df.empty:

        st.info(
            "No transactions available."
        )

    else:

        # -----------------------------------------
        # Filters
        # -----------------------------------------

        st.markdown(
            "### 🔎 Filters"
        )

        c1, c2, c3 = st.columns(3)

        with c1:

            search = st.text_input(
                "Search Transaction ID"
            )

        with c2:

            risk_filter = st.selectbox(
                "Risk Level",
                [
                    "All",
                    "LOW",
                    "MEDIUM",
                    "HIGH"
                ]
            )

        with c3:

            type_filter = st.selectbox(
                "Transaction Type",
                [
                    "All"
                ] + sorted(
                    df["transaction_type"].unique().tolist()
                )
            )


        filtered = df.copy()


        if search:

            filtered = filtered[
                filtered["transaction_id"]
                .str.contains(
                    search,
                    case=False,
                    na=False
                )
            ]


        if risk_filter != "All":

            filtered = filtered[
                filtered["risk_level"]
                == risk_filter
            ]


        if type_filter != "All":

            filtered = filtered[
                filtered["transaction_type"]
                == type_filter
            ]


        st.write(
            f"Showing **{len(filtered)}** transactions"
        )


        # -----------------------------------------
        # Download
        # -----------------------------------------

        csv = filtered.to_csv(
            index=False
        ).encode("utf-8")


        st.download_button(
            "📥 Download CSV",
            csv,
            "fraud_transactions.csv",
            "text/csv",
            use_container_width=True
        )


        st.write("")


        # -----------------------------------------
        # Table
        # -----------------------------------------

        display_columns = [
            "transaction_id",
            "amount",
            "location",
            "transaction_type",
            "transaction_time",
            "risk_score",
            "risk_level",
            "timestamp"
        ]


        st.dataframe(
            filtered[display_columns],
            use_container_width=True,
            hide_index=True
        )


        # -----------------------------------------
        # Delete transaction
        # -----------------------------------------

        st.markdown(
            "### 🗑️ Delete Transaction"
        )

        transaction_ids = filtered[
            "transaction_id"
        ].tolist()


        if transaction_ids:

            selected_id = st.selectbox(
                "Select transaction",
                transaction_ids
            )


            if st.button(
                "Delete Selected Transaction"
            ):

                delete_transaction(
                    selected_id
                )

                st.success(
                    "Transaction deleted."
                )

                st.rerun()


# ============================================================
# ANALYTICS
# ============================================================

elif page == "📈 Analytics":

    st.title("📈 Analytics")

    df = get_transactions()


    if df.empty:

        st.info(
            "Analyze some transactions first to generate analytics."
        )

    else:

        # -----------------------------------------
        # Statistics
        # -----------------------------------------

        avg_amount = df["amount"].mean()

        avg_score = df["risk_score"].mean()

        highest_amount = df["amount"].max()

        highest_score = df["risk_score"].max()


        c1, c2, c3, c4 = st.columns(4)


        with c1:

            st.metric(
                "Average Amount",
                f"₹{avg_amount:,.0f}"
            )


        with c2:

            st.metric(
                "Average Risk Score",
                f"{avg_score:.1f}"
            )


        with c3:

            st.metric(
                "Highest Amount",
                f"₹{highest_amount:,.0f}"
            )


        with c4:

            st.metric(
                "Highest Risk Score",
                f"{highest_score}/100"
            )


        st.divider()


        # -----------------------------------------
        # Location Analytics
        # -----------------------------------------

        left, right = st.columns(2)


        with left:

            st.markdown(
                "### 🌍 Transactions by Location"
            )

            location_data = (
                df["location"]
                .value_counts()
            )

            st.bar_chart(
                location_data
            )


        with right:

            st.markdown(
                "### 💳 Transactions by Type"
            )

            type_data = (
                df["transaction_type"]
                .value_counts()
            )

            st.bar_chart(
                type_data
            )


        # -----------------------------------------
        # Risk score distribution
        # -----------------------------------------

        st.markdown(
            "### 🎯 Risk Score Distribution"
        )

        score_data = df[
            ["transaction_id", "risk_score"]
        ].set_index(
            "transaction_id"
        )

        st.bar_chart(
            score_data
        )


        # -----------------------------------------
        # High-risk transactions
        # -----------------------------------------

        st.markdown(
            "### 🔴 High Risk Transactions"
        )

        high_risk = df[
            df["risk_level"] == "HIGH"
        ]


        if high_risk.empty:

            st.success(
                "No high-risk transactions detected."
            )

        else:

            st.dataframe(
                high_risk[
                    [
                        "transaction_id",
                        "amount",
                        "location",
                        "transaction_type",
                        "risk_score",
                        "timestamp"
                    ]
                ],
                use_container_width=True,
                hide_index=True
            )


# ============================================================
# SETTINGS
# ============================================================

elif page == "⚙️ Settings":

    st.title("⚙️ Fraud Detection Settings")

    st.caption(
        "Configure the thresholds used by the risk engine."
    )


    st.markdown(
        "### 🎯 Risk Thresholds"
    )


    medium = st.slider(
        "Medium Risk Threshold",
        1,
        80,
        st.session_state.medium_threshold
    )


    high = st.slider(
        "High Risk Threshold",
        20,
        100,
        st.session_state.high_threshold
    )


    if medium >= high:

        st.error(
            "Medium threshold must be lower than High threshold."
        )

    else:

        if st.button(
            "💾 Save Risk Settings"
        ):

            st.session_state.medium_threshold = medium
            st.session_state.high_threshold = high

            st.success(
                "Risk settings updated successfully."
            )


    st.divider()


    st.markdown(
        "### 📌 Current Configuration"
    )


    c1, c2 = st.columns(2)


    with c1:

        st.metric(
            "Medium Risk Starts At",
            st.session_state.medium_threshold
        )


    with c2:

        st.metric(
            "High Risk Starts At",
            st.session_state.high_threshold
        )


    st.divider()


    st.markdown(
        "### 🗑️ Database Management"
    )


    st.warning(
        "Deleting the database records cannot be undone."
    )


    if st.button(
        "🗑️ Delete ALL Transactions"
    ):

        clear_database()

        st.success(
            "All transaction records have been deleted."
        )

        st.rerun()


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.markdown(
    """
    <div style="
        text-align:center;
        color:#64748b;
        padding:15px;
    ">
        🛡️ <b>FinGuard AI</b>
        <br>
        Rule-Based Financial Fraud Detection System
        <br>
        <small>Educational / Demonstration Project</small>
    </div>
    """,
    unsafe_allow_html=True
)