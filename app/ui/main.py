"""
CervixAI Streamlit Frontend - Main Entry Point
"""
import streamlit as st
import requests

# Configure page
st.set_page_config(
    page_title="CervixAI",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Base URL
API_URL = "http://localhost:8000/api/v1"

# Session state initialization
if "token" not in st.session_state:
    st.session_state.token = None
if "user" not in st.session_state:
    st.session_state.user = None


def api_request(method: str, endpoint: str, data: dict = None, files: dict = None):
    """Make API request with authentication."""
    headers = {}
    if st.session_state.token:
        headers["Authorization"] = f"Bearer {st.session_state.token}"
    
    url = f"{API_URL}{endpoint}"
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, params=data)
        elif method == "POST":
            if files:
                response = requests.post(url, headers=headers, files=files, data=data)
            else:
                response = requests.post(url, headers=headers, json=data)
        elif method == "PATCH":
            response = requests.patch(url, headers=headers, json=data)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)
        else:
            return None, "Invalid method"
        
        if response.status_code in [200, 201]:
            return response.json(), None
        elif response.status_code == 204:
            return {}, None
        else:
            error_msg = response.json().get("detail", "Unknown error")
            return None, error_msg
    except requests.exceptions.ConnectionError:
        return None, "Cannot connect to API. Ensure the backend is running."
    except Exception as e:
        return None, str(e)


def login_page():
    """Login page."""
    st.title("🔬 CervixAI")
    st.subheader("AI-Powered Cervical Cancer Screening")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### Login")
        
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login", use_container_width=True)
            
            if submit:
                if email and password:
                    data, error = api_request("POST", "/auth/login", {
                        "email": email,
                        "password": password
                    })
                    if data:
                        st.session_state.token = data["access_token"]
                        # Get user profile
                        user, _ = api_request("GET", "/users/me")
                        st.session_state.user = user
                        st.rerun()
                    else:
                        st.error(f"Login failed: {error}")
                else:
                    st.warning("Please enter email and password")
        
        st.divider()
        st.markdown("### Register")
        
        with st.form("register_form"):
            reg_name = st.text_input("Full Name")
            reg_email = st.text_input("Email Address")
            reg_password = st.text_input("Password", type="password", key="reg_pass")
            reg_role = st.selectbox("Role", ["physician", "cytotechnologist", "pathologist", "admin"])
            reg_submit = st.form_submit_button("Register", use_container_width=True)
            
            if reg_submit:
                if reg_name and reg_email and reg_password:
                    data, error = api_request("POST", "/auth/register", {
                        "name": reg_name,
                        "email": reg_email,
                        "password": reg_password,
                        "role": reg_role
                    })
                    if data:
                        st.success("Registration successful! Please login.")
                    else:
                        st.error(f"Registration failed: {error}")
                else:
                    st.warning("Please fill all fields")


def dashboard_page():
    """Main dashboard."""
    st.title("📊 Dashboard")
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    # Get counts
    patients_data, _ = api_request("GET", "/patients", {"limit": 1})
    screenings_pending, _ = api_request("GET", "/screenings", {"status": "pending", "limit": 1})
    screenings_review, _ = api_request("GET", "/screenings", {"status": "ai_analyzed", "limit": 1})
    
    with col1:
        st.metric("Total Patients", patients_data.get("total", 0) if patients_data else 0)
    
    with col2:
        st.metric("Pending Upload", screenings_pending.get("total", 0) if screenings_pending else 0)
    
    with col3:
        st.metric("Awaiting Review", screenings_review.get("total", 0) if screenings_review else 0)
    
    with col4:
        st.metric("Your Role", st.session_state.user.get("role", "").title())
    
    st.divider()
    
    # Recent screenings
    st.subheader("Recent Screenings")
    screenings_data, error = api_request("GET", "/screenings", {"limit": 10})
    
    if screenings_data and screenings_data.get("items"):
        for screening in screenings_data["items"]:
            status_color = {
                "pending": "🟡",
                "ai_analyzed": "🟠",
                "under_review": "🔵",
                "completed": "🟢",
                "cancelled": "🔴"
            }.get(screening["status"], "⚪")
            
            with st.expander(f"{status_color} Screening {screening['id'][:8]}... - {screening['status'].upper()}"):
                st.write(f"**Patient ID:** {screening['patient_id'][:8]}...")
                st.write(f"**Created:** {screening['created_at']}")
                st.write(f"**Status:** {screening['status']}")
                if screening.get("reason_for_screening"):
                    st.write(f"**Reason:** {screening['reason_for_screening']}")
    else:
        st.info("No screenings found. Create a new patient and screening to get started.")


