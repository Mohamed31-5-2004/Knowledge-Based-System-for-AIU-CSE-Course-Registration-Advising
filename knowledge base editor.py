#!/usr/bin/env python
# coding: utf-8

# In[1]:


# knowledge_base_editor.py 
import streamlit as st
import pandas as pd

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


# In[ ]:




