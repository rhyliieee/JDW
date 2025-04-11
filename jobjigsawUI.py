import streamlit as st
from datetime import datetime
from graph import graphbuilder

#Get data from state
#def get_data_from_state( job_title: str job_location: str job_type: str department: str expiry_date: str job_description: str):
#     return f"""Job Title: {job_title}

# Preprocessing function to compile job description data
def compile_job_description(job_title, job_location, job_type, department, expiry_date, job_description):
    return f"""Job Title: {job_title}
Job Location: {job_location}
Job Type: {job_type}
Department: {department}
Job Expiry Date: {expiry_date}

Job Description: 
{job_description}
"""

# Streamlit UI components
st.title("Job Jigsaw - Job Posting Form")

# Textbox for Job Title
job_title = st.text_input("Job Title")

# Dropdown for Department
department = st.selectbox("Department", ["Engineering", "Marketing", "Sales", "HR", "Finance"])

# Textbox for Job Expiry Date with calendar picker
expiry_date = st.date_input("Job Expiry Date", min_value=datetime.today())

# Radio button for Job Location
job_location = st.radio("Job Location", ["Onsite", "Remote", "Hybrid"])

# Radio button for Job Type
job_type = st.radio("Job Type", ["Part-time", "Internship", "Fulltime"])

job_qualifications = st.text_area("Job Qualifications", height=100)

job_duties = st.text_area("Job Duties", height=100)

# Video file uploader for MP4 videos
video_file = st.file_uploader("Upload a video (MP4 format)", type=["mp4"])

# Button to send compiled job description
if st.button("Send Compiled Job Description"):
    if job_title and department and expiry_date and job_location and job_type and job_qualifications and job_duties:
        jdw_graph_builder = graphbuilder()


        jdw_response = jdw_graph_builder.invoke({
            "job_title": job_title,
            "expected_start_date": datetime.today().strftime("%Y-%m-%d"),
            "job_type": job_type,
            "department": department,
            "expiry_date": expiry_date.strftime("%Y-%m-%d"),
            "job_duties": job_duties,
            "job_qualification": job_qualifications,
            "job_location": job_location
        })
        # compiled_data = compile_job_description(
        #     job_title, job_location, job_type, department, expiry_date, job_description
        # )
        # Text Area for Job Description
        st.text_area("Job Description", value=jdw_response.get("job_description"), height=200)

        st.success("Job Description Compiled Successfully!")
        st.text_area("Compiled Job Description", jdw_response, height=200)
    else:
        st.error("Please fill out all fields before submitting.")