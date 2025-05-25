#!/usr/bin/env python
# coding: utf-8

# In[ ]:


get_ipython().system('pip install streamlit')
get_ipython().system('pip install pandas')
get_ipython().system('pip install experta')


# In[ ]:


#The full code
import streamlit as st
import pandas as pd
import hashlib
from experta import *

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
        margin-bottom: 5px мегабайт;
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

# Load data
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("Corrected_CSE_Courses3ver2.csv")
        required_columns = ['Course Code', 'Course Name', 'Credit Hours', 'Semester Offered', 'Year', 'Prerequisites', 'Co-requisites']
        if not all(col in df.columns for col in required_columns):
            st.error("CSV file is missing required columns.")
            return None
        df['Prerequisites'] = df['Prerequisites'].fillna('')
        df['Co-requisites'] = df['Co-requisites'].fillna('')
        return df
    except FileNotFoundError:
        st.error("Could not find 'Corrected_CSE_Courses3ver2.csv'. Please ensure the file is in the same directory.")
        return None
    except Exception as e:
        st.error(f"Error loading CSV file: {str(e)}")
        return None

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

# Admin Functions
def display_courses():
    with st.container():
        st.markdown("### 📋 Display All Courses")
        st.write("View the complete list of courses in the system.")
        st.dataframe(
            st.session_state.courses_data[['Course Code', 'Course Name', 'Credit Hours', 'Semester Offered', 'Year']],
            use_container_width=True,
            column_config={
                "Course Code": st.column_config.TextColumn("Code", width="small"),
                "Course Name": st.column_config.TextColumn("Name", width="medium"),
                "Credit Hours": st.column_config.NumberColumn("Credits", format="%d"),
                "Semester Offered": st.column_config.TextColumn("Semester", width="small"),
                "Year": st.column_config.NumberColumn("Year", format="%d")
            }
        )

def display_courses_by_semester_and_year():
    with st.container():
        st.markdown("### 📅 Filter Courses")
        st.write("Filter courses by semester and/or academic year.")
        with st.expander("Filter Options", expanded=True):
            semester = st.selectbox("Select Semester", ["Fall", "Spring", "Both"], help="Choose a semester to filter courses")
            year_input = st.text_input("Enter Academic Year (1-4, or leave blank for all years)", help="Enter a year between 1 and 4")
            filtered = st.session_state.courses_data.copy()
            if semester != 'Both':
                filtered = filtered[filtered['Semester Offered'].str.contains(semester, case=False, na=False)]
            if year_input and year_input.isdigit():
                year = int(year_input)
                filtered = filtered[filtered['Year'] == year]
            if filtered.empty:
                st.warning(f"No courses available for {semester} in Year {year_input or 'all years'}")
            else:
                st.write(f"Courses available for {semester} - Year {year_input or 'all years'}:")
                st.dataframe(
                    filtered[['Course Code', 'Course Name', 'Credit Hours', 'Semester Offered', 'Year', 'Prerequisites', 'Co-requisites']],
                    use_container_width=True,
                    column_config={
                        "Course Code": st.column_config.TextColumn("Code", width="small"),
                        "Course Name": st.column_config.TextColumn("Name", width="medium"),
                        "Credit Hours": st.column_config.NumberColumn("Credits", format="%d"),
                        "Semester Offered": st.column_config.TextColumn("Semester", width="small"),
                        "Year": st.column_config.NumberColumn("Year", format="%d"),
                        "Prerequisites": st.column_config.TextColumn("Prerequisites", width="medium"),
                        "Co-requisites": st.column_config.TextColumn("Co-requisites", width="medium")
                    }
                )

