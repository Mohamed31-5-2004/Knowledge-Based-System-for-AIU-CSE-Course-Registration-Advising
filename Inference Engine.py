#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# inference engine code 
get_ipython().system('pip install experta')
from experta import *

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

