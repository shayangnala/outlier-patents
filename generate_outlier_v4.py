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

# newly added mg symbols for each year
yearly_added_mg_symbols = {}

# this list stores the patents waiting to be compared
waitlist = {}

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

		yearly_added_mg_symbols[startyear-1] = set()
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

			# add to the master set
			existing_mg_symbols.add(mg_string)

			# add to the yearly set
			yearly_added_mg_symbols[startyear-1].add(mg_string)


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

			print ("Debug 2, the row looks like: ", apn , " date: ", appdate, " mg_string: ", mg_string)

			my_patent = Patent(apn, appdate, nationality, mg_string, mg_symbols)

			# check the mg_symbols that if it should be added as a newly added one:
			if mg_string not in existing_mg_symbols:

				# add to the master register:
				existing_mg_symbols.add(mg_string)


				# add to each year's register:
				if appyear in yearly_added_mg_symbols.keys():
					yearly_added_mg_symbols[appyear].add(mg_string)
				else:
					yearly_added_mg_symbols[appyear] = set() # this is a set, too
					yearly_added_mg_symbols[appyear].add(mg_string)


			if appyear in waitlist.keys():
				waitlist[appyear].append(my_patent) # using list so that appdate order is still maintained within each year
			else:
				waitlist[appyear] = []
				waitlist[appyear].append(my_patent)


def is_same_date(curr_p, next_p):
	curr_date = curr_p.appDate
	next_date = next_p.appDate

	cd_split = curr_date.split('/')
	nd_split = next_date.split('/')

	d1 = datetime.date(int(cd_split[0]), int(cd_split[1]), int(cd_split[2]))
	d2 = datetime.date(int(nd_split[0]), int(nd_split[1]), int(nd_split[2]))

	return d1 == d2


# this_set: a set of patents
# that_set: a set of mg symbol combinations
def compute(this_set, that_set):
	i = 0
	outliers = set()
	print ("Debug XX: " , len(this_set))
	while i < len(this_set):
		curr_p = this_set[i]

		# batch add all patents of the same date into a list		
		p_same_date = []
		p_same_date.append(curr_p)

		j = i + 1
		while j < len(this_set):
			if is_same_date(curr_p, this_set[j]):
				p_same_date.append(this_set[j])
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

			if this_mg_string in that_set:
				print ("Debug 6, this: ", this_mg_string, " is in existing_mg_symbols")
				continue

			# set the flag
			# assuming p is an outlier until not true
			is_outlier = True

			# set operation
			this_mg_set = set(this_mg_string.split())			
			for that_mg_string in that_set:
				that_mg_set = set(that_mg_string.split())
				symm_diff = this_mg_set.symmetric_difference(that_mg_set)

				print ("Debug 5, symm_diff between this: ", this_mg_string, " and that: ", that_mg_string, " is: ", " ".join(symm_diff))

				if len(symm_diff) < 2:
					is_outlier = False
					break

			if is_outlier == True:
				print ("Debug 3, appending outlier: ", p.appNo, " appdate: ", p.appDate, " mg_string: ", p.mg_string)
				outliers.add(p)

	return outliers

def compare_with_self_year(this_set):
	ty_existings = set()

	i = 0
	outliers = set()	

	# find the batch with the same date
	while i < len(this_set):
		curr_p = this_set[i]

		# batch add all patents of the same date into a list		
		p_same_date = []
		p_same_date.append(curr_p)

		j = i + 1
		while j < len(this_set):
			if is_same_date(curr_p, this_set[j]):
				p_same_date.append(this_set[j])
				j = j + 1
			else: 
				break

		i = j

		apns = []
		for x in p_same_date:
			apns.append(x.appNo)
		print ("Debug a, this batch: ", " ".join(apns))

		batch_mg_strings = []
		for p in p_same_date:			
			this_mg_string = p.mg_string
			batch_mg_strings.append(this_mg_string)

			if this_mg_string in ty_existings:
				print ("Debug y, this: ", this_mg_string, " is in existing_mg_symbols")
				continue

			# set the flag
			# assuming p is an outlier until not true
			is_outlier = True

			# set operation
			this_mg_set = set(this_mg_string.split())			
			for that_mg_string in ty_existings:
				that_mg_set = set(that_mg_string.split())
				symm_diff = this_mg_set.symmetric_difference(that_mg_set)

				print ("Debug 5, symm_diff between this: ", this_mg_string, " and that: ", that_mg_string, " is: ", " ".join(symm_diff))

				if len(symm_diff) < 2:
					is_outlier = False
					break

			if is_outlier == True:
				print ("Debug 3, appending outlier: ", p.appNo, " appdate: ", p.appDate, " mg_string: ", p.mg_string)
				outliers.add(p)

		ty_existings.update(batch_mg_strings)

	return outliers


def find_outliers(startyear, endyear):

	i = startyear
	
	all_outliers = set()

	for i in range (startyear, endyear+1): 
		this_set = waitlist[str(i)]

		results = []

		for j in range(startyear-1, i):
			that_set = yearly_added_mg_symbols[j]
			outliers = compute(this_set, that_set)
			# all_outliers = all_outliers + outliers # it has problems here
			results.append(outliers)

		results.append(compare_with_self_year(this_set))

		results_intersection = set.intersection(*results)

		all_outliers.update(results_intersection)


	return all_outliers


# === The main functions ====

retrieve_patents(args.startyear, args.endyear)
print ("Debug 3, the length of existing_mg_symbols set: ", len(existing_mg_symbols))
print ("Debug 3, the length of the waitlist: ", len(waitlist), " keys: ", waitlist.keys())
all_outliers = find_outliers(args.startyear, args.endyear)
print ("Debug 4, the length of outliers: ", len(all_outliers))

output_file_name = args.outputfile + "_" + str(args.startyear) + "_" + str(args.endyear) + ".csv"

# for debug purpose, write the outliers to a file
with open(output_file_name, 'w') as output_csv:
	writer = csv.writer(output_csv)
	# write header row
	writer.writerow(["appNo", "appDate", "mg_string", "nationality"])

	for p in all_outliers:
		# write to a file
		writer.writerow([p.appNo, p.appDate, p.mg_string, p.nationality])
		# print ("debug 2: ", p.appNo, " ", " ".join(p.adj_list))
