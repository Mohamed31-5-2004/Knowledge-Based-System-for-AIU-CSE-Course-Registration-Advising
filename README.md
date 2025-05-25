# 📚 AIU Academic Course Management & Recommendation System

![Logo](Final%20logo-01-small.png)

Welcome to the AIU Academic Course Management and Recommendation System, a Streamlit-based web application designed to help both administrators and students manage and select courses effectively. The system provides an intuitive interface for managing course data and a rule-based engine for personalized student course recommendations.

---

## Table of Contents

- [Features](#features)
- [Demo](#demo)
- [Getting Started](#getting-started)
- [Usage](#usage)
  - [Admin Mode](#admin-mode)
  - [Student Mode](#student-mode)
- [Recommendation Engine](#recommendation-engine)
- [Customization](#customization)
- [Dependencies](#dependencies)
- [License](#license)

---

## Features

- **Admin Mode**
  - View all courses
  - Filter courses by semester and year
  - Add new courses
  - Edit existing courses
  - Delete courses
  - Save course data to a CSV file
  - Password-protected access

- **Student Mode**
  - Receive course recommendations based on your:
    - CGPA
    - Completed courses
    - Failed courses
    - Academic year and semester
  - See explanations for recommendations and restrictions
  - Credit hour limits enforced based on CGPA

- **User Interface**
  - Stylish, responsive layout with custom CSS
  - Sidebar for navigation and system information

---

## Demo

<img src="MyIC_Article122529.png" width="600"/>

---

## Getting Started

### Prerequisites

- Python 3.8+
- [Streamlit](https://streamlit.io/)
- [pandas](https://pandas.pydata.org/)
- [experta](https://github.com/noxdafox/experta)

### Installation

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd <repo-folder>
   ```

2. **Install dependencies:**
   ```bash
   pip install streamlit pandas experta
   ```

3. **Prepare data files:**
   - Ensure `Corrected_CSE_Courses3ver2.csv` is present in the root directory.
   - Add images (`Final logo-01-small.png`, `MyIC_Article122529.png`) to the root directory for full UI experience.

4. **Run the application:**
   ```bash
   streamlit run <your_main_python_file>.py
   ```

---

## Usage

### Admin Mode

- **Access:** Select "Admin Mode" from the sidebar. Enter the admin password (`admin123` by default).
- **Features:**
  - **Display All Courses:** View all course data.
  - **Filter by Semester/Year:** View courses filtered by semester and/or academic year.
  - **Add Course:** Input new course details, with validation for prerequisites and co-requisites.
  - **Edit Course:** Update existing course information.
  - **Delete Course:** Remove a course from the database.
  - **Save Changes:** Export the current course list to a new CSV file.

### Student Mode

- **Access:** Select "Student Mode" from the sidebar.
- **Input:**
  - Student ID
  - Academic Year (1-4)
  - CGPA (0.0 - 4.0)
  - Completed Courses
  - Failed Courses
  - Semester (Fall/Spring)
- **Output:**
  - Personalized course recommendations
  - Total credit hours for recommended courses
  - Detailed explanations for each recommendation or restriction

---

## Recommendation Engine

The system uses an **expert system (rule-based engine)** via the [experta](https://github.com/noxdafox/experta) library to:

- Apply credit limits based on CGPA:
  - **CGPA ≥ 3.5:** Up to 22 credit hours
  - **2.0 ≤ CGPA < 3.5:** Up to 20 credit hours
  - **CGPA < 2.0:** Up to 13 credit hours
- Recommend courses only if prerequisites and co-requisites are satisfied
- Ensure failed courses are prioritized for retake if eligible
- Provide explanations for all recommendations and restrictions

---

## Customization

- **Course Data:** Edit or replace `Corrected_CSE_Courses3ver2.csv` with your institution's course list.
- **Admin Password:** Change the password by updating the `admin123` string in the `check_password` function.
- **Styling:** Modify custom CSS in the code for UI enhancements.

---

## Dependencies

- [Streamlit](https://streamlit.io/) - Web app framework
- [pandas](https://pandas.pydata.org/) - Data manipulation
- [experta](https://github.com/noxdafox/experta) - Rule-based expert system
- [hashlib](https://docs.python.org/3/library/hashlib.html) - Password security

Install all dependencies via:
```bash
pip install streamlit pandas experta
```

---

## License

This project is for academic and demonstration purposes. Please contact the author for reuse or adaptation.

---

## Acknowledgements

- AIU (Arab International University)
- [Streamlit](https://streamlit.io/)
- [Experta](https://github.com/noxdafox/experta)
