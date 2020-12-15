import csv
import datetime
from multiprocessing import Pool

# no dict version

# Step2. Load a sample data file
SYMBOL_SHORT_SAMPLE_FILE = "/Users/shayangnala/py_crawler/outlier_patent/ipcs_sample_till_2006_nationality_1.csv"
MAIN_GROUP_LIST_FILE = "/Users/shayangnala/Downloads/maingroup_symbol_list.csv"
TEST_OUTPUT = "/Users/shayangnala/py_crawler/outlier_patent/test_output.csv"


class Patent:

	def __init__(self, appNo, appDate, bitstring):
		self.appNo = appNo
		self.appDate = appDate
		self.bitstring = bitstring
		self.adj_list = []



	def __str__(self):
		return "appNo: " + str(self.appNo) + "appDate: " + str(self.appDate)
		# return "i am a string"

main_group_symbol_list = []
def retrieve_main_group_symbol_list():
	with open(MAIN_GROUP_LIST_FILE) as maingroup_list_csv:
		reader = csv.reader(maingroup_list_csv)
		for i in reader:
			main_group_symbol_list.append(str(i[0]))



# this function convert a list to a string
def convert_list_to_string(bit_list):
	return ''.join(bit_list)

# if two bit strings are adjacent
def isAdjacent(bitstring_1, bitstring_2):
	num_diff_bits = 0
	if len(bitstring_1) != len(bitstring_2):
		print ("Exception: two bit strings have different lengths ", len(bitstring_1), " ", len(bitstring_2))
		return


	for i in range (0, len(bitstring_1)):
		if bitstring_1[i] != bitstring_2[i]:
			# print ("pos: " , i, " bit from string1: ", bitstring_1[i], " bit from string2: ", bitstring_2[i])
			num_diff_bits = num_diff_bits + 1

	# print ("Different bits between the two bitstrings: ", num_diff_bits)
	isAdj = num_diff_bits < 2

	return isAdj

def isAdjacent(this_p, that_p):
	num_diff_bits = 0
	bitstring_1 = this_p.bitstring
	bitstring_2 = that_p.bitstring

	if len(bitstring_1) != len(bitstring_2):
		# print ("Exception: two bit strings have different lengths ", len(bitstring_1), " ", len(bitstring_2))
		return


	print ("this p: ", this_p.appNo, " that p: ", that_p.appNo)

	for i in range (0, len(bitstring_1)):
		if bitstring_1[i] != bitstring_2[i]:
			# print ("pos: " , i, " bit from string1: ", bitstring_1[i], " bit from string2: ", bitstring_2[i])
			num_diff_bits = num_diff_bits + 1

	# print ("Different bits between the two bitstrings: ", num_diff_bits)
	isAdj = num_diff_bits < 2

	return isAdj

# compare if that date is before this date
def isBefore(this_d, that_d):

	this_d_split = this_d.split('/')
	that_d_split = that_d.split('/')
	d1 = datetime.date(int(this_d_split[0]), int(this_d_split[1]), int(this_d_split[2]))
	d2 = datetime.date(int(that_d_split[0]), int(that_d_split[1]), int(that_d_split[2]))

	# print ("this date: " , this_d, " that date: ", that_d, " is that before this: ", d1 > d2)	

	return d1 > d2

result_dict = {}

list_of_patents = []
retrieve_main_group_symbol_list()
with open(SYMBOL_SHORT_SAMPLE_FILE) as symbol_csv_file:
	reader = csv.reader(symbol_csv_file)
	header_row = next(reader) # reader the header row

	# construct bitstring according to the main_group_symbol_list	

	for row in reader:

		# # initialize the dictionary
		# main_group_dict = {}
		# for k in main_group_symbol_list:
		# 	main_group_dict[k] = '0'

		# initialize a list
		n_list = ['0']*len(main_group_symbol_list)

		# add value to the ipc dictionary
		ipcs = str(row[1]).split()
		for i in ipcs:
			main_group = i.split('/')[0]
			if main_group in main_group_symbol_list: 
				pos = main_group_symbol_list.index(main_group)
				# print ("The position of ", main_group, " is at pos: ", pos)
				n_list[pos] = '1'
			else: 
				print (main_group, " not in the registered list")
			# if main_group in main_group_dict:
			# 	main_group_dict[main_group] = '1'
			# else: 
			# 	print ("main group not included in the dictionary: ", main_group)

		# == the end of creating the bit string


		# extract other attributes from the row
		apn = row[0]
		appdate = row[2]
		grtdate = row[4]
		nationality = row[5]

		# store the data
		# entry_dict = {}
		# entry_dict['appdate'] = appdate
		# entry_dict['grtdate'] = grtdate
		# entry_dict['nationality'] = nationality
		# entry_dict['bitstring'] = convert_list_to_string(n_list)

		# result_dict[apn] = entry_dict

		my_patent = Patent(apn, appdate, convert_list_to_string(n_list))
		list_of_patents.append(my_patent)


def compute(i):
	this_p = list_of_patents[i]

	j = i - 1
	while j >= 0:
		that_p = list_of_patents[j]
		
		this_d = this_p.appDate
		that_d = that_p.appDate

		isAdj = False
		if isBefore(this_d, that_d):
			isAdj = isAdjacent(this_p, that_p)

		if isAdj == True:
			this_p.adj_list.append(that_p.appNo)

		# move the pointer for the inner while loop
		j = j - 1


i = 216 # 216 for nationality 1, 2358 for nationality 0
while i < len(list_of_patents):
	compute(i)
	# move the pointer for the outer while loop
	i = i + 1


# seperate write module
with open(TEST_OUTPUT, 'w') as output_csv:
	writer = csv.writer(output_csv)
	# write header row
	writer.writerow(["appNo", "appDate", "Adj Patents"])

	for i in range (216, len(list_of_patents)):
		p = list_of_patents[i]	
		# write to a file
		writer.writerow([p.appNo, p.appDate, " ".join(p.adj_list)])
		print ("debug 2: ", p.appNo, " ", " ".join(p.adj_list))

