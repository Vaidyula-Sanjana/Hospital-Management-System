import streamlit as st
from database import create_tables
import sqlite3
import pandas as pd
from datetime import datetime

# ------------------ LOGIN SECTION ------------------ #
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None
    st.session_state.user = None

# ------------------ LOGOUT FUNCTION ------------------ #
def logout():
    st.session_state.logged_in = False
    st.session_state.role = None
    st.session_state.user = None
    st.success("Logged out successfully.")

# ------------------ SHOW LOGGED IN DASHBOARD ------------------ #
if st.session_state.logged_in:
    # Top right logout button using form and query param
    st.markdown(
        f"<div style='text-align:right'>"
        f"<form><button type='submit' name='logout' style='background-color:#f44336;color:white;border:none;padding:5px 10px;border-radius:5px;'>Logout ({st.session_state.role})</button></form>"
        f"</div><br>",
        unsafe_allow_html=True
    )

    # If logout button clicked
    if st.query_params.get("logout") is not None:
        logout()
        st.experimental_rerun()

else:
    st.title("Login to Hospital Management System")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Admin Login")
        admin_user = st.text_input("Admin Username", key="admin_user")
        admin_pass = st.text_input("Admin Password", type="password", key="admin_pass")
        if st.button("Login as Admin"):
            if admin_user == "admin" and admin_pass == "admin123":
                st.session_state.logged_in = True
                st.session_state.role = "admin"
                st.session_state.user = admin_user
                st.rerun()
            else:
                st.error("Invalid admin credentials")

    with col2:
        st.subheader("Staff Login")
        staff_user = st.text_input("Staff Username", key="staff_user")
        staff_pass = st.text_input("Staff Password", type="password", key="staff_pass")
        if st.button("Login as Staff"):
            if staff_user == "staff" and staff_pass == "staff123":
                st.session_state.logged_in = True
                st.session_state.role = "staff"
                st.session_state.user = staff_user
                st.rerun()
            else:
                st.error("Invalid staff credentials")

    st.stop()

 # Stop page here if not logged in
# Set page config
st.set_page_config(page_title="Hospital Management", layout="wide")

# Custom CSS for modern look with black fonts
st.markdown("""
    <style>
        body, h1, h2, h3, h4, h5, h6, p, label, div, span, input, select, textarea {
            color: black !important;
        }
        .block-container {
            padding: 1.5rem 2rem;
        }
        .stSidebar {
            background-color: #f0f2f6;
        }
        .stButton>button {
            background-color: #e3e3e3;
            border-radius: 8px;
        }
        .stDataFrameContainer {
            border: 1px solid #ccc;
            border-radius: 10px;
        }
    </style>
""", unsafe_allow_html=True)

# Sidebar navigation with modern layout
menu = {
    "Dashboard": "",
    "Patient Checkups": "",
    "Patient Tests": "",
    "Patient Management": "",
    "Bed Management": "",
    "Inventory": "",
    "AI Assistant": ""
}

st.sidebar.title(" HMS Navigation")
for page in menu:
    if st.sidebar.button(page):
        st.session_state.page = page

if "page" not in st.session_state:
    st.session_state.page = "Dashboard"