def add_course():
    with st.container():
        st.markdown("### ➕ Add New Course")
        st.write("Fill in the details to add a new course to the system.")
        with st.form("add_course_form"):
            code = st.text_input("Course Code", help="Enter the course code (e.g., CS301)")
            name = st.text_input("Course Name", help="Enter the full course name")
            desc = st.text_input("Description", help="Provide a brief course description")
            prereq = st.text_input("Prerequisites (comma-separated)", help="Enter course codes for prerequisites, separated by commas")
            coreq = st.text_input("Co-requisites (comma-separated)", help="Enter course codes for co-requisites, separated by commas")
            credits = st.number_input("Credit Hours", min_value=1, max_value=10, step=1, help="Enter credit hours (1-10)")
            semester = st.selectbox("Semester Offered", ["Fall", "Spring", "Both"], help="Choose when the course is offered")
            year = st.number_input("Year (1-4)", min_value=1, max_value=4, step=1, help="Enter the academic year (1-4)")
            submit = st.form_submit_button("Add Course")
            if submit:
                courses_data = st.session_state.courses_data
                if code in courses_data['Course Code'].values:
                    st.error("❌ Course already exists")
                    return
                all_codes = set(courses_data['Course Code'].dropna())
                invalid_prereq = [p for p in prereq.split(',') if p and p.strip() not in all_codes]
                invalid_coreq = [c for c in coreq.split(',') if c and c.strip() not in all_codes]
                if invalid_prereq:
                    st.error(f"❌ Invalid prerequisites: {', '.join(invalid_prereq)}")
                    return
                if invalid_coreq:
                    st.error(f"❌ Invalid co-requisites: {', '.join(invalid_coreq)}")
                    return
                new_row = {
                    'Course Code': code,
                    'Course Name': name,
                    'Description': desc,
                    'Prerequisites': prereq if prereq else None,
                    'Co-requisites': coreq if coreq else None,
                    'Credit Hours': credits,
                    'Semester Offered': semester,
                    'Year': year
                }
                st.session_state.courses_data = pd.concat([courses_data, pd.DataFrame([new_row])], ignore_index=True)
                st.success(f"✅ Course added: {code} - {name}")

def edit_course():
    with st.container():
        st.markdown("### 🔄 Edit Course")
        st.write("Select a course to edit its details.")
        courses_data = st.session_state.courses_data
        course_code = st.selectbox("Select Course Code to Edit", courses_data['Course Code'], help="Choose a course to edit")
        if course_code:
            idx = courses_data[courses_data['Course Code'] == course_code].index[0]
            with st.form("edit_course_form"):
                name = st.text_input("Course Name", value=courses_data.at[idx, 'Course Name'], help="Update the course name")
                desc = st.text_input("Description", value=courses_data.at[idx, 'Description'] or "", help="Update the course description")
                prereq = st.text_input("Prerequisites (comma-separated)", value=courses_data.at[idx, 'Prerequisites'] or "", help="Update prerequisites")
                coreq = st.text_input("Co-requisites (comma-separated)", value=courses_data.at[idx, 'Co-requisites'] or "", help="Update co-requisites")
                credits = st.number_input("Credit Hours", min_value=1, max_value=10, value=int(courses_data.at[idx, 'Credit Hours']), help="Update credit hours (1-10)")
                current_semester = courses_data.at[idx, 'Semester Offered']
                semester = st.selectbox("Semester Offered", ["Fall", "Spring", "Both"], index=["Fall", "Spring", "Both"].index(current_semester), help="Update the semester")
                submit = st.form_submit_button("Update Course")
                if submit:
                    st.session_state.courses_data.at[idx, 'Course Name'] = name
                    st.session_state.courses_data.at[idx, 'Description'] = desc
                    st.session_state.courses_data.at[idx, 'Prerequisites'] = prereq if prereq else None
                    st.session_state.courses_data.at[idx, 'Co-requisites'] = coreq if coreq else None
                    st.session_state.courses_data.at[idx, 'Credit Hours'] = credits
                    st.session_state.courses_data.at[idx, 'Semester Offered'] = semester
                    st.success(f"✅ Course updated: {course_code}")

def delete_course():
    with st.container():
        st.markdown("### 🗑 Delete Course")
        st.write("Select a course to remove from the system.")
        courses_data = st.session_state.courses_data
        course_code = st.selectbox("Select Course Code to Delete", courses_data['Course Code'], help="Choose a course to delete")
        if st.button("Delete Course", type="primary"):
            if course_code in courses_data['Course Code'].values:
                st.session_state.courses_data = courses_data[courses_data['Course Code'] != course_code]
                st.success(f"✅ Course deleted: {course_code}")
            else:
                st.error("❌ Course not found")

def save_to_file():
    with st.container():
        st.markdown("### 💾 Save Changes")
        st.write("Save all changes to a new CSV file.")
        filename = "Corrected_CSE_Courses3ver2_UPDATED.csv"
        if st.button("Save to File", type="primary"):
            st.session_state.courses_data.to_csv(filename, index=False)
            st.success(f"💾 Data saved to {filename}")

