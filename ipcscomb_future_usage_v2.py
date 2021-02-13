import csv
from time import sleep
from tqdm import tqdm
from itertools import combinations


ALL_PATENTS_FILE = "/Users/shayangnala/py_crawler/outlier_patent/pat_all_granted.csv"
# ALL_PATENTS_FILE = "/Users/shayangnala/py_crawler/outlier_patent/test_input.csv"

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

usage_output_file_name = "ipcscomb_usage_v2.csv"
# output the result
with open(usage_output_file_name, 'w') as output_csv:
	writer = csv.writer(output_csv)
	# write header row
	writer.writerow(["mg_comb", "first_patent_apn", "year", "t_start", "time", "num_usage_of_year", "usage_history"])

	for comb in mgcomb_dict.keys():
		# write to a file
		usages = mgcomb_dict[comb][0]
		adjs = mgcomb_dict[comb][1]

		year_to_usage = {}

		t_start = usages[0].split("+")[1].split("/")[0]
		# split the years
		for item in usages:
			elems = item.split("+")
			year = elems[1].split("/")[0]
			apn = elems[2]
			if year in year_to_usage:
				year_to_usage[year].append(apn)
			else:
				year_to_usage[year] = []
				year_to_usage[year].append(apn)


		for y in year_to_usage:
			writer.writerow([comb, usages[0].split("+")[2], y, t_start, int(y)-int(t_start), len(year_to_usage[y]), " ".join(year_to_usage[y])])


print("Output usage file: " + usage_output_file_name)

adj_output_file_name = "ipcscomb_adj_v2.csv"
# output the result
with open(adj_output_file_name, 'w') as output_csv:
	writer = csv.writer(output_csv)
	# write header row
	writer.writerow(["mg_comb", "first_patent_apn", "year", "t_start", "time", "num_adj_of_year", "adj_history"])

	for comb in mgcomb_dict.keys():
		# write to a file
		usages = mgcomb_dict[comb][0]
		adjs = mgcomb_dict[comb][1]

		year_to_usage = {}

		t_start = usages[0].split("+")[1].split("/")[0]
		# split the years
		for item in adjs:
			elems = item.split("+")
			year = elems[1].split("/")[0]
			apn = elems[2]
			if year in year_to_usage:
				year_to_usage[year].append(apn)
			else:
				year_to_usage[year] = []
				year_to_usage[year].append(apn)


		for y in year_to_usage:
			writer.writerow([comb, usages[0].split("+")[2], y, t_start, int(y)-int(t_start), len(year_to_usage[y]), " ".join(year_to_usage[y])])

print("Output adj file: " + adj_output_file_name)









