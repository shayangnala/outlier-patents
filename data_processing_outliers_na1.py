import csv
import datetime
import multiprocessing
import argparse
from itertools import combinations

# The input data format:
# 0. appno
# 1. appdate
# 2. mg_string
# 3. nationality
# 4. pubdate
# 5. grtdate
# 6. ipcs
# 7. app
# 8. inv
# 9. address
# 10. zipcode
# 11. province_code
# 12. province

parser = argparse.ArgumentParser(description="Data processing script")
parser.add_argument("--inputfile", "-i", help="Path of the input file (containing all outlier patents whose nationality is 1)")
parser.add_argument("--outputfile", "-o", help="Path of the output file")

args = parser.parse_args()

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




# retrieve all patents
def retrieve_patents():
	with open(args.inputfile) as input_csv_file:
		reader = csv.reader(input_csv_file)
		header_row = next(reader) # reader the header row

		for row in reader:

			# extract the applicant
			apps = str(row[8])
			apps_array = str(row[8]).split()
			app_type = analyze_app_type(apps_array).strip()
			num_of_apps = len(apps_array)

			# extract other attributes from the row
			appno = str(row[0])
			appdate = row[1]

			my_patent = Patent(appno, appdate, apps, app_type, num_of_apps)

			plist.append(my_patent)


# === The main functions ====

retrieve_patents()
print ("Debug 2, the length of input file: ", len(plist))

output_file_name = args.outputfile + "outliers_processed.csv"
print (output_file_name)

# for debug purpose, write the outliers to a file
with open(output_file_name, 'w') as output_csv:
	writer = csv.writer(output_csv)
	# write header row
	writer.writerow(["appNo", "appDate", "app", "app_type", "num_of_apps"])

	for p in plist:
		# write to a file
		writer.writerow([p.appNo, p.appDate, p.app, p.app_type, p.num_of_apps])
		# print ("debug 2: ", p.appNo, " ", " ".join(p.adj_list))
