import csv
from itertools import combinations
import pickle

ALL_PATENTS_FILE = "/Users/shayangnala/py_crawler/outlier_patent/pat_all_granted.csv"
# ALL_PATENTS_FILE = "/Users/shayangnala/py_crawler/outlier_patent/test_input.csv"
END_YEAR = 2005

ipc_comb_dict = {}

ipc_freq_dict = {}

# read in all patents and process
with open(ALL_PATENTS_FILE) as all_patents_file:
	reader = csv.reader(all_patents_file)
	header_row = next(reader) # reader the header row

	for row in reader:
		apn = str(row[0])
		ipcs = str(row[4]).split()
		appdate = row[1]
		print("Debug 1: ", appdate)

		if int(appdate.split("/")[0]) > END_YEAR:
			break		

		mg_symbols = set()
		for i in ipcs:
			mg = i.split('/')[0]
			mg_symbols.add(mg)

		# co-occurrence frequencies for all subclass combinations
		for j in combinations(sorted(list(mg_symbols)), 2):

			# 1. store the sorted order			
			if j in ipc_comb_dict.keys():
				ipc_comb_dict[j] = ipc_comb_dict[j] + 1
			else:
				ipc_comb_dict[j] = 1

			# 2. store the reversed order
			reversed_j = (j[1], j[0])
			if reversed_j in ipc_comb_dict.keys():
				ipc_comb_dict[reversed_j] = ipc_comb_dict[reversed_j] + 1
			else:
				ipc_comb_dict[reversed_j] = 1

		for k in mg_symbols:
			if k in ipc_freq_dict.keys():
				ipc_freq_dict[k] = ipc_freq_dict[k] + 1
			else:
				ipc_freq_dict[k] = 1


s_file_1 = open("ipc_comb_dict.pkl", "wb")
pickle.dump(ipc_comb_dict, s_file_1)
s_file_1.close()

s_file_2 = open("ipc_freq_dict.pkl", "wb")
pickle.dump(ipc_freq_dict, s_file_2)
s_file_2.close()


print("Length of ipc_comb_dict: ", len(ipc_comb_dict.keys()))
print("Length of ipc_freq_dict: ", len(ipc_freq_dict.keys()))