def patients_page():
    """Patient management page."""
    st.title("👥 Patients")
    
    # Search
    search_term = st.text_input("🔍 Search patients by name or MRN")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Patient list
        params = {"limit": 20}
        if search_term:
            params["search"] = search_term
        
        data, error = api_request("GET", "/patients", params)
        
        if data and data.get("items"):
            for patient in data["items"]:
                consent_icon = "✅" if patient.get("consent_given") else "⚠️"
                with st.expander(f"{consent_icon} {patient['first_name']} {patient['last_name']} - {patient.get('medical_record_number', 'N/A')}"):
                    st.write(f"**DOB:** {patient['date_of_birth']}")
                    st.write(f"**Email:** {patient.get('email', 'N/A')}")
                    st.write(f"**Phone:** {patient.get('phone', 'N/A')}")
                    st.write(f"**Consent:** {'Yes' if patient.get('consent_given') else 'No'}")
                    
                    if st.button("Create Screening", key=f"screen_{patient['id']}"):
                        st.session_state.selected_patient = patient
                        st.session_state.page = "screening"
                        st.rerun()
        else:
            st.info("No patients found.")
    
    with col2:
        # Add new patient
        st.subheader("➕ Add Patient")
        
        with st.form("add_patient"):
            first_name = st.text_input("First Name")
            last_name = st.text_input("Last Name")
            dob = st.date_input("Date of Birth")
            mrn = st.text_input("Medical Record Number")
            email = st.text_input("Email")
            phone = st.text_input("Phone")
            consent = st.checkbox("Consent Given")
            
            if st.form_submit_button("Add Patient", use_container_width=True):
                if first_name and last_name:
                    patient_data = {
                        "first_name": first_name,
                        "last_name": last_name,
                        "date_of_birth": str(dob),
                        "medical_record_number": mrn if mrn else None,
                        "email": email if email else None,
                        "phone": phone if phone else None,
                        "consent_given": consent
                    }
                    result, error = api_request("POST", "/patients", patient_data)
                    if result:
                        st.success("Patient added successfully!")
                        st.rerun()
                    else:
                        st.error(f"Failed: {error}")
                else:
                    st.warning("First and last name are required")


def screening_page():
    """Screening and image upload page."""
    st.title("🔬 Screening")
    
    # Patient selection if not coming from patients page
    if "selected_patient" not in st.session_state:
        st.session_state.selected_patient = None
    
    # Get patients for selection
    patients_data, _ = api_request("GET", "/patients", {"limit": 100})
    
    if not patients_data or not patients_data.get("items"):
        st.warning("No patients found. Please add a patient first.")
        return
    
    patient_options = {
        f"{p['first_name']} {p['last_name']} ({p.get('medical_record_number', 'N/A')})": p
        for p in patients_data["items"]
    }
    
    selected_name = st.selectbox("Select Patient", list(patient_options.keys()))
    selected_patient = patient_options[selected_name]
    
    if not selected_patient.get("consent_given"):
        st.error("⚠️ Patient consent is required before screening.")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Create New Screening")
        
        with st.form("create_screening"):
            reason = st.text_input("Reason for Screening")
            notes = st.text_area("Clinical Notes")
            
            if st.form_submit_button("Create Screening", use_container_width=True):
                data, error = api_request("POST", "/screenings", {
                    "patient_id": selected_patient["id"],
                    "reason_for_screening": reason,
                    "clinical_notes": notes
                })
                if data:
                    st.success(f"Screening created! ID: {data['id'][:8]}...")
                    st.session_state.current_screening = data
                    st.rerun()
                else:
                    st.error(f"Failed: {error}")
    
    with col2:
        st.subheader("Patient Screenings")
        
        screenings_data, _ = api_request("GET", "/screenings", {"patient_id": selected_patient["id"]})
        
        if screenings_data and screenings_data.get("items"):
            for screening in screenings_data["items"]:
                status_color = {
                    "pending": "🟡",
                    "ai_analyzed": "🟠",
                    "completed": "🟢"
                }.get(screening["status"], "⚪")
                
                with st.expander(f"{status_color} {screening['id'][:8]}... - {screening['status']}"):
                    st.write(f"**Created:** {screening['created_at']}")
                    
                    # Upload image
                    if screening["status"] == "pending":
                        uploaded_file = st.file_uploader(
                            "Upload Image",
                            type=["jpg", "jpeg", "png"],
                            key=f"upload_{screening['id']}"
                        )
                        
                        if uploaded_file and st.button("Upload", key=f"btn_upload_{screening['id']}"):
                            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                            result, error = api_request(
                                "POST",
                                f"/images/upload/{screening['id']}",
                                files=files
                            )
                            if result:
                                st.success("Image uploaded!")
                                st.rerun()
                            else:
                                st.error(f"Upload failed: {error}")
                        
                        if st.button("Run AI Analysis", key=f"analyze_{screening['id']}"):
                            result, error = api_request("POST", "/diagnoses/analyze", {
                                "screening_id": screening["id"]
                            })
                            if result:
                                st.success(f"AI Prediction: {result['ai_prediction']} (Confidence: {result['ai_confidence']:.1%})")
                                st.rerun()
                            else:
                                st.error(f"Analysis failed: {error}")
                    
                    elif screening["status"] == "ai_analyzed":
                        st.info("Awaiting clinician review")
                        if st.button("Go to Review", key=f"review_{screening['id']}"):
                            st.session_state.review_screening = screening
                            st.session_state.page = "review"
                            st.rerun()