choice = st.session_state.page
if choice == "Dashboard":
    st.subheader(" Dashboard Analytics")

    selected_date = st.date_input("Select Date", value=datetime.today())

    conn = sqlite3.connect("data/hospital.db")
    cursor = conn.cursor()

    # Ensure required tables exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Admissions (
            admission_id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_name TEXT,
            admit_date TEXT,
            discharge_date TEXT,
            bed_number INTEGER,
            notes TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS PatientInflow (
            inflow_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER,
            gender TEXT,
            visit_date TEXT,
            department TEXT,
            notes TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS PatientTests (
            test_id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER,
            test_type TEXT NOT NULL,
            test_date TEXT,
            result TEXT,
            FOREIGN KEY (patient_id) REFERENCES Patients(id)
        )
    """)
    conn.commit()

    formatted_date = selected_date.strftime("%Y-%m-%d")

    # Count total admissions
    cursor.execute("SELECT COUNT(*) FROM Admissions WHERE admit_date = ?", (formatted_date,))
    admission_count = cursor.fetchone()[0]

    # Count total patient visits
    cursor.execute("SELECT COUNT(*) FROM PatientInflow WHERE visit_date = ?", (formatted_date,))
    patient_count = cursor.fetchone()[0]

    # Count total tests
    cursor.execute("SELECT COUNT(*) FROM PatientTests WHERE test_date = ?", (formatted_date,))
    test_count = cursor.fetchone()[0]

    st.markdown("###  Statistics for " + selected_date.strftime("%B %d, %Y"))
    st.write(f" **Total Admissions:** {admission_count}")
    st.write(f" **Total Patient Visits:** {patient_count}")
    st.write(f" **Total Tests Conducted:** {test_count}")

    # --- Hardcoded test types (complete list) ---
    test_types = [
        "Blood Test", "X-Ray", "Thyroid Test", "Urine Test",
        "Diabetes Test", "CT Scan", "MRI", "B12 Test"
    ]

    selected_test = st.selectbox("🔬 Select a Test Type to View Count", sorted(test_types))

    # Fetch test count even if that test was not used yet
    cursor.execute("""
        SELECT COUNT(*) FROM PatientTests 
        WHERE test_type = ? AND test_date = ?
    """, (selected_test, formatted_date))
    test_type_count = cursor.fetchone()[0]

    st.success(f" **{test_type_count} '{selected_test}' tests done** on {selected_date.strftime('%B %d, %Y')}")

    conn.close()


elif choice == "Patient Checkups":
    st.subheader(" Patient Visit Records")

    conn = sqlite3.connect("data/hospital.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS PatientInflow (
            inflow_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER,
            gender TEXT,
            visit_date TEXT,
            department TEXT,
            notes TEXT
        )
    """)
    conn.commit()

    with st.form("outpatient_form"):
        name = st.text_input("Patient Name")
        age = st.number_input("Age", min_value=0, key="inflow_age")
        gender = st.selectbox("Gender", ["Male", "Female", "Other"], key="inflow_gender")
        visit_date = st.date_input("Visit Date", value=datetime.today(), key="inflow_date")
        department = st.text_input("Department Visited", key="inflow_department")
        notes = st.text_area("Doctor's Notes / Complaints", key="inflow_notes")
        submit_visit = st.form_submit_button("Add Visit Record")

        if submit_visit:
            cursor.execute("""
                INSERT INTO PatientInflow (name, age, gender, visit_date, department, notes)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (name, age, gender, visit_date.strftime("%Y-%m-%d"), department, notes))
            conn.commit()
            st.success(" Visit record added successfully!")
            st.rerun()

    st.markdown("---")

    #  Side-by-side layout
    left_col, right_col = st.columns(2)

    with left_col:
        st.subheader(" All Patient Records")
        cursor.execute("SELECT * FROM PatientInflow ORDER BY visit_date DESC")
        visits = cursor.fetchall()
        if visits:
            df_visits = pd.DataFrame(visits, columns=["ID", "Name", "Age", "Gender", "Visit Date", "Department", "Notes"])
            st.dataframe(df_visits, use_container_width=True)
        else:
            st.info("No visit records yet.")

    with right_col:
        st.subheader(" Edit /  Delete Visit Record")
        if visits:
            visit_options = {f"{row[1]} - {row[4]}": row[0] for row in visits}
            selected_visit = st.selectbox("Select visit to update/delete", list(visit_options.keys()), key="edit_visit")
            visit_id = visit_options[selected_visit]

            selected_data = next(row for row in visits if row[0] == visit_id)

            new_name = st.text_input("Patient Name", value=selected_data[1], key="edit_visit_name")
            new_age = st.number_input("Age", value=selected_data[2], min_value=0, key="edit_visit_age")
            new_gender = st.selectbox("Gender", ["Male", "Female", "Other"], index=["Male", "Female", "Other"].index(selected_data[3]), key="edit_visit_gender")
            new_date = st.date_input("Visit Date", value=pd.to_datetime(selected_data[4]), key="edit_visit_date")
            new_dept = st.text_input("Department", value=selected_data[5], key="edit_visit_dept")
            new_notes = st.text_area("Notes", value=selected_data[6], key="edit_visit_notes")

            update_col, delete_col = st.columns(2)
            with update_col:
                if st.button("Update Visit", key="update_visit_btn"):
                    cursor.execute("""
                        UPDATE PatientInflow
                        SET name = ?, age = ?, gender = ?, visit_date = ?, department = ?, notes = ?
                        WHERE inflow_id = ?
                    """, (new_name, new_age, new_gender, new_date.strftime("%Y-%m-%d"), new_dept, new_notes, visit_id))
                    conn.commit()
                    st.success(" Visit updated successfully!")
                    st.rerun()

            with delete_col:
                if st.button("Delete Visit", key="delete_visit_btn"):
                    cursor.execute("DELETE FROM PatientInflow WHERE inflow_id = ?", (visit_id,))
                    conn.commit()
                    st.warning(" Visit record deleted.")
                    st.rerun()
        else:
            st.info("No records to edit/delete.")
elif choice == "Patient Tests":
    st.subheader(" Patient Diagnostic Tests")

    conn = sqlite3.connect("data/hospital.db")
    cursor = conn.cursor()

    # Create PatientTests table with foreign key to Patients
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS PatientTests (
            test_id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER,
            test_type TEXT NOT NULL,
            test_date TEXT,
            result TEXT,
            FOREIGN KEY (patient_id) REFERENCES Patients(id)
        )
    """)
    conn.commit()

    #  Fix: Add patient_id column if missing (older databases)
    cursor.execute("PRAGMA table_info(PatientTests)")
    columns = [col[1] for col in cursor.fetchall()]
    if 'patient_id' not in columns:
        cursor.execute("ALTER TABLE PatientTests ADD COLUMN patient_id INTEGER")
        conn.commit()

    # Get list of patients for dropdown
    cursor.execute("SELECT id, name FROM Patients")
    patients = cursor.fetchall()
    patient_options = {f"{name} (ID: {pid})": pid for pid, name in patients}

    st.markdown("###  Add New Test Record")
    with st.form("add_test_form"):
        selected_patient = st.selectbox("Select Patient", list(patient_options.keys()), key="test_patient_add")
        patient_id = patient_options[selected_patient]

        test_types = ["Blood Test", "X-Ray", "Thyroid Test", "Urine Test",
                      "Diabetes Test", "CT Scan", "MRI", "B12 Test"]
        test_type = st.selectbox("Test Type", test_types, key="test_type_add")
        test_date = st.date_input("Test Date", key="test_date_add")
        result = st.text_area("Test Result / Notes", key="test_result_add")

        submit = st.form_submit_button("Add Test")
        if submit:
            cursor.execute("""
                INSERT INTO PatientTests (patient_id, test_type, test_date, result)
                VALUES (?, ?, ?, ?)
            """, (patient_id, test_type, test_date.strftime("%Y-%m-%d"), result))
            conn.commit()
            st.success(" Test record added successfully!")
            st.rerun()

    st.markdown("###  Edit /  Delete Test Record")

    # Join query to display patient name in test records
    cursor.execute("""
        SELECT t.test_id, p.name, t.test_type, t.test_date, t.result, t.patient_id
        FROM PatientTests t
        JOIN Patients p ON t.patient_id = p.id
        ORDER BY t.test_id ASC
    """)
    tests = cursor.fetchall()

    if tests:
        test_options = {f"{row[1]} - {row[2]} on {row[3]}": row[0] for row in tests}
        selected_label = st.selectbox("Select record to edit/delete", list(test_options.keys()), key="select_test_edit")
        selected_id = test_options[selected_label]

        selected_data = next(row for row in tests if row[0] == selected_id)

        # Reuse patient dropdown
        edit_patient_name = st.selectbox(
            "Patient", list(patient_options.keys()),
            index=list(patient_options.values()).index(selected_data[5]),
            key="test_patient_edit"
        )
        new_patient_id = patient_options[edit_patient_name]

        selected_index = test_types.index(selected_data[2]) if selected_data[2] in test_types else 0
        new_type = st.selectbox("Test Type", test_types, index=selected_index, key="test_type_edit")
        new_date = st.date_input("Test Date", value=pd.to_datetime(selected_data[3]), key="test_date_edit")
        new_result = st.text_area("Result", value=selected_data[4], key="test_result_edit")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Update Record", key="update_test_btn"):
                cursor.execute("""
                    UPDATE PatientTests
                    SET patient_id = ?, test_type = ?, test_date = ?, result = ?
                    WHERE test_id = ?
                """, (new_patient_id, new_type, new_date.strftime("%Y-%m-%d"), new_result, selected_id))
                conn.commit()
                st.success(" Test record updated!")
                st.rerun()

        with col2:
            if st.button("Delete Record", key="delete_test_btn"):
                cursor.execute("DELETE FROM PatientTests WHERE test_id = ?", (selected_id,))
                conn.commit()
                st.warning(" Test record deleted.")
                st.rerun()

    st.markdown("---")
    st.subheader(" All Test Records")

    if tests:
        df_tests = pd.DataFrame(tests, columns=["Test ID", "Patient Name", "Test Type", "Date", "Result", "Patient ID"])
        df_tests.drop(columns=["Patient ID"], inplace=True)
        st.dataframe(df_tests, use_container_width=True)
    else:
        st.info("No test records available.")

    conn.close()