# Student Recommendation Functions
class Student(Fact):
    """Student Information"""
    pass

class Course(Fact):
    """Course Information"""
    pass

class Recommendation(Fact):
    """Recommended Courses"""
    pass

class CourseRecommendationEngine(KnowledgeEngine):
    def __init__(self, courses_df):
        super().__init__()
        self.recommendations = []
        self.explanations = []
        self.explanation_set = set()
        self.total_credits = 0
        self.max_credits = 0
        self.courses_df = courses_df
        self.failed_course_warnings = []

    def prerequisites_met(self, course_prereqs, completed_courses, course_id):
        if not course_prereqs or course_prereqs == "SENIOR STANDING":
            if course_prereqs == "SENIOR STANDING":
                if not self.has_senior_standing(completed_courses):
                    explanation = f"Not recommended for {course_id}: Requires senior standing (90+ credits)."
                    if explanation not in self.explanation_set:
                        self.explanations.append(explanation)
                        self.explanation_set.add(explanation)
                    return False
                return True
            return True
        prereqs = course_prereqs.replace(' AND ', ',').split(',')
        met = all(prereq.strip() in completed_courses for prereq in prereqs)
        if not met:
            explanation = f"Not recommended for {course_id}: Prerequisites not met ({course_prereqs})."
            if explanation not in self.explanation_set:
                self.explanations.append(explanation)
                self.explanation_set.add(explanation)
        return met

    def corequisites_satisfied(self, course_coreqs, completed_courses, current_recommendations, course_id):
        if not course_coreqs:
            return True
        coreqs = course_coreqs.split(',')
        satisfied = all(coreq.strip() in completed_courses or coreq.strip() in current_recommendations for coreq in coreqs)
        if not satisfied:
            explanation = f"Not recommended for {course_id}: Co-requisites not met ({course_coreqs})."
            if explanation not in self.explanation_set:
                self.explanations.append(explanation)
                self.explanation_set.add(explanation)
        return satisfied

    def has_senior_standing(self, completed_courses):
        total_completed_credits = 0
        for course_id in completed_courses:
            course = self.courses_df[self.courses_df['Course Code'] == course_id]
            if not course.empty:
                total_completed_credits += course.iloc[0]['Credit Hours']
        return total_completed_credits >= 90

    @Rule(Student(cgpa=GE(3.5)), salience=100)
    def set_credit_limit_overload(self):
        self.max_credits = 22
        self.explanations.append("Credit limit set to 22 (overload) because CGPA ≥ 3.5.")
        self.explanation_set.add("Credit limit set to 22 (overload) because CGPA ≥ 3.5.")

    @Rule(Student(cgpa=GE(2.0) & LT(3.5)), salience=100)
    def set_credit_limit_full_load(self):
        self.max_credits = 20
        self.explanations.append("Credit limit set to 20 (full load) because 2.0 ≤ CGPA < 3.5.")
        self.explanation_set.add("Credit limit set to 20 (full load) because 2.0 ≤ CGPA < 3.5.")

    @Rule(Student(cgpa=LT(2.0)), salience=100)
    def set_credit_limit_half_load(self):
        self.max_credits = 13
        self.explanations.append("Credit limit set to 13 (half load) because CGPA < 2.0.")
        self.explanation_set.add("Credit limit set to 13 (half load) because CGPA < 2.0.")

    @Rule(AS.student << Student(failed_courses=MATCH.failed, completed_courses=MATCH.completed, year=MATCH.student_year, semester=MATCH.semester),
          AS.course << Course(course_id=MATCH.course_id,
                             prerequisites=MATCH.prereqs,
                             corequisites=MATCH.coreqs,
                             semester=MATCH.course_semester,
                             credits=MATCH.credits,
                             year=MATCH.course_year),
          TEST(lambda failed, course_id: failed and course_id in failed.split(',')),
          TEST(lambda course_semester, semester: course_semester.lower() == semester.lower().strip()),
          TEST(lambda student_year, course_year: course_year <= student_year),
          TEST(lambda completed, course_id: not completed or course_id not in completed.split(',')),
          salience=20)
    def recommend_failed_course(self, student, course_id, prereqs, coreqs, credits):
        completed = student['completed_courses'].split(',') if student['completed_courses'] else []
        if self.prerequisites_met(prereqs, completed, course_id) and self.corequisites_satisfied(coreqs, completed, self.recommendations, course_id):
            if self.total_credits + credits <= self.max_credits:
                self.recommendations.append(course_id)
                self.total_credits += credits
                self.declare(Recommendation(course_id=course_id))
                explanation = f"Recommended {course_id} because you failed it previously and all prerequisites and co-requisites are met."
                self.explanations.append(explanation)
                self.explanation_set.add(explanation)
            else:
                explanation = f"Not recommended for {course_id}: Exceeds credit limit of {self.max_credits} credits."
                if explanation not in self.explanation_set:
                    self.explanations.append(explanation)
                    self.explanation_set.add(explanation)

    @Rule(AS.student << Student(completed_courses=MATCH.completed, year=MATCH.student_year, semester=MATCH.semester),
          AS.course << Course(course_id=MATCH.course_id,
                             prerequisites=MATCH.prereqs,
                             corequisites=MATCH.coreqs,
                             semester=MATCH.course_semester,
                             track='CS',
                             credits=MATCH.credits,
                             year=MATCH.course_year),
          NOT(Recommendation(course_id=MATCH.course_id)),
          TEST(lambda course_semester, semester: course_semester.lower() == semester.lower().strip()),
          TEST(lambda student_year, course_year: course_year <= student_year),
          TEST(lambda completed, course_id: not completed or course_id not in completed.split(',')),
          salience=15)
    def recommend_core_cs_course(self, student, course_id, prereqs, coreqs, credits):
        completed = student['completed_courses'].split(',') if student['completed_courses'] else []
        if self.prerequisites_met(prereqs, completed, course_id) and self.corequisites_satisfied(coreqs, completed, self.recommendations, course_id):
            if course_id in ['CSE493', 'CSE494'] and not self.has_senior_standing(completed):
                explanation = f"Not recommended for {course_id}: Requires senior standing (90+ credits)."
                if explanation not in self.explanation_set:
                    self.explanations.append(explanation)
                    self.explanation_set.add(explanation)
                return
            if self.total_credits + credits <= self.max_credits:
                self.recommendations.append(course_id)
                self.total_credits += credits
                self.declare(Recommendation(course_id=course_id))
                explanation = f"Recommended {course_id} as a core Computer Science course because all prerequisites and co-requisites are met."
                self.explanations.append(explanation)
                self.explanation_set.add(explanation)
            else:
                explanation = f"Not recommended for {course_id}: Exceeds credit limit of {self.max_credits} credits."
                if explanation not in self.explanation_set:
                    self.explanations.append(explanation)
                    self.explanation_set.add(explanation)

    @Rule(AS.student << Student(completed_courses=MATCH.completed, year=MATCH.student_year, semester=MATCH.semester),
          AS.course << Course(course_id=MATCH.course_id,
                             prerequisites=MATCH.prereqs,
                             corequisites=MATCH.coreqs,
                             semester=MATCH.course_semester,
                             credits=MATCH.credits,
                             year=MATCH.course_year),
          NOT(Recommendation(course_id=MATCH.course_id)),
          TEST(lambda course_semester, semester: course_semester.lower() == semester.lower().strip()),
          TEST(lambda student_year, course_year: course_year <= student_year),
          TEST(lambda completed, course_id: not completed or course_id not in completed.split(',')))
    def recommend_other_course(self, student, course_id, prereqs, coreqs, credits):
        completed = student['completed_courses'].split(',') if student['completed_courses'] else []
        if self.prerequisites_met(prereqs, completed, course_id) and self.corequisites_satisfied(coreqs, completed, self.recommendations, course_id):
            if self.total_credits + credits <= self.max_credits:
                self.recommendations.append(course_id)
                self.total_credits += credits
                self.declare(Recommendation(course_id=course_id))
                explanation = f"Recommended {course_id} because all prerequisites and co-requisites are met."
                self.explanations.append(explanation)
                self.explanation_set.add(explanation)
            else:
                explanation = f"Not recommended for {course_id}: Exceeds credit limit of {self.max_credits} credits."
                if explanation not in self.explanation_set:
                    self.explanations.append(explanation)
                    self.explanation_set.add(explanation)

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

