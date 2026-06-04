import streamlit as st
import sqlite3
import bcrypt
import pandas as pd
import os
import datetime
from PIL import Image
from pathlib import Path

# ==================================================
# CONFIG
# ==================================================

st.set_page_config(
    page_title="SafeWalk AI",
    page_icon="🛡️",
    layout="wide"
)

# ==================================================
# FOLDERS
# ==================================================

UPLOAD_FOLDER = "uploads"

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# ==================================================
# DATABASE
# ==================================================

conn = sqlite3.connect(
    "safewalk.db",
    check_same_thread=False
)

cursor = conn.cursor()

# ==================================================
# USERS
# ==================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT,
email TEXT UNIQUE,
phone TEXT,
city TEXT,
password TEXT,
photo TEXT,
created_at TEXT
)
""")

# ==================================================
# FAMILY MEMBERS
# ==================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS family(
id INTEGER PRIMARY KEY AUTOINCREMENT,
user_email TEXT,
member_name TEXT,
relation TEXT,
phone TEXT
)
""")

# ==================================================
# ROUTES
# ==================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS routes(
id INTEGER PRIMARY KEY AUTOINCREMENT,
user_email TEXT,
city TEXT,
source TEXT,
destination TEXT,
travel_time TEXT
)
""")

# ==================================================
# COMPANION REQUESTS
# ==================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS requests(
id INTEGER PRIMARY KEY AUTOINCREMENT,
sender_email TEXT,
receiver_email TEXT,
status TEXT
)
""")

# ==================================================
# MESSAGES
# ==================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS messages(
id INTEGER PRIMARY KEY AUTOINCREMENT,
sender TEXT,
receiver TEXT,
message TEXT,
time TEXT
)
""")

# ==================================================
# SOS ALERTS
# ==================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS sos_alerts(
id INTEGER PRIMARY KEY AUTOINCREMENT,
user_email TEXT,
location TEXT,
image_path TEXT,
alert_time TEXT
)
""")

