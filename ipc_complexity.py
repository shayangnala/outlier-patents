import csv
from itertools import combinations
import pickle

ALL_PATENTS_FILE = "/Users/shayangnala/py_crawler/outlier_patent/pat_all_granted.csv"
# ALL_PATENTS_FILE = "/Users/shayangnala/py_crawler/outlier_patent/test_input.csv"

ipc_comb_dict_file = open("ipc_comb_dict.pkl", "rb")
ipc_comb_dict = pickle.load(ipc_comb_dict_file)

ipc_freq_dict_file = open("ipc_freq_dict.pkl", "rb")
ipc_freq_dict = pickle.load(ipc_freq_dict_file)

result_dict = {}

START_YEAR = 2006
END_YEAR = 2006

num_of_single = 0
num_warn0 = 0
num_warn1 = 0
num_warn2 = 0

total_counter = 0

# read in all patents and process
with open(ALL_PATENTS_FILE) as all_patents_file:
	reader = csv.reader(all_patents_file)
	header_row = next(reader) # reader the header row

	for row in reader:
		apn = str(row[0])
		appdate = row[1]

		if int(appdate.split("/")[0]) < START_YEAR:
			continue		

		if int(appdate.split("/")[0]) > END_YEAR:
			break	

		total_counter = total_counter + 1

		ipcs = str(row[4]).split()

		# print("Debug 0: ", appdate)

		# remove duplicates
		mg_symbols = set()
		for i in ipcs:
			mg = i.split('/')[0]
			mg_symbols.add(mg)


		all_comb = set(combinations(sorted(list(mg_symbols)), 2))

		# for a in all_comb:
		# 	print("comb: ", a, " freq: ", ipc_comb_dict[a])

		if len(all_comb) == 0:
			# print("Debug 1.1: length of all_comb--0, interd_for_patent--0")
			num_of_single = num_of_single + 1
			continue

		if len(all_comb) == 1:
			if list(all_comb)[0] in ipc_comb_dict.keys():
				n = ipc_comb_dict[list(all_comb)[0]]
				elem1 = list(all_comb)[0][0]
				elem2 = list(all_comb)[0][1]
				interd_for_patent = ((n/ipc_freq_dict[elem1]) + (n/ipc_freq_dict[elem2]))/2

				# print("Debug 1.2: length of all_comb--1, interd_for_patent--", interd_for_patent)
			else:
				print("Warning 0: ", list(all_comb)[0], " not in ipc_comb_dict")
				interd_for_patent = 0
				num_warn0 = num_warn0 + 1

			result_dict[apn] = appdate + "|" + str(interd_for_patent)
			continue


		#--- the code below is for the case that len(all_comb) >= 3
		# print("Debug 1: all_comb--", all_comb)


		interd_for_patent_numerator = 0
		# print("Debug all ipcs: ", mg_symbols)
		for ipc in mg_symbols:
			set_curr = set()
			set_curr.add(ipc)
			# print("Debug no current: ", sorted(list(mg_symbols.difference(set_curr))))
			comb_no_current = set(combinations(sorted(list(mg_symbols.difference(set_curr))), 2))
			# print("Debug 2: comb_no_current--", comb_no_current)

			comb_for_current = all_comb.difference(comb_no_current)
			# print("Debug 3: comb_for_current--", comb_for_current)

			numerator = 0
			for c in comb_for_current:
				if c in ipc_comb_dict.keys():
					numerator = numerator + ipc_comb_dict[c]
				else:
					print("Warning 1: ", c, " not in ipc_comb_dict")
					num_warn1 = num_warn1 + 1

			denominator = 0
			if ipc in ipc_freq_dict.keys():
				denominator = ipc_freq_dict[ipc]
			else:
				print("Warning 2: ", ipc, " not in ipc_freq_dict")
				num_warn2 = num_warn2 + 1
				break;

			if denominator != 0:
				interd_for_ipc = numerator/denominator
				# print("Debug 4: interd_for_ipc--", ipc, " is ", interd_for_ipc)
				interd_for_patent_numerator = interd_for_patent_numerator + interd_for_ipc


		interd_for_patent = interd_for_patent_numerator/len(mg_symbols)
		# print("Debug 5: interd_for_patent--", interd_for_patent)
		result_dict[apn] = appdate + "|" + str(interd_for_patent)

output_file_name = "ipc_interd_score.txt"
with open(output_file_name, "w") as output_file:
	output_file.write("apn|appdate|interd_score"+"\n")
	for i in result_dict.keys():
		output_file.write(i + "|" + result_dict[i] + "\n")

print("Number of warning 0: ", num_warn0, " Number of warning 1: ", num_warn1, " Number of warning 2: ", num_warn2)
print("Number of entries with interd_score: ", len(result_dict.keys()))
print("Number of single ipcs: ", num_of_single)
print("Total number in 2006: ", total_counter)