def review_page():
    """Clinician review page."""
    st.title("📋 Clinician Review")
    
    # Get screenings needing review
    screenings_data, _ = api_request("GET", "/screenings", {"status": "ai_analyzed", "limit": 20})
    
    if not screenings_data or not screenings_data.get("items"):
        st.info("No screenings awaiting review.")
        return
    
    for screening in screenings_data["items"]:
        with st.expander(f"🟠 Screening {screening['id'][:8]}... - Awaiting Review", expanded=True):
            # Get diagnosis
            diagnosis, _ = api_request("GET", f"/diagnoses/screening/{screening['id']}")
            
            if diagnosis:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("### AI Analysis")
                    st.write(f"**Prediction:** {diagnosis.get('ai_prediction', 'N/A')}")
                    st.write(f"**Confidence:** {diagnosis.get('ai_confidence', 0):.1%}")
                    st.write(f"**Notes:** {diagnosis.get('ai_notes', 'N/A')}")
                
                with col2:
                    st.markdown("### Your Review")
                    
                    with st.form(f"review_form_{diagnosis['id']}"):
                        agrees = st.radio("Do you agree with AI?", ["Yes", "No"])
                        
                        diagnosis_options = [
                            "nilm", "asc_us", "asc_h", "lsil", "hsil", 
                            "scc", "agc", "adenocarcinoma", "unsatisfactory"
                        ]
                        clinician_diagnosis = st.selectbox(
                            "Your Diagnosis",
                            diagnosis_options,
                            index=diagnosis_options.index(diagnosis.get("ai_prediction", "nilm")) if diagnosis.get("ai_prediction") in diagnosis_options else 0
                        )
                        clinician_notes = st.text_area("Notes")
                        follow_up = st.checkbox("Follow-up Recommended")
                        follow_up_notes = st.text_input("Follow-up Notes") if follow_up else ""
                        
                        if st.form_submit_button("Submit Review", use_container_width=True):
                            result, error = api_request("POST", "/diagnoses/review", {
                                "diagnosis_id": diagnosis["id"],
                                "agrees_with_ai": agrees == "Yes",
                                "clinician_diagnosis": clinician_diagnosis,
                                "clinician_notes": clinician_notes,
                                "follow_up_recommended": follow_up,
                                "follow_up_notes": follow_up_notes
                            })
                            if result:
                                st.success("Review submitted successfully!")
                                st.rerun()
                            else:
                                st.error(f"Failed: {error}")


def sidebar():
    """Sidebar navigation."""
    with st.sidebar:
        st.image("https://via.placeholder.com/150x50?text=CervixAI", use_container_width=True)
        st.markdown(f"**Welcome, {st.session_state.user.get('name', 'User')}**")
        st.markdown(f"Role: `{st.session_state.user.get('role', 'N/A')}`")
        
        st.divider()
        
        if st.button("📊 Dashboard", use_container_width=True):
            st.session_state.page = "dashboard"
            st.rerun()
        
        if st.button("👥 Patients", use_container_width=True):
            st.session_state.page = "patients"
            st.rerun()
        
        if st.button("🔬 Screening", use_container_width=True):
            st.session_state.page = "screening"
            st.rerun()
        
        if st.button("📋 Review", use_container_width=True):
            st.session_state.page = "review"
            st.rerun()
        
        st.divider()
        
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.token = None
            st.session_state.user = None
            st.rerun()


def main():
    """Main application."""
    if not st.session_state.token:
        login_page()
    else:
        sidebar()
        
        page = st.session_state.get("page", "dashboard")
        
        if page == "dashboard":
            dashboard_page()
        elif page == "patients":
            patients_page()
        elif page == "screening":
            screening_page()
        elif page == "review":
            review_page()
        else:
            dashboard_page()


if __name__ == "__main__":
    main()