# Patient Management Page
elif choice == "Patient Management":
    st.subheader(" Patient Management")

    col1, col2 = st.columns(2)

    #  Left Column: Add New Patient
    with col1:
        st.markdown("###  Add New Patient")
        with st.form("patient_form"):
            name = st.text_input("Patient Name")
            age = st.number_input("Age", min_value=0)
            gender = st.selectbox("Gender", ["Male", "Female", "Other"])
            admission_date = st.date_input("Admission Date")
            department = st.text_input("Department")

            submitted = st.form_submit_button("Admit Patient")
            if submitted:
                conn = sqlite3.connect("data/hospital.db")
                cursor = conn.cursor()

                #  Find the first vacant bed
                cursor.execute("SELECT bed_id FROM Beds WHERE status = 'Vacant' LIMIT 1")
                bed_result = cursor.fetchone()

                if bed_result:
                    bed_id = bed_result[0]
                    status = "Admitted"

                    #  Insert patient record with assigned bed
                    cursor.execute(
                        "INSERT INTO Patients (name, age, gender, admission_date, status, department, bed_id) VALUES (?, ?, ?, ?, ?, ?, ?)",
                        (name, age, gender, admission_date.strftime("%Y-%m-%d"), status, department, bed_id)
                    )

                    #  Mark that bed as occupied
                    cursor.execute("UPDATE Beds SET status = 'Occupied' WHERE bed_id = ?", (bed_id,))
                    conn.commit()
                    conn.close()

                    st.success(f" {name} admitted and assigned to Bed {bed_id}!")
                    st.rerun()
                else:
                    conn.close()
                    st.error(" No vacant beds available!")

    #  Right Column: Show Admitted Patients Table
    with col2:
        st.markdown("###  Current Admitted Patients")
        conn = sqlite3.connect("data/hospital.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, age, gender, admission_date, department FROM Patients WHERE status = 'Admitted'")
        data = cursor.fetchall()
        conn.close()

        if data:
            df = pd.DataFrame(data, columns=["ID", "Name", "Age", "Gender", "Admission Date", "Department"])
            df.index = df.index + 1
            df.insert(0, "S.No", df.index)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No patients admitted yet.")

    with st.expander(" Discharge Patient"):
        selected_id = st.number_input("Enter Patient ID to discharge", min_value=1, step=1, value=1)
        if st.button("Discharge"):
            conn = sqlite3.connect("data/hospital.db")
            cursor = conn.cursor()
            cursor.execute("UPDATE Patients SET status = 'Discharged', discharge_date = date('now') WHERE id = ?", (selected_id,))
            conn.commit()
            conn.close()
            st.success(f"  Patient ID {selected_id} discharged successfully!")
            st.rerun()

