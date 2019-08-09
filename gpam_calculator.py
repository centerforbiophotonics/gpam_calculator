"""
A program to calculate all of the GPAM and TERM_GPAM of students within a CSV depending on the term they were enrolled.
When running this file, two arugments need to be passed. A CSV that contains a list of students that were
admitted after a certain year and a CSV that contains a list of the grades students obtained for all of their courses.

The program should be run in the following format (order of files passed in does matter): 
"python3 gpam_calculator.py FILENAME_ADMITTED.csv FILENAME_COURSES.csv"

The first file should contain "PIDM" and "TERM" columns. The second file should contain "PIDM", "TERM", "CRSE", "CLASS_ID",
"UNITS", "GRADE", "GRADE_PT" columns. Order of the columns does not matter.
"""

# https://www.insidehighered.com/views/2019/05/07/advice-improving-gpa-and-how-its-interpreted-opinion

# GPAM = (Sum of Median Grades of Classes Taken, Weighted by Units)/Sum of Total Units Taken
# cumulative (entire academic history) and per term (quarters) and per year (or they can select)

import csv
import statistics
import pandas as pd
import unittest
import sys

class GPAM:

	admittance_data = ''	
	course_data = ''		
	course_rows = []		
	admittance_rows = []	
	medians = []
	sorted_rows = {}
	
	def __init__(self):
		"""
		Constructor method. Runs first when the GPAM class object is created.
		Initializes globla variables. Admittance_data and course_data will contain
		references to the csvs. course_rows and admittance_rows will be lists of
		the rows of data from the csvs. course_rows will be sorted by pidm.
		subject_rows will be similar to course_rows but sorted by subject.
		"""
		global admittance_data
		global course_data
		global course_rows
		global admittance_rows	
		global medians
		global sorted_rows

		sorted_rows = {}
		assert(len(sys.argv) > 2), "Did not pass admittance CSV and course CSV"
		admittance_data = sys.argv[1]	
		course_data = sys.argv[2]	
		course_rows = self.retrieve_and_sort_rows(course_data)	
		admittance_rows = self.retrieve_rows(admittance_data)	

		medians = []	
		try:
			medians = self.retrieve_rows('course_medians.csv')
		except FileNotFoundError:	
			self.calculate_medians()	
		print("Initialization completed. Press control+c to exit program and save progress.")

	"""
	Calculates the GPAM of a student.
	Parameter is the student's student id passed in as a string.
	Returns the gpam as a float.
	"""
	def gpam(self, pidm, term=None):

		num_units = 0
		courses_completed = []

		courses_taken = sorted_rows[pidm]	

		if term != None:
			for row in courses_taken:	
				if row["\"TERM\""] == term:	
					num_units += float(row["\"UNITS\""])	
				if row["\"TERM\""] == term and row["\"GRADE_PT\""] != "\"\"":	
					courses_completed.append(row)	
		else:
			for row in courses_taken:	
				num_units += float(row["\"UNITS\""])
				if row["\"GRADE_PT\""] != "\"\"": 
					courses_completed.append(row)

		sum_of_medians = self.get_sum_of_medians(courses_completed) # Add all of the medians together
		
		gpam = sum_of_medians/num_units # GPAM formula
		gpam = round(gpam, 2) # Round the GPAM to two decimal places

		return gpam

	"""
	Checks to see if student was admitted after fall 2008.
	Returns boolean found_pidm, True if pidm was found. 
	"""	
	def verify_admittance(self, pidm):
		global admittance_rows
		found_pidm = False
		
		for row in admittance_rows:
			if row["\"PIDM\""] == pidm:
				found_pidm = True

		return found_pidm

	"""
	Calculates the median of a course for a specific quarter given its term, subject, course, and class id.
	Returns median as a grade point.
	"""
	def calc_median(self, term, subj, crse, class_id):
		median = 0
		term_grades_for_course = [] # List of grades for the course that matches the given term, subject, course, and class id
		
		for row in course_rows:
			if row["\"GRADE_PT\""] != "\"\"" and row["\"TERM\""] == term and row["\"SUBJ\""] == subj and row["\"CRSE\""] == crse and row["\"CLASS_ID\""] == class_id:
				term_grades_for_course.append(float(row["\"GRADE_PT\""]))
		
		if not term_grades_for_course: 
			return 0
		else:	
			median = statistics.median(term_grades_for_course)
			return median

	"""
	Read through the data from the courses and grades CSV and calculates the median of every course for every term.
	When a course that already has its median calculated is encountered, the program will skip to the next course in line.
	Once all of the courses have had their medians calculated, a course_medians.csv will either be generated or updated.
	By pressing control+C, the user can exit the program and the course_medians.csv will be either generated or updated.
	"""
	def calculate_medians(self):
		global medians 
		try:
			for row in course_rows:
				if any(dct["TERM"] == row["\"TERM\""] and dct["SUBJ"] == row["\"SUBJ\""] and dct["CRSE"] == row["\"CRSE\""] and dct["CLASS_ID"] == row["\"CLASS_ID\""] for dct in medians):
					print("Already calculated. Continuing")
					continue	
				median = self.calc_median(row["\"TERM\""], row["\"SUBJ\""], row["\"CRSE\""], row["\"CLASS_ID\""])
				course_median = {}	
				course_median.update({"TERM": row["\"TERM\""], "SUBJ": row["\"SUBJ\""], "CRSE": row["\"CRSE\""], "CLASS_ID": row["\"CLASS_ID\""], "MEDIAN": median})
				print("Finished calculating")
				print("Adding new...")
				medians.append(course_median)	
			df_list = []
			for dct in medians:
				df_list.append(pd.DataFrame([dct], columns = ["TERM", "SUBJ", "CRSE", "CLASS_ID", "MEDIAN"]))
			df = pd.concat(df_list)	
			df.to_csv("course_medians.csv", index=False, quoting=csv.QUOTE_NONE)
		except KeyboardInterrupt:	
			df_list = []
			for dct in medians:
				df_list.append(pd.DataFrame([dct], columns = ["TERM", "SUBJ", "CRSE", "CLASS_ID", "MEDIAN"]))
			df = pd.concat(df_list)
			df.to_csv("course_medians.csv", index=False, quoting=csv.QUOTE_NONE)

	"""
	Gets the sum of the median grade of each course weighted by the units each course is worth.
	Median grade for one course is multiplied by the units the course is worth.
	Parameter courses_completed is a list of courses as a string that a student has completed. 
	Returns the sum of the medians as a float: median of course * units of the course 
	"""
	def get_sum_of_medians(self, courses_completed):

		sum_of_medians = 0

		for row in courses_completed:
			median_grade = None
			for dct in medians:
				if dct["TERM"] == row["\"TERM\""] and dct["SUBJ"] == row["\"SUBJ\""] and dct["CRSE"] == row["\"CRSE\""] and dct["CLASS_ID"] == row["\"CLASS_ID\""]:
					median_grade = dct["MEDIAN"]
			assert(median_grade != None)
			sum_of_medians += float(median_grade) * int(row["\"UNITS\""])

		return sum_of_medians

	"""
	Reads CSV file and stores its contents within a list of dictionaries with the column names as keys.
	Returns the list of dictionaries. 
	"""
	def retrieve_rows(self, file_data):

		rows = [] 

		with open(file_data, 'r') as csvFile:	
			csv_reader = csv.DictReader(csvFile, delimiter=',', quotechar="'", quoting=csv.QUOTE_MINIMAL)
			for row in csv_reader:	
				rows.append(row)
			csvFile.close()
		return rows

	"""
	Reads CSV file and stores its contents within a list of dictionaries with the column names as keys.
	Additionally, also updates a dictionary to map all of the courses a student took to the students ID. 
	Returns the list of dictionaries. 
	"""
	def retrieve_and_sort_rows(self, file_data):
		global sorted_rows
		rows = []
		with open(file_data, 'r') as csvFile:	
			csv_reader = csv.DictReader(csvFile, delimiter=',', quotechar="'", quoting=csv.QUOTE_MINIMAL)
			for row in csv_reader:	
				rows.append(row)
				try:	
					sorted_rows[row["\"PIDM\""]].append(row)	
				except KeyError:
					sorted_rows.update({row["\"PIDM\""]: [row]})
			csvFile.close()
		return rows


	"""
	Updates the course_data csv file with the calculated GPAM. It will update either the cummulative
	GPAM or the TERM_GPAM. Uses pandas module to search and insert values into the csv.
	Parameters are strings for pidm, gpam, and the term.
	"""
	def update_gpam(self, pidm, df, gpam, term=None):
		
		if term != None:
			print("Updating: PIDM-" + pidm + " TERM_GPAM-" + str(gpam))
			df.loc[(df.PIDM.isin([pidm])) & (df.TERM.isin([term])), "TERM_GPAM"] = gpam

		else:
			print("Updating: PIDM-" + pidm + " GPAM-" + str(gpam))
			df.loc[df.PIDM.isin([pidm]), "GPAM"] = gpam


	
	def main(self):
		global course_rows

		found_pidm = False
		previous_pidm = 0
		previous_terms = []

		df = pd.read_csv(course_data) 
		df["UNITS"] = df["UNITS"].astype(int)	
	
		try:
			for row in course_rows:
				pidm = row["\"PIDM\""]
				term = row["\"TERM\""]

				if previous_pidm != pidm:	
					found_pidm = self.verify_admittance(pidm)	
					print("PIDM: " + pidm + " is " + str(found_pidm))
					previous_pidm = pidm
					previous_terms = []

				if previous_pidm == pidm and term in previous_terms:
					continue	
				else:
					previous_terms.append(term)	
				
				try:
					assert(found_pidm is True), "The pidm could not be found."
				except AssertionError: 
					continue	
				
				try:
					if row["\"GPAM\""] == "\"\"":	
						print("calculating GPAM...")
						gpam = self.gpam(pidm)
						print("GPAM is " + str(gpam) + " " + str(pidm))
						self.update_gpam(pidm, df, gpam)	
					
					if row["\"TERM_GPAM\""] == "\"\"":	
						print("calculating TERM_GPAM...")
						term_gpam = self.gpam(pidm, term)
						print("TERM_GPAM is " + str(term_gpam) + " " + str(pidm) + " Term: " + str(term))
						self.update_gpam(pidm, df, term_gpam, term)	

				except IndexError:	
					print("Missing column") 

					print("calculating GPAM...")
					gpam = self.gpam(pidm)
					print("GPAM is " + str(gpam) + " " + str(pidm))
					self.update_gpam(pidm, df, gpam)

					print("calculating TERM_GPAM...")
					term_gpam = self.gpam(pidm, term)
					print("TERM_GPAM is " + str(term_gpam) + " " + str(pidm) + " Term: " + str(term))
					self.update_gpam(pidm, df, term_gpam, term)

				except ZeroDivisionError:	
					print("Zero units being divided.")
					continue
			print("Finished") 

		except KeyboardInterrupt: 
			sys.exit(0)	

if __name__ == "__main__":
    gpam_obj = GPAM()	
    gpam_obj.main()		
