import sys, mechanize

from bs4 import BeautifulSoup

class HAC:

	login_url = ("https://hac.westport.k12.ct.us/"
				 "HomeAccess/Account/LogOn?ReturnUrl=%2fhomeaccess")

	data_url = ("https://hac.westport.k12.ct.us/"
				"HomeAccess/Content/Student/Assignments.aspx")

	grade_weight = { "F": 0.0, "D": 1.0, "C": 2.0, "B": 3.0, "A": 4.0 }

	modifier_weight = { "-": -1/3.0, "+": 1/3.0, " ": 0,
						"B": -1/3.0, "A": 0, "H": 1/3.0, "P": 2/3.0 }

	def __init__(self, username, password):
		self.username = username
		self.password = password
		self.student_data = []
		self.max_string_length = 0

	def get_data(self):
		"""Get the class data from hac and store it in student_data"""
		browser = mechanize.Browser()

		browser.open(self.login_url)

		browser.select_form(nr=0)
		browser.form["LogOnDetails.Password"] = self.password
		browser.form["LogOnDetails.UserName"] = self.username
		browser.submit()

		browser.open(self.data_url)

		html = browser.response().read()
		soup = BeautifulSoup(html)

		classes = soup.select(".AssignmentClass")

		#Invalid username or password
		if not classes:
			print "Could not access account with \
				   given username and password."
			sys.exit(0)

		class_num = 0
		for section in classes:
			average = section.select("#plnMain_rptAssigmnetsByCourse"
				"_lblOverallAverage_"+ str(class_num))[0].string

			name = section.select("a.sg-header-heading")[0].string
			class_num += 1

			for letter in name:
				if letter.isalpha():
					level = letter
					break
			name = name.replace('\n','').replace('\r','').lstrip().rstrip()
			name = name[18:]

			length = len(name + ": " + average)

			if length > self.max_string_length:
				self.max_string_length = length

			self.student_data.append(
				dict(_class=name, average=average, level=level)
			)

	def display_data(self):
		"""format and disply the data in student_data"""
		if self.student_data:
			print ("-" * self.max_string_length + "|--|")
			for data in self.student_data:		
				length = len(data["_class"] + ": " + data["average"])

				print(
					data["_class"] + ": "
					+ (" " * (self.max_string_length - length) 
					+ data["average"] +  "|")
					+ self._letter_grade(float(data["average"]))
					+ "|"
				)
				
				print ("-" * self.max_string_length + "|--|")
		else:
			raise UserWarning("Must get_data() first!")

	def display_gpa(self):
		"""Display the gpa calculated by _gpa, both weighted and not."""
		if self.student_data:
			uw_gpa, w_gpa = self._gpa()
			print("Weighted GPA: " + str(w_gpa))
			print("Unweighted GPA: " + str(uw_gpa))
		else:
			raise UserWarning("Must get_data() first!")

	def _gpa(self):
		"""Calculate the weighted and not GPA and return both in a tuple."""
		weighted_total = 0
		unweighted_total = 0
		count = 0
		for data in self.student_data:
			letter_grade = self._letter_grade(data["average"])
			if data["level"] != "E":  #E is not an academic class
				weighted_total += (self.grade_weight[letter_grade[0]] 
						+ self.modifier_weight[letter_grade[1]]
						+ self.modifier_weight[data["level"]])

			unweighted_total += (self.grade_weight[letter_grade[0]]
					+ self.modifier_weight[letter_grade[1]])
			count += 1

		return (weighted_total / count, unweighted_total / count)

	def _letter_grade(self, average):
		"""Take the average and return the corresponding letter grade."""
		grade = ""
		if average < 59.5:
			grade = "F "
		elif 59.5 <= average < 69.5:
			grade = "D"
			if average < 62.5:
				grade += "-"
			elif average >= 66.5:
				grade += "+"
			else:
				grade += " "
		elif 69.5 <= average < 79.5:
			grade = "C"
			if average < 72.5:
				grade += "-"
			elif average >= 76.5:
				grade += "+"
			else:
				grade += " "
		elif 79.5 <= average < 89.5:
			grade = "B"
			if average < 82.5:
				grade += "-"
			elif average >= 86.5:
				grade += "+"
			else:
				grade += " "
		elif 89.5 <= average:
			grade = "A"
			if average < 92.5:
				grade += "-"
			elif average >= 96.5:
				grade += "+"
			else:
				grade += " "
		return grade

if __name__ == "__main__":
	
	homeAccess = HAC(sys.argv[1], sys.argv[2])
	homeAccess.get_data()
	homeAccess.display_data()
	homeAccess.display_gpa()