# Bed Management Page
elif choice == "Bed Management":
    st.subheader(" Bed Management")

    conn = sqlite3.connect("data/hospital.db")
    df = pd.read_sql_query("SELECT * FROM Beds", conn)
    conn.close()

    # Create two columns
    left_col, right_col = st.columns(2)

    #  Left Column: View & Filter
    with left_col:
        st.markdown("###  View & Filter Beds")
        vacant_count = df[df["status"] == "Vacant"].shape[0]
        st.info(f"Vacant Beds: {vacant_count}")

        filter_status = st.selectbox("Filter by Status", ["All", "Vacant", "Occupied"])
        filter_ward = st.text_input("Filter by Ward")

        filtered_df = df.copy()
        if filter_status != "All":
            filtered_df = filtered_df[filtered_df["status"] == filter_status]
        if filter_ward:
            filtered_df = filtered_df[filtered_df["ward"].str.lower() == filter_ward.lower()]

        st.dataframe(filtered_df, use_container_width=True)

    #  Right Column: Edit/Add
    with right_col:
        st.markdown("###  Edit /  Add Bed Info")

        conn = sqlite3.connect("data/hospital.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Beds")
        beds = cursor.fetchall()
        conn.close()

        if beds:
            bed_dict = {f"Bed {bed[0]} (Ward: {bed[1]}, Room: {bed[2]})": bed[0] for bed in beds}
            selected_label = st.selectbox("Select Bed to Edit", list(bed_dict.keys()))
            selected_bed_id = bed_dict[selected_label]

            selected_bed = next(bed for bed in beds if bed[0] == selected_bed_id)
            new_ward = st.text_input("Ward", selected_bed[1], key="edit_ward")
            new_room = st.text_input("Room", selected_bed[2], key="edit_room")
            new_status = st.selectbox("Status", ["Vacant", "Occupied"], index=0 if selected_bed[3] == "Vacant" else 1, key="edit_status")

            if st.button("Update Bed Info"):
                conn = sqlite3.connect("data/hospital.db")
                cursor = conn.cursor()
                cursor.execute("UPDATE Beds SET ward = ?, room = ?, status = ? WHERE bed_id = ?",
                               (new_ward, new_room, new_status, selected_bed_id))
                conn.commit()
                conn.close()
                st.success(f" Bed {selected_bed_id} updated successfully!")
                st.rerun()
        else:
            st.info("No beds found.")

        st.markdown("---")
        st.subheader(" Add New Bed")
        with st.form("add_bed_form"):
            new_bed_id = st.number_input("Bed ID", min_value=1, step=1, key="add_id")
            new_ward = st.text_input("Ward", key="add_ward")
            new_room = st.text_input("Room", key="add_room")
            new_status = st.selectbox("Status", ["Vacant", "Occupied"], key="add_status")
            add_bed = st.form_submit_button("Add Bed")

            if add_bed:
                conn = sqlite3.connect("data/hospital.db")
                cursor = conn.cursor()
                try:
                    cursor.execute("INSERT INTO Beds (bed_id, ward, room, status) VALUES (?, ?, ?, ?)",
                                   (new_bed_id, new_ward, new_room, new_status))
                    conn.commit()
                    st.success(f" Bed {new_bed_id} added successfully!")
                    st.rerun()
                except sqlite3.IntegrityError:
                    st.error(" Bed ID already exists!")
                conn.close()
