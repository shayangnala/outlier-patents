import csv
from time import sleep
from tqdm import tqdm
from itertools import combinations


ALL_PATENTS_FILE = "/Users/shayangnala/py_crawler/outlier_patent/pat_all_granted.csv"

mgcomb_dict = {}

mgadj_dict = {}

# Given a set of strings with length n
# generate all possible subset with length of n - 1
def one_elem_less_subset(orig_set):
	if len(orig_set) == 1:
		return []

	l = list(combinations(orig_set, len(orig_set)-1))

	result_str = []
	for elem in l:
		result_str.append(" ".join(sorted(elem)))

	return result_str

# read in all patents and process
with open(ALL_PATENTS_FILE) as all_patents_file:
	reader = csv.reader(all_patents_file)

	# count total number of rows in the input csv file
	# row_count = sum(1 for row in reader)
	# print ("Debug 0 total count of rows: ", row_count)
	header_row = next(reader) # reader the header row

	# pbar = tqdm(total=row_count)

	for row in reader:
		apn = str(row[0])
		appdate = row[1]
		ipcs = str(row[4]).split()

		mg_symbols = set()
		for i in ipcs:
			mg = i.split('/')[0]
			mg_symbols.add(mg)
			# turn the set into a string with main group symbols in sorted order
			mg_string = " ".join(sorted(list(mg_symbols)))

		# if this patent is <one more step> ajacencies of previous patents
		subsets = one_elem_less_subset(mg_symbols)

		if mg_string in mgcomb_dict.keys():
			mgcomb_dict[mg_string][0].append("0+"+appdate+"+"+apn)
		else:
			mgcomb_dict[mg_string] = [["0+"+appdate+"+"+apn], []]


		for s in subsets:
			if s in mgcomb_dict.keys():
				mgcomb_dict[s][1].append("1+"+appdate+"+"+apn)


		print("Debug 1: ", apn, " ", appdate, " ", mg_string)

		# update the progress bar
		# sleep(0.1)
		# pbar.update(1)

	# pbar.close()

output_file_name = "ipcscomb_usage.csv"
# output the result
with open(output_file_name, 'w') as output_csv:
	writer = csv.writer(output_csv)
	# write header row
	writer.writerow(["mg_comb", "first patent", "num_usage", "usage history", "num_adj", "adjs"])

	for comb in mgcomb_dict.keys():
		# write to a file
		usages = mgcomb_dict[comb][0]
		adjs = mgcomb_dict[comb][1]
		writer.writerow([comb, usages[0].split("+")[2], len(usages), " ".join(usages), len(adjs), " ".join(adjs)])


print("Output file: " + output_file_name)






