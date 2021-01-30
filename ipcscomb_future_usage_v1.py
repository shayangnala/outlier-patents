import csv
from time import sleep
from tqdm import tqdm

ALL_PATENTS_FILE = "/Users/shayangnala/py_crawler/outlier_patent/pat_all_granted.csv"

mgcomb_dict = {}

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

		if mg_string in mgcomb_dict.keys():
			mgcomb_dict[mg_string].append(apn+"+"+appdate)
		else:
			mgcomb_dict[mg_string] = [apn+"+"+appdate]

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
	writer.writerow(["mg_comb", "first patent", "num_usage", "usage history"])

	for comb in mgcomb_dict.keys():
		# write to a file
		patents = mgcomb_dict[comb]
		writer.writerow([comb, patents[0].split("+")[0], len(patents), " ".join(patents)])


print("Output file: " + output_file_name)






