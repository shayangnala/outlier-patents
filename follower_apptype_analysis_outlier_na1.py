import csv
import datetime
import multiprocessing
import argparse
from itertools import combinations

# The input data format:
# 0. mg_comb
# 1. apn
# 2. num_usage
# 3. usagehistory
# 4. num_adj
# 5. adjs
# 6. appdate
# 7. appyr
# 8. ipcs
# 9. first_used
# 10. newcom
# 11. outlier
# 12. distance
# 13. app
# 14. app_type
# 15. num_of_apps
# 16. pubdate
# 17. grtdate
# 18. inv
# 19. address
# 20. zipcode
# 21. nationality
# 22. year

PAT_APPTYPE_FILE = "/Users/shayangnala/py_crawler/outlier_patent/dpoutliers_processed.csv"
IPC_USAGE_FILE = "/Users/shayangnala/py_crawler/outlier_patent/ipcsusage_outlier_university.csv"

# the list to store patents in the input file
plist = []

# the patent class
class Patent:

	def __init__(self, appNo, appDate, app, app_type, num_of_apps):
		self.appNo = appNo
		self.appDate = appDate
		self.app = app
		self.app_type = app_type
		self.num_of_apps = num_of_apps

	def __str__(self):
		return "appNo: " + str(self.appNo) + "appDate: " + str(self.appDate)

def identify_type(app):
	if len(app) == 0:
		return ""

	if len(app) == 2 or len(app) == 3:
		return "individual"

	if "研究" in app or "医院" in app:
		return "institute"

	if "大学" in app or "学院" in app:
		return "university"

	if "公司" in app:
		return "company"

	if "厂" in app:
		return "factory"


	return "other"


def analyze_app_type(apps):

	result_set = set()

	for a in apps:
		result_set.add(identify_type(a))

	return " ".join(sorted(list(result_set)))



apn_to_apptype = {}
result_list = []
# retrieve all patents
def construct_apn_apptype_dict():
	with open(PAT_APPTYPE_FILE) as input_csv_file:
		reader = csv.reader(input_csv_file)
		header_row = next(reader) # reader the header row

		for row in reader:
			apn = row[0]
			app_type = row[3]
			apn_to_apptype[apn] = app_type


			# apn = row[1]
			# appdate = row[6]
			# usagehistory = row[3]




			# # extract the applicant
			# apps = str(row[5])
			# apps_array = apps.split()
			# app_type = analyze_app_type(apps_array).strip()
			# num_of_apps = len(apps_array)

			# # extract other attributes from the row
			# appno = str(row[0])
			# appdate = row[1]

			# my_patent = Patent(appno, appdate, apps, app_type, num_of_apps)

			# plist.append(my_patent)

def analyze_outlier_follower_apptype():
	with open(IPC_USAGE_FILE) as input_csv_file:
		reader = csv.reader(input_csv_file)
		header_row = next(reader)

		for row in reader:
			apn = row[1]
			usagehistory = row[3]

			usages_split_arr = usagehistory.split()

			apptype_counter = {}

			year_univ_follower = 0
			year_company_follower = 0

			for item in usages_split_arr:
				follower_apn = item.split("+")[2]
				if follower_apn in apn_to_apptype.keys():
					apptype = apn_to_apptype[follower_apn]
					if apptype in apptype_counter.keys():
						apptype_counter[apptype] = apptype_counter[apptype] + 1
					else:											
						apptype_counter[apptype] = 1
						if apptype == "university":
							year_univ_follower = item.split("+")[1]
						if apptype == "company":
							year_company_follower = item.split("+")[1]

			# "apn|num_univ_follower|year_univ_follower|num_company_follower|year_company_follower"		
			value = apn + "|" + str(apptype_counter["university"]) + "|" \
						+ str(year_univ_follower)

			if "company" in apptype_counter.keys():
				value = value + "|" + str(apptype_counter["company"]) + "|" + str(year_company_follower)
			else:
				value = value + "|0|."
			result_list.append(value)




# === The main functions ====

construct_apn_apptype_dict()
analyze_outlier_follower_apptype()

output_file_name = "univ_outlier_follower.txt"
print (output_file_name)

# for debug purpose, write the outliers to a file
with open(output_file_name, 'w') as output_file:
	# write header row
	output_file.write("apn|num_univ_follower|year_univ_follower|num_company_follower|year_company_follower\n")

	for item in result_list:
		output_file.write(item+"\n")