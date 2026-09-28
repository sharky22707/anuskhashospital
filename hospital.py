import streamlit as st
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List


# ============================================================
# ABSTRACT BASE CLASS
# ============================================================

class Person(ABC):

    def __init__(self, person_id, name, age, phone):
        self.__person_id = person_id
        self.__name = name
        self.__age = age
        self.__phone = phone

    # Encapsulation: getters
    @property
    def person_id(self):
        return self.__person_id

    @property
    def name(self):
        return self.__name

    @property
    def age(self):
        return self.__age

    @property
    def phone(self):
        return self.__phone

    @abstractmethod
    def get_role(self):
        pass


# ============================================================
# PATIENT CLASS
# ============================================================

class Patient(Person):

    def __init__(
        self,
        patient_id,
        name,
        age,
        phone,
        blood_group,
        condition="Stable"
    ):
        super().__init__(patient_id, name, age, phone)

        self.__blood_group = blood_group
        self.__condition = condition
        self.__medical_history = []

    @property
    def blood_group(self):
        return self.__blood_group

    @property
    def condition(self):
        return self.__condition

    def add_medical_history(self, record):
        self.__medical_history.append(record)

    def get_history(self):
        return self.__medical_history

    def update_condition(self, condition):
        self.__condition = condition

    def get_role(self):
        return "Patient"


# ============================================================
# EMERGENCY PATIENT
# INHERITANCE + POLYMORPHISM
# ============================================================

class EmergencyPatient(Patient):

    def __init__(
        self,
        patient_id,
        name,
        age,
        phone,
        blood_group,
        condition,
        severity,
        symptoms
    ):
        super().__init__(
            patient_id,
            name,
            age,
            phone,
            blood_group,
            condition
        )

        self.__severity = severity
        self.__symptoms = symptoms

    @property
    def severity(self):
        return self.__severity

    @property
    def symptoms(self):
        return self.__symptoms

    # Polymorphic method
    def calculate_priority(self):
        severity_score = {
            "Critical": 100,
            "High": 75,
            "Medium": 50,
            "Low": 25
        }

        score = severity_score.get(self.__severity, 0)

        # Age-based additional priority
        if self.age >= 65:
            score += 10

        if self.age <= 12:
            score += 10

        return min(score, 100)

    def get_role(self):
        return "Emergency Patient"


# ============================================================
# DOCTOR CLASS
# ============================================================

class Doctor(Person):

    def __init__(
        self,
        doctor_id,
        name,
        age,
        phone,
        specialization
    ):
        super().__init__(doctor_id, name, age, phone)

        self.__specialization = specialization
        self.__available = True
        self.__assigned_patients = []

    @property
    def specialization(self):
        return self.__specialization

    @property
    def available(self):
        return self.__available

    def assign_patient(self, patient_id):
        self.__assigned_patients.append(patient_id)

    def get_assigned_patients(self):
        return self.__assigned_patients

    def change_availability(self, status):
        self.__available = status

    def get_role(self):
        return "Doctor"


# ============================================================
# APPOINTMENT CLASS
# ============================================================

class Appointment:

    def __init__(
        self,
        appointment_id,
        patient_id,
        doctor_id,
        date,
        time,
        reason
    ):
        self.__appointment_id = appointment_id
        self.__patient_id = patient_id
        self.__doctor_id = doctor_id
        self.__date = date
        self.__time = time
        self.__reason = reason
        self.__status = "Scheduled"

    @property
    def appointment_id(self):
        return self.__appointment_id

    @property
    def patient_id(self):
        return self.__patient_id

    @property
    def doctor_id(self):
        return self.__doctor_id

    @property
    def date(self):
        return self.__date

    @property
    def time(self):
        return self.__time

    @property
    def reason(self):
        return self.__reason

    @property
    def status(self):
        return self.__status

    def cancel(self):
        self.__status = "Cancelled"

    def complete(self):
        self.__status = "Completed"


# ============================================================
# HOSPITAL MANAGEMENT SYSTEM
# ============================================================

