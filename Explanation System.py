#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# Explanation System 
import streamlit as st
import pandas as pd
import hashlib
from inference_engine import CourseRecommendationEngine, Student, Course, Recommendation
from knowledge_base_editor import load_data, display_courses, display_courses_by_semester_and_year, add_course, edit_course, delete_course, save_to_file

# Set page configuration
st.set_page_config(page_title="AIU Course Management & Recommendation System", page_icon="📚", layout="wide")

# Custom CSS for styling
st.markdown(
    """
    <style>
    .sidebar .sidebar-content {
        background-color: #f0f2f6;
        padding: 20px;
    }
    .stApp {
        background-color: #ffffff;
    }
    .stCard {
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        padding: 20px;
        margin-bottom: 20px;
        background-color: #f9fbff;
    }
    .stButton>button {
        background-color: #ff6f61;
        color: white;
        border-radius: 10px;
        padding: 10px 20px;
        border: 2px solid #ff6f61;
    }
    .stButton>button:hover {
        background-color: #e65b52;
        border: 2px solid #e65b52;
    }
    .recommended-course {
        background-color: #e6f4ea;
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 5px;
    }
    .explanation-success {
        background-color: #e6f4ea;
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 5px;
    }
    .explanation-warning {
        background-color: #fff3cd;
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 5px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Initialize data in session_state
if 'courses_data' not in st.session_state:
    st.session_state.courses_data = load_data()
if st.session_state.courses_data is None:
    st.stop()

# Password authentication
def check_password():
    def password_entered():
        if hashlib.sha256(st.session_state["password"].encode()).hexdigest() == hashlib.sha256("admin123".encode()).hexdigest():
            st.session_state["password_correct"] = True
        else:
            st.session_state["password_correct"] = False
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False
    if not st.session_state["password_correct"]:
        with st.container():
            st.markdown("### 🔒 Admin Login")
            st.text_input("Enter Password", type="password", on_change=password_entered, key="password", help="Enter the password to access the system")
            if "password_correct" in st.session_state and not st.session_state["password_correct"]:
                st.error("😕 Incorrect Password")
        return False
    return True

def student_recommendation():
    course_codes = st.session_state.courses_data['Course Code'].tolist()
    with st.container():
        st.markdown('<div class="stCard">', unsafe_allow_html=True)
        st.subheader("Student Information")
        col1, col2 = st.columns(2)
        with col1:
            student_id = st.text_input("Student ID", value="")
            year = st.selectbox("Year", ["", 1, 2, 3, 4], index=0)
        with col2:
            cgpa = st.number_input("CGPA", min_value=0.0, max_value=4.0, step=0.1, value=0.0)
            completed_courses = st.multiselect("Completed Courses", course_codes, default=[])
        col3, col4 = st.columns(2)
        with col3:
            semester = st.selectbox("Semester", ["", "Fall", "Spring"], index=0)
        with col4:
            failed_courses = st.multiselect("Failed Courses (if any)", course_codes, default=[])
        st.markdown('</div>', unsafe_allow_html=True)
        if st.button("Get Recommendations"):
            errors = []
            if not student_id:
                errors.append("Student ID is required.")
            if not (0.0 <= cgpa <= 4.0):
                errors.append("CGPA must be between 0.0 and 4.0.")
            if semester not in ['Fall', 'Spring']:
                errors.append("Please select a semester ('Fall' or 'Spring').")
            if year not in [1, 2, 3, 4]:
                errors.append("Please select a year between 1 and 4.")
            completed_set = set(completed_courses)
            failed_set = set(failed_courses)
            overlapping_courses = completed_set.intersection(failed_set)
            if overlapping_courses:
                errors.append(f"Error: The following courses cannot be both completed and failed: {', '.join(overlapping_courses)}")
            invalid_failed = [course for course in failed_courses if course not in course_codes]
            invalid_completed = [course for course in completed_courses if course not in course_codes]
            if invalid_failed:
                errors.append(f"Invalid failed courses: {', '.join(invalid_failed)}")
            if invalid_completed:
                errors.append(f"Invalid completed courses: {', '.join(invalid_completed)}")
            if errors:
                for error in errors:
                    st.error(error)
            else:
                engine = CourseRecommendationEngine(st.session_state.courses_data)
                engine.reset()
                student_data = {
                    'student_id': student_id,
                    'cgpa': cgpa,
                    'completed_courses': ','.join(completed_courses) if completed_courses else '',
                    'failed_courses': ','.join(failed_courses) if failed_courses else '',
                    'semester': semester,
                    'year': year
                }
                engine.declare(Student(**student_data))
                for _, row in st.session_state.courses_data.iterrows():
                    course_code = row['Course Code']
                    semester_offered = row['Semester Offered'].strip()
                    course_year = int(row['Year'])
                    credits = float(row['Credit Hours'])
                    track = 'CS' if course_code.startswith('CSE') and course_code not in ['CSE493', 'CSE494'] else 'AI' if course_code.startswith('AIE') else 'Elective'
                    if course_code.startswith('UC') or course_code.startswith('UE'):
                        track = 'University'
                    engine.declare(Course(
                        course_id=course_code,
                        credits=credits,
                        prerequisites=row['Prerequisites'],
                        corequisites=row['Co-requisites'],
                        semester=semester_offered,
                        track=track,
                        year=course_year
                    ))
                engine.run()
                if failed_courses:
                    for course_id in failed_courses:
                        if course_id:
                            course = st.session_state.courses_data[st.session_state.courses_data['Course Code'] == course_id]
                            if not course.empty:
                                course = course.iloc[0]
                                if course['Semester Offered'].lower() != semester.lower() or course['Year'] > year:
                                    explanation = f"Note: Failed course {course_id} is not recommended in {semester} Year {year}. Retake it in {course['Semester Offered']} Year {course['Year']}."
                                    if explanation not in engine.explanation_set:
                                        engine.explanations.append(explanation)
                                        engine.explanation_set.add(explanation)
                recommended_courses = set(engine.recommendations)
                completed_courses_set = set(completed_courses)
                next_year = year + 1
                for _, row in st.session_state.courses_data.iterrows():
                    course_id = row['Course Code']
                    semester_offered = row['Semester Offered'].lower()
                    course_year = row['Year']
                    completed = completed_courses if completed_courses else []
                    prerequisites = row['Prerequisites']
                    if (course_id not in recommended_courses and 
                        course_id not in completed_courses_set and
                        (semester_offered != semester.lower() or course_year > year) and 
                        course_year <= next_year):
                        explanation = f"Not recommended for {course_id}: Not available in {semester} Year {year}, available in {row['Semester Offered']} Year {course_year}."
                        if explanation not in engine.explanation_set:
                            engine.explanations.append(explanation)
                            engine.explanation_set.add(explanation)
                    if (course_id not in recommended_courses and 
                        course_id not in completed_courses_set and
                        course_year <= year and
                        semester_offered == semester.lower()):
                        engine.prerequisites_met(prerequisites, completed, course_id)
                st.markdown('<div class="stCard">', unsafe_allow_html=True)
                st.subheader("Recommended Courses")
                if not engine.recommendations:
                    st.warning(f"No eligible courses for {semester} Year {year}.")
                else:
                    st.success(f"Total Credits: {engine.total_credits}")
                    for course_id in engine.recommendations:
                        course = st.session_state.courses_data[st.session_state.courses_data['Course Code'] == course_id].iloc[0]
                        st.markdown(
                            f'<div class="recommended-course">✔ Recommended {course_id} ({course["Credit Hours"]} credits, {course["Semester Offered"]} Year {course["Year"]})</div>',
                            unsafe_allow_html=True
                        )
                st.markdown('</div>', unsafe_allow_html=True)
                st.markdown('<div class="stCard">', unsafe_allow_html=True)
                st.subheader("Explanations")
                if not engine.explanations:
                    st.info("No explanations available.")
                else:
                    for explanation in engine.explanations:
                        if "Recommended" in explanation:
                            st.markdown(f'<div class="explanation-success">✅ {explanation}</div>', unsafe_allow_html=True)
                        else:
                            st.markdown(f'<div class="explanation-warning">⚠️ {explanation}</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

# Main function
def main():
    st.image("Aiu_logo.png", width=200)
    st.title("📚 AIU Course Management & Recommendation System")
    with st.sidebar:
        st.subheader("About the System")
        st.write("""
        This system assists in managing courses and recommending courses for students based on:
        - **Admin Mode**: Manage courses (view, add, edit, delete).
        - **Student Mode**: Recommendations based on CGPA, completed courses, failed courses, and semester.
        - **Credit Limits**: 22 for CGPA ≥3.5, 20 for CGPA 2.0–3.49, 13 for CGPA <2.0.
        - **Prerequisites**: Ensures prerequisites and co-requisites are met.
        """)
        mode = st.selectbox("Select Mode", ["Student Mode", "Admin Mode"], help="Choose between managing courses or getting recommendations")
    if mode == "Admin Mode":
        if not check_password():
            return
        menu = ["Display All Courses", "Filter by Semester/Year", "Add Course", "Edit Course", "Delete Course", "Save Changes"]
        choice = st.sidebar.selectbox("Menu", menu, help="Select an action to perform")
        if choice == "Display All Courses":
            display_courses()
        elif choice == "Filter by Semester/Year":
            display_courses_by_semester_and_year()
        elif choice == "Add Course":
            add_course()
        elif choice == "Edit Course":
            edit_course()
        elif choice == "Delete Course":
            delete_course()
        elif choice == "Save Changes":
            save_to_file()
    else:
        student_recommendation()

if __name__ == "__main__":
    main()

