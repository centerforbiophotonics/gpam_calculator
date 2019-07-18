# https://www.insidehighered.com/views/2019/05/07/advice-improving-gpa-and-how-its-interpreted-opinion

# GPAM = (Sum of Median Grades of Classes Taken, Weighted by Units)/Sum of Total Units Taken
# cumulative (entire academic history) and per term (quarters) and per year (or they can select)

# TODO: unit test
# TODO: put binary in separate function and clean up/optimize code

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
	subject_rows = []

	"""
	Constructor method. Runs first when the GPAM class object is created.
	Initializes globla variables. Admittance_data and course_data will contain
	references to the csvs. course_rows and admittance_rows will be lists of
	the rows of data from the csvs. course_rows will be sorted by pidm.
	subject_rows will be similar to course_rows but sorted by subject.
	"""
	def __init__(self):
		global admittance_data
		global course_data
		global course_rows
		global admittance_rows
		global subject_rows
		admittance_data = 'FILENAME_ADMITTED.csv'
		course_data = 'FILENAME_COURSES.csv'
		course_rows = self.retrieve_rows()
		admittance_rows = self.retrieve_admittance_rows()
		admittance_rows.pop(0)
		course_rows.pop(0)	#don't need the headers for the sort so remove them
		admittance_rows = sorted(admittance_rows, key = lambda x: x[0])
		course_rows = sorted(course_rows, key = lambda x: x[0])	#sorts the list in ascending order
		subject_rows = sorted(course_rows, key = lambda x: x[2])

		print("Initialization completed. Press control+c to exit program and save progress.")

	"""
	Calculates the GPAM of a student.
	Parameter is the student's student id passed in as a string.
	Returns the gpam as a float.
	"""
	def gpam(self, pidm, term=None):

		# Verify student was admitted after 2008 before calculating GPAM
		#found_pidm = self.verify_admittance(pidm)
		#assert(found_pidm is True), "The pidm could not be found."

		# Begin calculating GPAM
		if term != None:
			rows = self.retrieve_rows_term(pidm, term) # Obtain courses taken by student
		else:
			rows = self.retrieve_rows(pidm)
		num_units = 0
		courses_completed = []

		if term != None:
			for row in rows:
				if row[1] == term:
					num_units += float(row[5])
				if row[1] == term and row[7] is not '':	# Omit courses with no grade
					courses_completed.append(row)
		else:
			for row in rows:
				num_units += float(row[5])
				if row[7] is not '': # Omit courses with no grade
					courses_completed.append(row)



		sum_of_medians = self.get_sum_of_medians(courses_completed) # Add all of the medians together
		
		gpam = sum_of_medians/num_units # GPAM formula
		gpam = round(gpam, 2) # Round the GPAM to two decimal places

		return gpam

	"""
	Checks to see if student was admitted after fall 2008.
	"""
	def verify_admittance(self, pidm):
		global admittance_rows
		found_pidm = False
		
		"""
		for row in admittance_rows:
			if row[0] == pidm:
				found_pidm = True
				index = admittance_rows.index(row)
				print("Found at " + str(index)) # Linear
		"""

		left_index = 0
		right_index = len(admittance_rows) - 1
		mid_index = 0

		while left_index <= right_index:
			mid_index = (left_index + right_index) // 2

			if admittance_rows[mid_index][0] == pidm:
				found_pidm = True
				#index = admittance_rows.index(row)
				print("Found at " + str(mid_index)) # Binary
				break
			elif admittance_rows[mid_index][0] < pidm:
				left_index = mid_index + 1
			else:
				right_index = mid_index - 1

		return found_pidm


	"""
	Calculates the median of a course for a specific quarter given its term, subject, course, and class id.
	Returns median as a grade point.
	"""
	def calc_median(self, term, subj, crse, class_id):
		global course_rows
		global subject_rows
		median = 0
		term_grades_for_course = [] # List of grades for the course that matches the given term, subject, course, and class id
		

		# Binary Search for the courses

		left_index = 0
		right_index = len(subject_rows) - 1
		mid_index = 0

		while left_index <= right_index:
			mid_index = (left_index + right_index) // 2

			if subject_rows[mid_index][2] == subj:
				#print("Found midpoint at " + str(mid_index))
				if subject_rows[mid_index][7] is not "" and subject_rows[mid_index][7] != "\"\"" and subject_rows[mid_index][1].lower() == term.lower() and \
				subject_rows[mid_index][3].lower() == crse.lower() and subject_rows[mid_index][4].lower() == class_id.lower():
					term_grades_for_course.append(float(subject_rows[mid_index][7]))
				break
			elif subject_rows[mid_index][2] < subj:
				left_index = mid_index + 1
			else:
				right_index = mid_index - 1

		temp_index = mid_index
		# Check if there are other courses to the left
		while mid_index != 0:
			mid_index = mid_index - 1
			if subject_rows[mid_index][2] == subj:
				if subject_rows[mid_index][7] is not "" and subject_rows[mid_index][7] != "\"\"" and subject_rows[mid_index][1].lower() == term.lower() and \
				subject_rows[mid_index][3].lower() == crse.lower() and subject_rows[mid_index][4].lower() == class_id.lower():
					term_grades_for_course.append(float(subject_rows[mid_index][7]))
			else:
				break

		mid_index = temp_index
		# Check if there are other courses to the right
		while mid_index != len(subject_rows) - 1:
			mid_index = mid_index + 1
			if subject_rows[mid_index][2] == subj:
				if subject_rows[mid_index][7] is not "" and subject_rows[mid_index][7] != "\"\"" and subject_rows[mid_index][1].lower() == term.lower() and \
				subject_rows[mid_index][3].lower() == crse.lower() and subject_rows[mid_index][4].lower() == class_id.lower():
					term_grades_for_course.append(float(subject_rows[mid_index][7])) # Converts grade from string to float
			else:
				break
		
		if not term_grades_for_course: 
			#print("No grades. P/NP course: " + term + " " + subj + " " + crse + " " + class_id)
			return 0
		else:
			median = statistics.median(term_grades_for_course)
			#print("Median is: " + str(median))
			return median

	"""
	Calculates the total number of units taken by a student.
	Parameter is the student's student id passed in as a string.
	Returns the number of total units the student has taken as an int.
	"""
	def calc_units_taken(self, courses, pidm, term=None):
		num_units = 0

		# If the course is P/NP, then the units should still be considered.
		if term != None:
			for row in courses:
				if row[1] == term:
					num_units += float(row[5])
		else:
			for row in courses:
				num_units += float(row[5])
		return num_units

	"""
	Gets all the courses that a student completed.
	Parameter is the student's student id passed in as a string.
	Returns the courses as a list.
	"""
	def get_courses_completed(self, courses, pidm, term=None):
		courses_completed = []

		if term != None:
			for row in courses:
				if row[1] == term and row[7] is not '':	# Omit courses with no grade
					courses_completed.append(row)
		else: 
			for row in courses:
				if row[7] is not '': # Omit courses with no grade
					courses_completed.append(row)
		return courses_completed

	"""
	Gets the sum of the median grade of each course weighted by the units each course is worth.
	Median grade for one course is multiplied by the units the course is worth.
	Parameter courses_completed is a list of courses as a string that a student has completed. 
	Returns the sum of the medians as a float
	"""
	def get_sum_of_medians(self, courses_completed):
		sum_of_medians = 0

		for row in courses_completed:
			sum_of_medians += self.calc_median(row[1], row[2], row[3], row[4]) * int(row[5])

		return sum_of_medians

	"""
	Retrieves the rows of data from a hard-coded csv file. 
	If a pidm is provided, the rows of grades related to that pidm will be returned. 
	If not pidm is provided, all of the rows of grades will be returned.
	"""
	def retrieve_rows(self, pidm=None):
		rows = []
		global course_rows
		if pidm != None:

			print("Binary searching for courses")

			left_index = 0
			right_index = len(course_rows) - 1
			mid_index = 0
			while left_index <= right_index:

				mid_index = (left_index + right_index) // 2
				
				if course_rows[mid_index][0] == pidm:
					print("Found midpoint at " + str(mid_index))
					rows.append(course_rows[mid_index])
					break
				elif course_rows[mid_index][0] < pidm:
					left_index = mid_index + 1
				else:
					right_index = mid_index - 1


			temp_index = mid_index
			# Check if there are other courses to the left of midpoint
			while mid_index != 0:
				mid_index = mid_index - 1
				if course_rows[mid_index][0] == pidm:
					rows.append(course_rows[mid_index])
				else:
					break
			mid_index = temp_index
			# Check if there are other courses to the right of midpoint
			while mid_index != len(course_rows) - 1:
				mid_index = mid_index + 1
				if course_rows[mid_index][0] == pidm:
					rows.append(course_rows[mid_index])
				else:
					break
		else:
			with open(course_data, 'r') as csvFile:	
				csv_reader = csv.reader(csvFile, delimiter=',', quotechar="'", quoting=csv.QUOTE_MINIMAL) #separated by commas and remove extra quotes
				
				for row in csv_reader:	
					rows.append(row)
			csvFile.close()
		return rows

	"""
	Retrieves the rows of data from a hard-coded csv file based on a given term. 
	"""
	def retrieve_rows_term(self, pidm, term):
		rows = []
		global course_rows
		if pidm != None and course_rows:
			print("Binary")

			left_index = 0
			right_index = len(course_rows) - 1
			mid_index = 0
			while left_index <= right_index:
				mid_index = (left_index + right_index) // 2

				if course_rows[mid_index][0] == pidm:
					print("Found midpoint at " + str(mid_index))
					if course_rows[mid_index][1] == term:
						rows.append(course_rows[mid_index])
					break
				elif course_rows[mid_index][0] < pidm:
					left_index = mid_index + 1
				else:
					right_index = mid_index - 1

			temp_index = mid_index

			# Check if there are other courses to the left of midpoint
			while mid_index != 0:
				mid_index = mid_index - 1
				if course_rows[mid_index][0] == pidm:
					if course_rows[mid_index][1] == term:
						rows.append(course_rows[mid_index])
				else:
					break
			mid_index = temp_index		
			# Check if there are other courses to the right of midpoint 
			while mid_index != len(course_rows) - 1:
				mid_index = mid_index + 1
				if course_rows[mid_index][0] == pidm:
					if course_rows[mid_index][1] == term:
						rows.append(course_rows[mid_index])
				else:
					break

		return rows

	def retrieve_admittance_rows(self):
		rows = []

		#Load the csv data that contains student acadamic data into the program
		#rows is a list of each row in the csv file
		with open(admittance_data, 'r') as csvFile:	
			csv_reader = csv.reader(csvFile, delimiter=',', quotechar="'", quoting=csv.QUOTE_MINIMAL)
			for row in csv_reader:
				rows.append(row)
			csvFile.close()
		return rows

	"""
	Updates the course_data csv file with the calculated GPAM. It will update either the cummulative
	GPAM or the TERM_GPAM. Uses pandas module to search and insert values into the csv.
	Parameters are strings for pidm, gpam, and the term.
	"""
	def update_gpam(self, pidm, df, gpam, term=None):
		print("Updating: PIDM-" + pidm + " GPAM-" + gpam)
		if term != None:
			# Get the locations/indexes of each row that contains the PIDM and TERM
			row_locs = df.loc[(df["PIDM"].astype(str) == pidm) & (df["TERM"].astype(str) == term)].index.values #Requires & operator instead of and to make comparison
			for index in row_locs:	#Update the column for each of the rows 
				df.loc[index, "TERM_GPAM"] = gpam
		else:
			df.loc[df.PIDM.isin([pidm]), "GPAM"] = gpam
		
	def main(self):
		global course_rows

		# dict to add to dataframe
		gpam_dict = {'PIDM' : [], 'GPAM': []}
		counter = 0
		df = pd.read_csv(course_data)
		df["UNITS"] = df["UNITS"].astype(int)	# Prevents the UNITS column from being changed to floats after updating csv
		previous = 0
		for row in course_rows:
			pidm = row[0]
			counter += 1

			try:
				if row[8] != "\"\"":	# Skip rows that already have GPAM updated
					#print("Already has GPAM: " + row[8])
					continue
			except IndexError:	# GPAM column not created yet
				try: 
					found_pidm = self.verify_admittance(pidm)
					assert(found_pidm is True), "The pidm could not be found."
					print("calculating GPAM...")
					gpam = str(self.gpam(pidm))
					print("GPAM is " + gpam + " " + str(pidm) + " Row: " + str(counter-1))
					self.update_gpam(pidm, df, gpam)
					continue
				except AssertionError:
					continue

			# Check if the current pidm is the same as the last one
			if previous == pidm:
				#print(previous + " == " + row[0])
				continue
			else:
				previous = pidm
			
			try :
				# Verify student was admitted after 2008 before calculating GPAM
				found_pidm = self.verify_admittance(pidm)
				assert(found_pidm is True), "The pidm could not be found."
				print("calculating GPAM...")
				#gpam = str(self.gpam(pidm))
				gpam = str(self.gpam(pidm))
				print("GPAM is " + gpam + " " + str(pidm) + " Row: " + str(counter-1))
				
				#gpam_dict['PIDM'].append(row[0])
				#gpam_dict['GPAM'].append(gpam)
				#print(gpam_dict)

				self.update_gpam(pidm, df, gpam)
				#print("TERM_GPAM is " + str(self.gpam(row[0], row[1])))
			except AssertionError:
				continue
			except ZeroDivisionError:
				print("Zero units being divided.")
				continue
			except KeyboardInterrupt:
				df.to_csv(course_data, index=False, quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
				sys.exit(0)

		# At this point, the dataframe should have all of the GPAMs. Write to the CSV.
		df.to_csv(course_data, index=False, quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
		print("Finished")

if __name__ == "__main__":
    gpam_obj = GPAM()
    gpam_obj.main()
