import csv
import datetime
import multiprocessing
import argparse

# Preprocessing the data 
# 1. extract
# 2. remove duplicates
# 3. sort

# The input data format:
# [0] apn
# [1] appdate
# [2] pubdate
# [3] grtdate
# [4] ipcs
# [5] app
# [6] inv
# [7] address
# [8] zipcode
# [9] nationality

SYMBOL_SHORT_SAMPLE_FILE = "/Users/shayangnala/py_crawler/outlier_patent/ipcs_sample_till_2006_nationality_1.csv"
TEST_OUTPUT = "/Users/shayangnala/py_crawler/outlier_patent/test_output_new.csv"

parser = argparse.ArgumentParser(description="Identify the outliers for a particular year, the input file must be sorted")
parser.add_argument("--startyear", type=int, help="The start year to identify outliers for")
parser.add_argument("--endyear", type=int, help="The end year to identify outliers for")
parser.add_argument("--inputfile", "-i", help="Path of the input file (containing all patents)", default=SYMBOL_SHORT_SAMPLE_FILE)
parser.add_argument("--outputfile", "-o", help="Path of the output file", default=TEST_OUTPUT)

args = parser.parse_args()

# this list stores the registered main group symbols
main_group_symbol_list = []

# this list contains all the patents
list_of_patents = []

# the dictionary that contains the year: patent list pairs
all_pats = {}

# all mg symbol combination register
existing_mg_symbols = set()

# this list stores the patents waiting to be compared
waitlist = []

# this list stores the outlier patents
outliers = []

# the patent class
class Patent:

	def __init__(self, appNo, appDate, nationality, mg_string, mg_symbols_set):
		self.appNo = appNo
		self.appDate = appDate
		self.nationality = nationality
		self.mg_string = mg_string
		self.mg_symbols_set = mg_symbols_set
		self.adj_list = []

	def __str__(self):
		return "appNo: " + str(self.appNo) + "appDate: " + str(self.appDate)


# retrieve patents before the given end date
def retrieve_patents(startyear, endyear):
	with open(args.inputfile) as symbol_csv_file:
		reader = csv.reader(symbol_csv_file)
		header_row = next(reader) # reader the header row

		# construct bitstring according to the main_group_symbol_list	
		for row in reader:
			appyear = row[1].split('/')[0]
			if int(appyear) >= int(startyear):
				break


			# extract the ipcs
			ipcs = str(row[4]).split()

			# extract the main group symbols
			# using set will automatically remove the duplicates
			mg_symbols = set()

			for i in ipcs:
				mg = i.split('/')[0]
				mg_symbols.add(mg)

			# remove dupcates and sort the main group symbols

			# turn the set into a string with main group symbols in sorted order
			mg_string = " ".join(sorted(list(mg_symbols)))

			# extract other attributes from the row
			apn = row[0]
			appdate = row[1]
			nationality = row[9]

			print ("Debug 1, the row looks like: ", apn , " date: ", appdate, " mg_string: ", mg_string)

			my_patent = Patent(apn, appdate, nationality, mg_string, mg_symbols)

			existing_mg_symbols.add(mg_string)


		for row in reader:
			appyear = row[1].split('/')[0]
			if int(appyear) > int(endyear) :
				break

			# extract the ipcs
			ipcs = str(row[4]).split()

			# extract the main group symbols
			# using set will automatically remove the duplicates
			mg_symbols = set()

			for i in ipcs:
				mg = i.split('/')[0]
				mg_symbols.add(mg)

			# remove dupcates and sort the main group symbols

			# turn the set into a string with main group symbols in sorted order
			mg_string = " ".join(sorted(list(mg_symbols)))

			# extract other attributes from the row
			apn = row[0]
			appdate = row[1]
			nationality = row[9]
			my_patent = Patent(apn, appdate, nationality, mg_string, mg_symbols)

			waitlist.append(my_patent)


def is_same_date(curr_p, next_p):
	curr_date = curr_p.appDate
	next_date = next_p.appDate

	cd_split = curr_date.split('/')
	nd_split = next_date.split('/')

	d1 = datetime.date(int(cd_split[0]), int(cd_split[1]), int(cd_split[2]))
	d2 = datetime.date(int(nd_split[0]), int(nd_split[1]), int(nd_split[2]))

	return d1 == d2


def find_outliers():
	i = 0
	while i < len(waitlist):
		curr_p = waitlist[i]

		# batch add all patents of the same date into a list		
		p_same_date = []
		p_same_date.append(curr_p)

		j = i + 1
		while j < len(waitlist):
			if is_same_date(curr_p, waitlist[j]):
				p_same_date.append(waitlist[j])
				j = j + 1
			else: 
				break

		i = j

		apns = []
		for x in p_same_date:
			apns.append(x.appNo)
		print ("Debug 8, this batch: ", " ".join(apns))

		batch_mg_strings = []
		for p in p_same_date:			
			this_mg_string = p.mg_string
			batch_mg_strings.append(this_mg_string)

			if this_mg_string in existing_mg_symbols:
				print ("Debug 6, this: ", this_mg_string, " is in existing_mg_symbols")
				continue

			# set the flag
			# assuming p is an outlier until not true
			is_outlier = True

			# set operation
			this_mg_set = set(this_mg_string.split())			
			for that_mg_string in existing_mg_symbols:
				that_mg_set = set(that_mg_string.split())
				symm_diff = this_mg_set.symmetric_difference(that_mg_set)

				print ("Debug 5, symm_diff between this: ", this_mg_string, " and that: ", that_mg_string, " is: ", " ".join(symm_diff))

				if len(symm_diff) < 2:
					is_outlier = False
					break

			if is_outlier == True:
				print ("Debug 3, appending outlier: ", p.appNo, " appdate: ", p.appDate, " mg_string: ", p.mg_string)
				outliers.append(p)


		# add the mg_string to existing mg symbols set
		existing_mg_symbols.update(batch_mg_strings)

# === The main functions ====

retrieve_patents(args.startyear, args.endyear)
print ("Debug 2, the length of existing_mg_symbols set: ", len(existing_mg_symbols))
print ("Debug 2, the length of the waitlist: ", len(waitlist))
find_outliers()
print ("Debug 4, the length of outliers: ", len(outliers))

output_file_name = args.outputfile + "_" + str(args.startyear) + "_" + str(args.endyear) + ".csv"

# for debug purpose, write the outliers to a file
with open(output_file_name, 'w') as output_csv:
	writer = csv.writer(output_csv)
	# write header row
	writer.writerow(["appNo", "appDate", "mg_string", "nationality"])

	for p in outliers:
		# write to a file
		writer.writerow([p.appNo, p.appDate, p.mg_string, p.nationality])
		# print ("debug 2: ", p.appNo, " ", " ".join(p.adj_list))