class HospitalSystem:

    def __init__(self):
        self.patients = []
        self.doctors = []
        self.appointments = []
        self.emergency_cases = []

    # ---------------- PATIENT ----------------

    def add_patient(self, patient):
        self.patients.append(patient)

    def get_patient(self, patient_id):
        for patient in self.patients:
            if patient.person_id == patient_id:
                return patient

        return None

    # ---------------- DOCTOR ----------------

    def add_doctor(self, doctor):
        self.doctors.append(doctor)

    def get_doctor(self, doctor_id):
        for doctor in self.doctors:
            if doctor.person_id == doctor_id:
                return doctor

        return None

    # ---------------- APPOINTMENT ----------------

    def add_appointment(self, appointment):
        self.appointments.append(appointment)

    # ---------------- EMERGENCY ----------------

    def add_emergency(self, emergency_patient):
        self.emergency_cases.append(emergency_patient)

        # Highest priority first
        self.emergency_cases.sort(
            key=lambda patient: patient.calculate_priority(),
            reverse=True
        )

    def get_emergency_queue(self):
        return self.emergency_cases


# ============================================================
# STREAMLIT INITIALIZATION
# ============================================================

st.set_page_config(
    page_title="Smart Hospital Management",
    page_icon="🏥",
    layout="wide"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown("""
<style>

.main {
    background-color: #f5f7fb;
}

.header {
    padding: 25px;
    border-radius: 15px;
    background: linear-gradient(135deg, #0f766e, #0891b2);
    color: white;
    margin-bottom: 25px;
}

.header h1 {
    margin-bottom: 5px;
}

.card {
    padding: 20px;
    border-radius: 15px;
    background-color: white;
    border: 1px solid #e5e7eb;
    margin-bottom: 15px;
}

.metric-card {
    padding: 20px;
    border-radius: 15px;
    background-color: white;
    text-align: center;
    border: 1px solid #e5e7eb;
}

.metric-number {
    font-size: 32px;
    font-weight: bold;
    color: #0f766e;
}

.priority-critical {
    padding: 12px;
    border-radius: 10px;
    background-color: #fee2e2;
    border-left: 5px solid #dc2626;
}

.priority-high {
    padding: 12px;
    border-radius: 10px;
    background-color: #ffedd5;
    border-left: 5px solid #f97316;
}

.priority-medium {
    padding: 12px;
    border-radius: 10px;
    background-color: #fef9c3;
    border-left: 5px solid #eab308;
}

.priority-low {
    padding: 12px;
    border-radius: 10px;
    background-color: #dcfce7;
    border-left: 5px solid #22c55e;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# SESSION STATE
# ============================================================

if "hospital" not in st.session_state:

    hospital = HospitalSystem()

    # Sample patients
    hospital.add_patient(
        Patient(
            "P001",
            "Rahul Sharma",
            32,
            "9876543210",
            "O+",
            "Stable"
        )
    )

    hospital.add_patient(
        Patient(
            "P002",
            "Priya Patil",
            45,
            "9876501234",
            "A+",
            "Under Observation"
        )
    )

    # Sample doctors
    hospital.add_doctor(
        Doctor(
            "D001",
            "Dr. Amit Mehta",
            42,
            "9876541111",
            "Cardiologist"
        )
    )

    hospital.add_doctor(
        Doctor(
            "D002",
            "Dr. Sneha Shah",
            38,
            "9876542222",
            "General Physician"
        )
    )

    hospital.add_doctor(
        Doctor(
            "D003",
            "Dr. Raj Verma",
            45,
            "9876543333",
            "Neurologist"
        )
    )

    st.session_state.hospital = hospital


hospital = st.session_state.hospital


# ============================================================
# HEADER
# ============================================================

st.markdown("""
<div class="header">

<h1>🏥 Smart Hospital Management System</h1>

<p>
Object-Oriented Hospital Management & Emergency Prioritization
</p>

</div>
""", unsafe_allow_html=True)


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("🏥 Hospital System")

page = st.sidebar.radio(
    "Navigation",
    [
        "📊 Dashboard",
        "👤 Patients",
        "👨‍⚕️ Doctors",
        "📅 Appointments",
        "🚨 Emergency",
        "🧠 OOP Concepts"
    ]
)


# ============================================================
# DASHBOARD
# ============================================================

if page == "📊 Dashboard":

    st.subheader("📊 Hospital Dashboard")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown("""
        <div class="metric-card">
        <div class="metric-number">{}</div>
        <div>Patients</div>
        </div>
        """.format(len(hospital.patients)), unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="metric-card">
        <div class="metric-number">{}</div>
        <div>Doctors</div>
        </div>
        """.format(len(hospital.doctors)), unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="metric-card">
        <div class="metric-number">{}</div>
        <div>Appointments</div>
        </div>
        """.format(len(hospital.appointments)), unsafe_allow_html=True)

    with col4:
        st.markdown("""
        <div class="metric-card">
        <div class="metric-number">{}</div>
        <div>Emergency Cases</div>
        </div>
        """.format(len(hospital.emergency_cases)), unsafe_allow_html=True)

    st.divider()

    st.subheader("🚨 Current Emergency Queue")

    if hospital.emergency_cases:

        for index, patient in enumerate(
            hospital.emergency_cases,
            start=1
        ):

            score = patient.calculate_priority()

            if score >= 90:
                css_class = "priority-critical"
                label = "🔴 CRITICAL"

            elif score >= 70:
                css_class = "priority-high"
                label = "🟠 HIGH"

            elif score >= 40:
                css_class = "priority-medium"
                label = "🟡 MEDIUM"

            else:
                css_class = "priority-low"
                label = "🟢 LOW"

            st.markdown(
                f"""
                <div class="{css_class}">
                    <b>#{index} — {patient.name}</b><br>
                    Patient ID: {patient.person_id}<br>
                    Severity: {patient.severity}<br>
                    Priority Score: <b>{score}/100</b><br>
                    Symptoms: {patient.symptoms}
                    <br><br>
                    <b>{label}</b>
                </div>
                """,
                unsafe_allow_html=True
            )

    else:
        st.info("No emergency cases currently registered.")


# ============================================================
# PATIENT PAGE
# ============================================================

elif page == "👤 Patients":

    st.subheader("👤 Patient Management")

    tab1, tab2 = st.tabs(
        ["➕ Register Patient", "📋 Patient Records"]
    )

    with tab1:

        with st.form("patient_form"):

            col1, col2 = st.columns(2)

            with col1:

                patient_id = st.text_input(
                    "Patient ID",
                    placeholder="P003"
                )

                name = st.text_input("Patient Name")

                age = st.number_input(
                    "Age",
                    min_value=0,
                    max_value=120,
                    value=20
                )

            with col2:

                phone = st.text_input("Phone")

                blood_group = st.selectbox(
                    "Blood Group",
                    [
                        "A+",
                        "A-",
                        "B+",
                        "B-",
                        "AB+",
                        "AB-",
                        "O+",
                        "O-"
                    ]
                )

                condition = st.selectbox(
                    "Condition",
                    [
                        "Stable",
                        "Under Observation",
                        "Critical"
                    ]
                )

            submit = st.form_submit_button(
                "Register Patient"
            )

            if submit:

                if not patient_id or not name:

                    st.error(
                        "Patient ID and Name are required."
                    )

                elif hospital.get_patient(patient_id):

                    st.error(
                        "Patient ID already exists."
                    )

                else:

                    patient = Patient(
                        patient_id,
                        name,
                        age,
                        phone,
                        blood_group,
                        condition
                    )

                    hospital.add_patient(patient)

                    st.success(
                        f"Patient {name} registered successfully."
                    )

    with tab2:

        if hospital.patients:

            for patient in hospital.patients:

                with st.expander(
                    f"👤 {patient.name} — {patient.person_id}"
                ):

                    col1, col2 = st.columns(2)

                    with col1:
                        st.write(
                            f"**Age:** {patient.age}"
                        )

                        st.write(
                            f"**Phone:** {patient.phone}"
                        )

                    with col2:

                        st.write(
                            f"**Blood Group:** "
                            f"{patient.blood_group}"
                        )

                        st.write(
                            f"**Condition:** "
                            f"{patient.condition}"
                        )


# ============================================================
# DOCTOR PAGE
# ============================================================

elif page == "👨‍⚕️ Doctors":

    st.subheader("👨‍⚕️ Doctor Management")

    tab1, tab2 = st.tabs(
        ["➕ Add Doctor", "📋 Doctor Records"]
    )

    with tab1:

        with st.form("doctor_form"):

            col1, col2 = st.columns(2)

            with col1:

                doctor_id = st.text_input(
                    "Doctor ID",
                    placeholder="D004"
                )

                name = st.text_input(
                    "Doctor Name"
                )

                age = st.number_input(
                    "Age",
                    min_value=25,
                    max_value=80,
                    value=35
                )

            with col2:

                phone = st.text_input(
                    "Phone"
                )

                specialization = st.selectbox(
                    "Specialization",
                    [
                        "General Physician",
                        "Cardiologist",
                        "Neurologist",
                        "Orthopedic",
                        "Pediatrician",
                        "Surgeon"
                    ]
                )

            submit = st.form_submit_button(
                "Add Doctor"
            )

            if submit:

                if hospital.get_doctor(doctor_id):

                    st.error(
                        "Doctor ID already exists."
                    )

                else:

                    doctor = Doctor(
                        doctor_id,
                        name,
                        age,
                        phone,
                        specialization
                    )

                    hospital.add_doctor(doctor)

                    st.success(
                        f"Dr. {name} added successfully."
                    )

    with tab2:

        for doctor in hospital.doctors:

            status = (
                "🟢 Available"
                if doctor.available
                else "🔴 Busy"
            )

            with st.expander(
                f"👨‍⚕️ {doctor.name} — "
                f"{doctor.specialization}"
            ):

                st.write(
                    f"**Doctor ID:** {doctor.person_id}"
                )

                st.write(
                    f"**Phone:** {doctor.phone}"
                )

                st.write(
                    f"**Status:** {status}"
                )

                st.write(
                    "**Assigned Patients:**",
                    doctor.get_assigned_patients()
                )


# ============================================================
# APPOINTMENT PAGE
# ============================================================

elif page == "📅 Appointments":

    st.subheader("📅 Appointment Management")

    if not hospital.patients or not hospital.doctors:

        st.warning(
            "You need at least one patient and doctor."
        )

    else:

        with st.form("appointment_form"):

            patient_options = {
                f"{p.name} ({p.person_id})":
                p.person_id
                for p in hospital.patients
            }

            doctor_options = {
                f"{d.name} ({d.specialization})":
                d.person_id
                for d in hospital.doctors
            }

            patient_name = st.selectbox(
                "Select Patient",
                list(patient_options.keys())
            )

            doctor_name = st.selectbox(
                "Select Doctor",
                list(doctor_options.keys())
            )

            col1, col2 = st.columns(2)

            with col1:
                date = st.date_input(
                    "Appointment Date"
                )

            with col2:
                time = st.time_input(
                    "Appointment Time"
                )

            reason = st.text_input(
                "Reason for Appointment"
            )

            submit = st.form_submit_button(
                "📅 Book Appointment"
            )

            if submit:

                appointment_id = (
                    f"A{len(hospital.appointments) + 1:03d}"
                )

                appointment = Appointment(
                    appointment_id,
                    patient_options[patient_name],
                    doctor_options[doctor_name],
                    date,
                    time,
                    reason
                )

                hospital.add_appointment(
                    appointment
                )

                doctor = hospital.get_doctor(
                    doctor_options[doctor_name]
                )

                doctor.assign_patient(
                    patient_options[patient_name]
                )

                st.success(
                    f"Appointment {appointment_id} booked."
                )

    st.divider()

    st.subheader("📋 Appointment Records")

    if hospital.appointments:

        for appointment in hospital.appointments:

            patient = hospital.get_patient(
                appointment.patient_id
            )

            doctor = hospital.get_doctor(
                appointment.doctor_id
            )

            st.markdown(
                f"""
                <div class="card">

                <b>Appointment ID:</b>
                {appointment.appointment_id}<br>

                <b>Patient:</b>
                {patient.name}<br>

                <b>Doctor:</b>
                {doctor.name}<br>

                <b>Date:</b>
                {appointment.date}<br>

                <b>Time:</b>
                {appointment.time}<br>

                <b>Reason:</b>
                {appointment.reason}<br>

                <b>Status:</b>
                {appointment.status}

                </div>
                """,
                unsafe_allow_html=True
            )


# ============================================================
# EMERGENCY PAGE
# ============================================================

elif page == "🚨 Emergency":

    st.subheader("🚨 Emergency Prioritization System")

    st.info(
        "Emergency patients are automatically ordered "
        "according to their calculated priority score."
    )

    with st.form("emergency_form"):

        col1, col2 = st.columns(2)

        with col1:

            patient_id = st.text_input(
                "Emergency Patient ID",
                placeholder="E001"
            )

            name = st.text_input(
                "Patient Name"
            )

            age = st.number_input(
                "Age",
                min_value=0,
                max_value=120,
                value=30
            )

            phone = st.text_input(
                "Phone"
            )

            blood_group = st.selectbox(
                "Blood Group",
                [
                    "A+",
                    "A-",
                    "B+",
                    "B-",
                    "AB+",
                    "AB-",
                    "O+",
                    "O-"
                ],
                key="emergency_blood"
            )

        with col2:

            severity = st.selectbox(
                "Severity",
                [
                    "Critical",
                    "High",
                    "Medium",
                    "Low"
                ]
            )

            condition = st.selectbox(
                "Current Condition",
                [
                    "Critical",
                    "Unstable",
                    "Stable"
                ]
            )

            symptoms = st.text_area(
                "Symptoms",
                placeholder=(
                    "Example: chest pain, "
                    "difficulty breathing..."
                )
            )

        submit = st.form_submit_button(
            "🚨 Register Emergency"
        )

        if submit:

            if not patient_id or not name:

                st.error(
                    "Patient ID and Name are required."
                )

            else:

                emergency_patient = EmergencyPatient(
                    patient_id,
                    name,
                    age,
                    phone,
                    blood_group,
                    condition,
                    severity,
                    symptoms
                )

                hospital.add_emergency(
                    emergency_patient
                )

                score = (
                    emergency_patient.calculate_priority()
                )

                st.success(
                    f"Emergency case registered. "
                    f"Priority Score: {score}/100"
                )

    st.divider()

    st.subheader("🚑 Emergency Queue")

    if hospital.emergency_cases:

        for index, patient in enumerate(
            hospital.emergency_cases,
            start=1
        ):

            score = patient.calculate_priority()

            if score >= 90:
                label = "🔴 CRITICAL"

            elif score >= 70:
                label = "🟠 HIGH"

            elif score >= 40:
                label = "🟡 MEDIUM"

            else:
                label = "🟢 LOW"

            st.markdown(
                f"""
                <div class="card">

                <h3>#{index} {patient.name}</h3>

                <b>Patient ID:</b>
                {patient.person_id}<br>

                <b>Age:</b>
                {patient.age}<br>

                <b>Severity:</b>
                {patient.severity}<br>

                <b>Symptoms:</b>
                {patient.symptoms}<br>

                <b>Priority Score:</b>
                {score}/100<br>

                <h4>{label}</h4>

                </div>
                """,
                unsafe_allow_html=True
            )

    else:

        st.info(
            "No emergency cases registered."
        )


# ============================================================
# OOP EXPLANATION PAGE
# ============================================================

elif page == "🧠 OOP Concepts":

    st.subheader("🧠 Object-Oriented Programming Used")

    st.markdown("""
    ### 1. 🔒 Encapsulation

    Sensitive attributes are kept private using `__`.

    Example:

    ```python
    class Patient:

        def __init__(self, name):
            self.__name = name

        @property
        def name(self):
            return self.__name
    ```

    Patient data is controlled through class methods and properties.

    ---

    ### 2. 🧬 Inheritance

    `Patient` inherits from the abstract `Person` class.

    ```python
    class Patient(Person):
        ...
    ```

    `EmergencyPatient` further inherits from `Patient`.

    ```python
    class EmergencyPatient(Patient):
        ...
    ```

    ---

    ### 3. 🎯 Abstraction

    `Person` is an abstract class.

    ```python
    class Person(ABC):

        @abstractmethod
        def get_role(self):
            pass
    ```

    Every subclass must implement `get_role()`.

    ---

    ### 4. 🔄 Polymorphism

    `EmergencyPatient` provides its own implementation of:

    ```python
    calculate_priority()
    ```

    The hospital system can call:

    ```python
    patient.calculate_priority()
    ```

    without needing to know the internal calculation.

    ---

    ### 5. 🏗️ Composition

    `HospitalSystem` contains:

    - Patients
    - Doctors
    - Appointments
    - Emergency cases

    This models the relationship between the hospital and its components.
    """)


# ============================================================
# FOOTER
# ============================================================

st.sidebar.divider()

st.sidebar.caption(
    "🏥 Smart Hospital Management System"
)

st.sidebar.caption(
    "Python + Streamlit + OOP"
)