elif choice == "Inventory":
    st.subheader(" Inventory Management")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("####  Search & Items")

        conn = sqlite3.connect("data/hospital.db")
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Inventory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_name TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                unit TEXT NOT NULL
            )
        """)
        conn.commit()

        search = st.text_input("Search Item by Name")
        if search:
            cursor.execute("SELECT * FROM Inventory WHERE item_name LIKE ?", ('%' + search + '%',))
        else:
            cursor.execute("SELECT * FROM Inventory")
        inventory_data = cursor.fetchall()

        if inventory_data:
            df_inv = pd.DataFrame(inventory_data, columns=["ID", "Item", "Qty", "Unit"])
            st.dataframe(df_inv, use_container_width=True)
        else:
            st.info("No inventory items found.")

    with col2:
        st.markdown("####  Add or Edit Item")

        st.subheader("Add New Item")
        with st.form("add_item_form"):
            name = st.text_input("Item Name", key="add_name")
            qty = st.number_input("Quantity", min_value=0, step=1, key="add_qty")
            unit = st.text_input("Unit (e.g. mg, tablets, boxes)", key="add_unit")
            add_btn = st.form_submit_button("Add Item")

            if add_btn:
                if name and unit:
                    cursor.execute("INSERT INTO Inventory (item_name, quantity, unit) VALUES (?, ?, ?)", (name, qty, unit))
                    conn.commit()
                    st.success(f" {name} added successfully!")
                    st.rerun()
                else:
                    st.error(" Please fill all fields.")

        st.divider()
        st.subheader(" Edit or  Delete Item")

        if inventory_data:
            item_dict = {f"{item[1]} ({item[2]} {item[3]})": item[0] for item in inventory_data}
            selected = st.selectbox("Select item", list(item_dict.keys()), key="edit_select")
            selected_id = item_dict[selected]

            selected_data = next(item for item in inventory_data if item[0] == selected_id)
            new_name = st.text_input("Item Name", selected_data[1], key="edit_name")
            new_qty = st.number_input("Quantity", value=selected_data[2], key="edit_qty")
            new_unit = st.text_input("Unit", selected_data[3], key="edit_unit")

            colu1, colu2 = st.columns(2)
            with colu1:
                if st.button("Update Item", key="update_btn"):
                    cursor.execute("UPDATE Inventory SET item_name = ?, quantity = ?, unit = ? WHERE item_id = ?",
                                   (new_name, new_qty, new_unit, selected_id))
                    conn.commit()
                    st.success(" Item updated!")
                    st.rerun()
            with colu2:
                if st.button("Delete Item", key="delete_btn"):
                    cursor.execute("DELETE FROM Inventory WHERE item_id = ?", (selected_id,))
                    conn.commit()
                    st.warning(" Item deleted.")
                    st.rerun()

        conn.close()
elif choice == "AI Assistant":
    st.subheader("AI Assistant")

    tab1, tab2, tab3 = st.tabs(["Dosage Advisor", "Recommend Medicines", "Summarize Notes"])

    # ---- TAB 1: Dosage Advisor ----
    with tab1:
        st.markdown("###  Medicine Dosage Advisor")
        st.markdown("Enter the medicine and patient's age to get a recommended dosage.")

        medicine_name = st.text_input("Enter medicine name", placeholder="e.g., Paracetamol")
        age = st.number_input("Enter patient's age (in years)", min_value=0, max_value=120, step=1)

        if st.button("Suggest Dosage"):
            if medicine_name:
                if age < 1:
                    st.info(f"**{medicine_name} for Infant**: Consult pediatrician. Liquid form only. Usually measured in drops or ml.")
                elif 1 <= age <= 5:
                    st.info(f"**{medicine_name} for Toddler**: 1/4 of adult dose or syrup-based.")
                elif 6 <= age <= 12:
                    st.info(f"**{medicine_name} for Child**: 1/2 of adult dose. Avoid strong antibiotics unless prescribed.")
                elif 13 <= age <= 18:
                    st.info(f"**{medicine_name} for Teenager**: 3/4 or full adult dose depending on weight.")
                elif 19 <= age <= 60:
                    st.info(f"**{medicine_name} for Adult**: Full dose (usually 1 tablet every 6–8 hours).")
                else:
                    st.info(f"**{medicine_name} for Elderly**: Start with 1/2 dose. Monitor kidney/liver health.")
            else:
                st.warning("Please enter a medicine name.")


    # ---- TAB 2: Recommend Medicines ----
    with tab2:
        st.markdown("### Symptom-based Medicine Recommender")
        symptoms = st.text_area("Enter patient symptoms (comma-separated)", placeholder="fever, headache, sore throat")

        if st.button("Recommend Medicines"):
            if symptoms:
                symptom_list = [s.strip().lower() for s in symptoms.split(",")]
                recommendations = []

                if "fever" in symptom_list:
                    recommendations.append("Paracetamol")
                if "headache" in symptom_list:
                    recommendations.append("Ibuprofen")
                if "cold" in symptom_list or "sore throat" in symptom_list:
                    recommendations.append("Cough Syrup")
                if "stomach pain" in symptom_list:
                    recommendations.append("Antacid")
                if "vomiting" in symptom_list:
                    recommendations.append("Ondansetron")

                if recommendations:
                    st.success("**Recommended Medicines:**")
                    st.write(", ".join(set(recommendations)))
                else:
                    st.info("No specific recommendations found. Refer to a doctor.")
            else:
                st.warning("Please enter some symptoms.")

    # ---- TAB 3: Summarize Notes ----
    with tab3:
        st.markdown("### Doctor Notes Summarizer")
        st.markdown("This tool summarizes long notes into short, meaningful summaries using basic AI logic.")

        note_input = st.text_area("Paste Doctor's Notes")

        if st.button("Summarize"):
            if note_input:
                keywords = ["twice", "daily", "week", "quantity", "overdose", "tablet", "syrup"]
                summary = ". ".join([sent for sent in note_input.split(".") if any(word in sent.lower() for word in keywords)])
                if summary:
                    st.success("**Summary:**")
                    st.write(summary.strip())
                else:
                    st.info("No key instructions found. Please check the note.")
            else:
                st.warning("Please enter some notes.")
