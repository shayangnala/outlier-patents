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

total_counter = 0
new_pair_counter = 0

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


		numerator_for_patent = 0
		for j in mg_symbols:
			subset_without_j = mg_symbols.difference(j)

			numerator = 0
			for k in subset_without_j:
				pair = (j, k)
				if pair in ipc_comb_dict.keys():
					numerator = numerator + ipc_comb_dict[pair]
				else:
					new_pair_counter = new_pair_counter + 1

			K_j = numerator/ipc_freq_dict[j]
			numerator_for_patent = numerator_for_patent + K_j

		interd_for_patent = numerator_for_patent/len(mg_symbols)

		result_dict[apn] = appdate + "|" + str(interd_for_patent)

output_file_name = "ipc_interd_score.txt"
with open(output_file_name, "w") as output_file:
	output_file.write("apn|appdate|interd_score"+"\n")
	for i in result_dict.keys():
		output_file.write(i + "|" + result_dict[i] + "\n")

print("Total number in 2006: ", total_counter)
print("Number of new pairs in 2006: ", new_pair_counter)