conn.commit()
# ==================================================
# FAMILY ALERTS
# ==================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS family_alerts(
id INTEGER PRIMARY KEY AUTOINCREMENT,
user_email TEXT,
family_name TEXT,
family_phone TEXT,
alert_time TEXT,
status TEXT
)
""")

conn.commit()

# ==================================================
# ADMIN
# ==================================================

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "12345"

# ==================================================
# SESSION STATE
# ==================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False

if "user_email" not in st.session_state:
    st.session_state.user_email = ""

# ==================================================
# HELPER FUNCTIONS
# ==================================================

def hash_password(password):
    return bcrypt.hashpw(
        password.encode(),
        bcrypt.gensalt()
    )

def verify_password(password, hashed):
    return bcrypt.checkpw(
        password.encode(),
        hashed
    )

def save_image(camera_image, filename):
    path = os.path.join(
        UPLOAD_FOLDER,
        filename
    )

    with open(path, "wb") as f:
        f.write(camera_image.getbuffer())

    return path

# ==================================================
# SIDEBAR
# ==================================================

st.sidebar.title("🛡️ SafeWalk AI")

menu = st.sidebar.selectbox(
    "Navigation",
    [
        "Home",
        "Signup",
        "Login",
        "Admin Login"
    ]
)

# ==================================================
# HOME
# ==================================================

if menu == "Home":

    st.title("🛡️ SafeWalk AI")

    st.markdown("""
    ### Women Safety & Companion Network

    Features:

    ✅ User Registration

    ✅ Companion Finder

    ✅ SOS Emergency Alert

    ✅ Threat Image Capture

    ✅ Family Safety Network

    ✅ In-App Messaging

    ✅ Admin Dashboard
    """)

# ==================================================\n# USER SIGNUP
# ==================================================

elif menu == "Signup":

    st.title("User Signup")

    name = st.text_input("Full Name")

    email = st.text_input("Email")

    phone = st.text_input("Phone")

    city = st.text_input("City")

    password = st.text_input(
        "Password",
        type="password"
    )

    photo = st.camera_input(
        "Capture Profile Photo"
    )

    st.subheader("Family Contact")

    family_name = st.text_input(
        "Family Member Name"
    )

    family_relation = st.text_input(
        "Relationship"
    )

    family_phone = st.text_input(
        "Family Phone"
    )

    if st.button("Register"):

        if (
            name == "" or
            email == "" or
            password == ""
        ):
            st.error("Fill all required fields")

        else:

            image_path = ""

            if photo:

                filename = (
                    email.replace("@", "_")
                    + ".jpg"
                )

                image_path = save_image(
                    photo,
                    filename
                )

            hashed_password = hash_password(
                password
            )

            try:

                cursor.execute("""
                INSERT INTO users(
                name,email,phone,city,
                password,photo,created_at
                )
                VALUES(?,?,?,?,?,?,?)
                """,(
                    name,
                    email,
                    phone,
                    city,
                    hashed_password,
                    image_path,
                    str(datetime.datetime.now())
                ))

                cursor.execute("""
                INSERT INTO family(
                user_email,
                member_name,
                relation,
                phone
                )
                VALUES(?,?,?,?)
                """,(
                    email,
                    family_name,
                    family_relation,
                    family_phone
                ))

                conn.commit()

                st.success(
                    "Registration Successful"
                )

            except:
                st.error(
                    "Email already exists"
                )

# ==================================================
# USER LOGIN
# ==================================================

elif menu == "Login":

    st.title("User Login")

    email = st.text_input(
        "Email"
    )

    password = st.text_input(
        "Password",
        type="password"
    )

    if st.button("Login"):

        cursor.execute("""
        SELECT password
        FROM users
        WHERE email=?
        """,(email,))

        user = cursor.fetchone()

        if user:

            stored_password = user[0]

            if verify_password(
                password,
                stored_password
            ):

                st.session_state.logged_in = True

                st.session_state.user_email = (
                    email
                )

                st.success(
                    "Login Successful"
                )

            else:

                st.error(
                    "Incorrect Password"
                )

        else:

            st.error(
                "User Not Found"
            )

# ==================================================
# ADMIN LOGIN
# ==================================================
# ==================================================
# ADMIN PANEL
# ==================================================

elif menu == "Admin Login":

    st.title("🔐 Admin Login")

    username = st.text_input(
        "Username"
    )

    password = st.text_input(
        "Password",
        type="password"
    )

    if st.button("Admin Login"):

        if (
            username == ADMIN_USERNAME
            and
            password == ADMIN_PASSWORD
        ):

            st.session_state.admin_logged_in = True

            st.success(
                "Admin Login Successful"
            )

        else:

            st.error(
                "Invalid Credentials"
            )

    if st.session_state.admin_logged_in:

        st.sidebar.markdown("---")

        admin_menu = st.sidebar.selectbox(
            "Admin Menu",
            [
                "Admin Dashboard",
                "Users",
                "Routes",
                "Requests",
                "Messages",
                "SOS Alerts",
                "Analytics",
                "Logout Admin"
            ]
        )

        # ==========================================
        # DASHBOARD
        # ==========================================

        if admin_menu == "Admin Dashboard":

            st.title("🛡️ Admin Dashboard")

            col1,col2,col3,col4 = st.columns(4)

            cursor.execute(
                "SELECT COUNT(*) FROM users"
            )
            total_users = cursor.fetchone()[0]

            cursor.execute(
                "SELECT COUNT(*) FROM routes"
            )
            total_routes = cursor.fetchone()[0]

            cursor.execute(
                "SELECT COUNT(*) FROM requests"
            )
            total_requests = cursor.fetchone()[0]

            cursor.execute(
                "SELECT COUNT(*) FROM sos_alerts"
            )
            total_sos = cursor.fetchone()[0]

            col1.metric(
                "Users",
                total_users
            )

            col2.metric(
                "Routes",
                total_routes
            )

            col3.metric(
                "Requests",
                total_requests
            )

            col4.metric(
                "SOS Alerts",
                total_sos
            )

        # ==========================================
        # USERS
        # ==========================================

        elif admin_menu == "Users":

            st.title("👥 Users")

            cursor.execute("""
            SELECT
            id,
            name,
            email,
            phone,
            city,
            created_at

            FROM users
            """)

            users = cursor.fetchall()

            if users:

                df = pd.DataFrame(
                    users,
                    columns=
                        [
                        "ID",
                        "Name",
                        "Email",
                        "Phone",
                        "City",
                        "Created"
                    ]
                )

                st.dataframe(
                    df,
                    use_container_width=True
                )

            st.write("---")

            st.subheader(
                "Delete User"
            )

            delete_email = st.text_input(
                "User Email"
            )

            if st.button(
                "Delete User"
            ):

                cursor.execute("""
                DELETE FROM users
                WHERE email=?
                """,
                (
                    delete_email,
                ))

                conn.commit()

                st.success(
                    "User Deleted"
                )

        # ==========================================
        # ROUTES
        # ==========================================

        elif admin_menu == "Routes":

            st.title("🛣️ User Routes")

            cursor.execute("""
            SELECT
            user_email,
            city,
            source,
            destination,
            travel_time

            FROM routes
            """)

            data = cursor.fetchall()

            if data:

                df = pd.DataFrame(
                    data,
                    columns=
                        [
                        "User",
                        "City",
                        "Source",
                        "Destination",
                        "Time"
                    ]
                )

                st.dataframe(
                    df,
                    use_container_width=True
                )

        # ==========================================
        # REQUESTS
        # ==========================================

        elif admin_menu == "Requests":

            st.title("🤝 Companion Requests")

            cursor.execute("""
            SELECT *
            FROM requests
            """)

            data = cursor.fetchall()

            if data:

                df = pd.DataFrame(
                    data,
                    columns=
                        [
                        "ID",
                        "Sender",
                        "Receiver",
                        "Status"
                    ]
                )

                st.dataframe(
                    df,
                    use_container_width=True
                )

        # ==========================================
        # MESSAGES
        # ==========================================

        elif admin_menu == "Messages":

            st.title("💬 Messages")

            cursor.execute("""
            SELECT
            sender,
            receiver,
            message,
            time

            FROM messages
            ORDER BY id DESC
            """)

            messages = cursor.fetchall()

            if messages:

                df = pd.DataFrame(
                    messages,
                    columns=
                        [
                        "Sender",
                        "Receiver",
                        "Message",
                        "Time"
                    ]
                )

                st.dataframe(
                    df,
                    use_container_width=True
                )

        # ==========================================
        # SOS ALERTS
        # ==========================================

        elif admin_menu == "SOS Alerts":

            st.title("🚨 SOS Alerts")

            cursor.execute("""
            SELECT
            id,
            user_email,
            location,
            image_path,
            alert_time

            FROM sos_alerts
            ORDER BY id DESC
            """)

            alerts = cursor.fetchall()

            if alerts:

                for alert in alerts:

                    st.write("---")

                    st.write(
                        f"User: {alert[1]}"
                    )

                    st.write(
                        f"Location: {alert[2]}"
                    )

                    st.write(
                        f"Time: {alert[4]}"
                    )

                    if alert[3]:

                        try:

                            st.image(
                                alert[3],
                                width=300
                            )

                        except:
                            pass

        # ==========================================
        # ANALYTICS
        # ==========================================

        elif admin_menu == "Analytics":

            st.title("📊 Analytics")

            cursor.execute(
                "SELECT city,COUNT(*) FROM users GROUP BY city"
            )

            city_data = cursor.fetchall()

            if city_data:

                city_df = pd.DataFrame(
                    city_data,
                    columns=
                        [
                        "City",
                        "Users"
                    ]
                )

                st.bar_chart(
                    city_df.set_index(
                        "City"
                    )
                )

            cursor.execute(
                "SELECT status,COUNT(*) FROM requests GROUP BY status"
            )

            req_data = cursor.fetchall()

            if req_data:

                req_df = pd.DataFrame(
                    req_data,
                    columns=
                        [
                        "Status",
                        "Count"
                    ]
                )

                st.bar_chart(
                    req_df.set_index(
                        "Status"
                    )
                )

        # ==========================================
        # ADMIN LOGOUT
        # ==========================================

        elif admin_menu == "Logout Admin":

            st.session_state.admin_logged_in = False

            st.success(
                "Admin Logged Out"
            )

            st.rerun()
          # ==================================================
# USER DASHBOARD
# ==================================================

if st.session_state.logged_in:

    st.sidebar.markdown("---")
    st.sidebar.success(
        f"Logged in as\n{st.session_state.user_email}"
    )

    user_menu = st.sidebar.selectbox(
        "User Menu",
        [
        "Dashboard",
        "Profile",
        "Add Route",
        "Find Companion",
        "Requests",
        "Messages",
        "SOS Center",
        "Emergency History",
        "Family Alerts",
        "Nearby Help",
        "Logout"
    ]
)


    # ==============================================D
    # DASHBOARDD
    # ==============================================D

    if user_menu == "Dashboard":

        st.title("🏠 Dashboard")

        col1, col2, col3 = st.columns(3)

        cursor.execute(
            "SELECT COUNT(*) FROM users"
        )
        total_users = cursor.fetchone()[0]

        cursor.execute(
            "SELECT COUNT(*) FROM routes"
        )
        total_routes = cursor.fetchone()[0]

        cursor.execute(
            "SELECT COUNT(*) FROM requests"
        )
        total_requests = cursor.fetchone()[0]

        with col1:
            st.metric(
                "Users",
                total_users
            )

        with col2:
            st.metric(
                "Routes",
                total_routes
            )

        with col3:
            st.metric(
                "Requests",
                total_requests
            )

        st.info(
            "Use the sidebar to access all features."
        )

    # ==============================================D
    # PROFILED
    # ==============================================D

    elif user_menu == "Profile":

        st.title("👤 My Profile")

        cursor.execute("""
        SELECT *
        FROM users
        WHERE email=?
        """,
        (st.session_state.user_email,)
        )

        user = cursor.fetchone()

        if user:

            st.write("### User Details")

            st.write(
                f"**Name:** {user[1]}"
            )

            st.write(
                f"**Email:** {user[2]}"
            )

            st.write(
                f"**Phone:** {user[3]}"
            )

            st.write(
                f"**City:** {user[4]}"
            )

            if user[6]:

                st.image(
                    user[6],
                    width=250
                )

        st.write("---")

        st.write("### Family Contacts")

        cursor.execute("""
        SELECT member_name,
        relation,
        phone
        FROM family
        WHERE user_email=?
        """,
        (st.session_state.user_email,)
        )

        family_data = cursor.fetchall()

        if family_data:

            df = pd.DataFrame(
                family_data,
                columns=
                    [
                    "Name",
                    "Relation",
                    "Phone"
                ]
            )

            st.dataframe(df)

        else:

            st.warning(
                "No family members added"
            )

    # ==============================================D
    # ADD ROUTED
    # ==============================================D

    elif user_menu == "Add Route":

        st.title("🛣 Add Daily Route")

        city = st.text_input(
            "City"
        )

        source = st.text_input(
            "Source Location"
        )

        destination = st.text_input(
            "Destination"
        )

        travel_time = st.text_input(
            "Travel Time"
        )

        if st.button(
            "Save Route"
        ):

            cursor.execute("""
            INSERT INTO routes(
            user_email,
            city,
            source,
            destination,
            travel_time
            )
            VALUES(?,?,?,?,?)
            """,
            (
                st.session_state.user_email,
                city,
                source,
                destination,
                travel_time
            ))

            conn.commit()

            st.success(
                "Route Saved"
            )

    # ==============================================D
    # FIND COMPANIOND
    # ==============================================D

    elif user_menu == "Find Companion":

        st.title("🤝 Find Companion")

        city_search = st.text_input(
            "City"
        )

        # Removed source_search and destination_search as they were not being used in the SQL query.
        # source_search = st.text_input(
        #     "Source"
        # )

        # destination_search = st.text_input(
        #     "Destination"
        # )

        if "companion_results" not in st.session_state:
            st.session_state.companion_results = []

        if st.button(
            "Search Companion"
        ):

            cursor.execute("""
            SELECT
            routes.user_email,
            users.name,
            routes.source,
            routes.destination,
            routes.travel_time

            FROM routes

            JOIN users
            ON routes.user_email =
            users.email

            WHERE
            routes.city=?
            AND
            routes.user_email != ?
            """,
            (
                city_search,
                st.session_state.user_email
            ))

            st.session_state.companion_results = cursor.fetchall()

        results = st.session_state.companion_results

        if results:

            for row in results:

                email = row[0]
                name = row[1]

                st.write("---")

                st.write(
                    f"### {name}"
                )

                st.write(
                    f"Email: {email}"
                )

                st.write(
                    f"Source: {row[2]}"
                )

                st.write(
                    f"Destination: {row[3]}"
                )

                st.write(
                    f"Time: {row[4]}"
                )

                if st.button(
                    f"Send Request {email}",
                    key=f"req_{email}"
                ):

                    cursor.execute("""
                    INSERT INTO requests(
                    sender_email,
                    receiver_email,
                    status
                    )
                    VALUES(?,?,?)
                    """,
                    (
                        st.session_state.user_email,
                        email,
                        "Pending"
                    ))

                    conn.commit()

                    st.success(
                        "Request Sent Successfully"
                    )

                    st.rerun()

        else:
            st.info("Search for companions")

    # ==============================================D
    # REQUESTSD
    # ==============================================D

    elif user_menu == "Requests":

        st.title("📨 Companion Requests")

        # --- Temporary: Display all requests for debugging ---
        st.subheader("All Requests (for Searching similar)")
        cursor.execute("SELECT * FROM requests")
        all_requests = cursor.fetchall()
        if all_requests:
            df_all = pd.DataFrame(all_requests, columns=["ID", "Sender", "Receiver", "Status"])
            st.dataframe(df_all, use_container_width=True)
        else:
            st.info("No requests found in the database.")
        st.write("---")
        # ---------------------------------------------------

        st.subheader(
            "Incoming Requests"
        )

        cursor.execute("""
        SELECT
        id,
        sender_email,
        status

        FROM requests

        WHERE receiver_email=?
        """,
        (
            st.session_state.user_email,
        ))

        incoming = cursor.fetchall()

        if incoming:

            for req in incoming:

                request_id = req[0]

                sender = req[1]

                status = req[2]

                st.write("---")

                st.write(
                    f"From: {sender}"
                )

                st.write(
                    f"Status: {status}"
                )

                col1, col2 = st.columns(2)

                with col1:

                    if st.button(
                        f"Accept {request_id}", key=f"accept_req_{request_id}"
                    ):

                        cursor.execute("""
                        UPDATE requests
                        SET status='Accepted'
                        WHERE id=?
                        """,
                        (request_id,)
                        )

                        conn.commit()

                        st.success(
                            "Request Accepted"
                        )
                        st.rerun() # Added rerun

                with col2:

                    if st.button(
                        f"Reject {request_id}", key=f"reject_req_{request_id}"
                    ):

                        cursor.execute("""
                        UPDATE requests
                        SET status='Rejected'
                        WHERE id=?
                        """,
                        (request_id,)
                        )

                        conn.commit()

                        st.error(
                            "Request Rejected"
                        )
                        st.rerun() # Added rerun

        else:

            st.info(
                "No incoming requests"
            )

        st.write("---")

        st.subheader(
            "Sent Requests"
        )

        cursor.execute("""
        SELECT
        receiver_email,
        status

        FROM requests

        WHERE sender_email=?
        """,
        (
            st.session_state.user_email,
        ))

        sent = cursor.fetchall()

        if sent:

            df = pd.DataFrame(
                sent,
                columns=
                    [
                    "Receiver",
                    "Status"
                ]
            )

            st.dataframe(df)

        else:

            st.info(
                "No sent requests"
            )

    # ==============================================D
    # LOGOUTD
    # ==============================================D

    elif user_menu == "Logout":

        st.session_state.logged_in = False

        st.session_state.user_email = ""

        st.success(
            "Logged Out"
        )

        st.rerun()

    # ==============================================D
    # MESSAGESD
    # ==============================================D

    elif user_menu == "Messages":
        st.title("💬 SafeWalk Chat")

        partner = st.text_input(
        "Enter User Email"
           )

        st.write("---")

        message = st.text_input(
            "Message"
        )

        if st.button("Send Message"):

            if partner and message:

                cursor.execute("""
                INSERT INTO messages(
                sender,
                receiver,
                message,
                time
                )
                VALUES(?,?,?,?)
                """,
                (
                    st.session_state.user_email,
                    partner,
                    message,
                    str(datetime.datetime.now())
                ))

                conn.commit()

                st.success(
                    "Message Sent"
                )

        st.write("---")

        st.subheader("Inbox")

        cursor.execute("""
        SELECT sender,
        message,
        time

        FROM messages

        WHERE receiver=?

        ORDER BY id DESC
        """,
        (
            st.session_state.user_email,
        ))

        inbox = cursor.fetchall()

        if inbox:

            for msg in inbox:

                st.info(
                    f"""
                    From: {msg[0]}

                    {msg[1]}

                    {msg[2]}
                    """
                )

        else:

            st.warning(
                "No Messages"
            )



    # ==============================================D
    # SOS CENTERD
    # ==============================================D

    elif user_menu == "SOS Center":

        st.title("🚨 Emergency SOS")

        st.error(
            "Use only during emergencies"
        )

        location = st.text_input(
            "Current Location"
        )

        threat_image = st.camera_input(
            "Capture Threat Image"
        )

        if st.button(
            "SEND SOS ALERT"
        ):

            image_path = ""

            if threat_image:

                filename = (
                    "SOS_"
                    +
                    str(
                        int(
                            datetime.datetime.now().timestamp()
                        )
                    )
                    +
                    ".jpg"
                )

                image_path = save_image(
                    threat_image,
                    filename
                )

            cursor.execute("""
            INSERT INTO sos_alerts(
            user_email,
            location,
            image_path,
            alert_time
            )
            VALUES(?,?,?,?)
            """,
            (
                st.session_state.user_email,
                location,
                image_path,
                str(datetime.datetime.now())
            ))

            cursor.execute("""
            SELECT member_name,
            phone
            FROM family

            WHERE user_email=?
            """,
            (
                st.session_state.user_email,
            ))

            family_members = cursor.fetchall()

            for member in family_members:

                cursor.execute("""
                INSERT INTO family_alerts(
                user_email,
                family_name,
                family_phone,
                alert_time,
                status
                )
                VALUES(?,?,?,?,?)D
                """,
                (
                    st.session_state.user_email,
                    member[0],
                    member[1],
                    str(datetime.datetime.now()),
                    "ALERT SENT"
                ))

            conn.commit()

            st.success(
                "Emergency Alert Activated"
            )

            st.warning(
                "Family Members Notified"
            )

    # ==============================================D
    # EMERGENCY HISTORYD
    # ==============================================D

    elif user_menu == "Emergency History":

        st.title("📋 Emergency History")

        cursor.execute("""
        SELECT
        location,
        image_path,
        alert_time

        FROM sos_alerts

        WHERE user_email=?

        ORDER BY id DESC
        """,
        (
            st.session_state.user_email,
        ))

        alerts = cursor.fetchall()

        if alerts:

            for alert in alerts:

                st.write("---")

                st.write(
                    f"Location: {alert[0]}"
                )

                st.write(
                    f"Time: {alert[2]}"
                )

                if alert[1]:

                    try:

                        st.image(
                            alert[1],
                            width=300
                        )

                    except:
                        pass

        else:

            st.info(
                "No Alerts Found"
            )

    # ==============================================D
    # FAMILY ALERT STATUSD
    # ==============================================D

    elif user_menu == "Family Alerts":

        st.title("👨‍👩‍👧 Family Alert Records")

        cursor.execute("""
        SELECT
        family_name,
        family_phone,
        alert_time,
        status

        FROM family_alerts

        WHERE user_email=?

        ORDER BY id DESC
        """,
        (
            st.session_state.user_email,
        ))

        alerts = cursor.fetchall()

        if alerts:

            df = pd.DataFrame(
                alerts,
                columns=
                    [
                    "Family Member",
                    "Phone",
                    "Time",
                    "Status"
                ]
            )

            st.dataframe(df)

        else:

            st.info(
                "No Alerts Found"
            )

    # ==============================================D
    # NEARBY HELPD
    # ==============================================D

    elif user_menu == "Nearby Help":

        st.title("🏥 Nearby Help Centers")

        st.success(
            "Emergency Support Directory"
        )

        help_data = [
            [
                "Police Station",
                "100"
            ],
            [
                "Women Helpline",
                "1091"
            ],
            [
                "Emergency",
                "112"
            ],
            [
                "Ambulance",
                "108"
            ],
            [
                "Child Helpline",
                "1098"
            ]
        ]

        help_df = pd.DataFrame(
            help_data,
            columns=
                [
                "Service",
                "Number"
            ]
        )

        st.dataframe(
            help_df,
            use_container_width=True
        )

        st.info(
            "Future Version: GPS Based Nearby Hospitals, Medical Stores and Police Stations."
        )
