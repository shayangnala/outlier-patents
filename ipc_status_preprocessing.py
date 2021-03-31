
import csv
import pickle

ALL_PATENTS_FILE = "/Users/shayangnala/py_crawler/outlier_patent/pat_all_granted.csv"
# ALL_PATENTS_FILE = "/Users/shayangnala/py_crawler/outlier_patent/test_input.csv"

mon_pcount_dict = {}

# Example entries:
# {
# 	"1984 04": {
# 		"B29C51": 3,
# 		"H04J3": 5
# 	}
# }
mon_ipc_pcount_dict = {}

# read in all patents and process
with open(ALL_PATENTS_FILE) as all_patents_file:
	reader = csv.reader(all_patents_file)

	# print ("Debug 0 total count of rows: ", row_count)
	header_row = next(reader) # reader the header row

	for row in reader:
		apn = str(row[0])
		appdate = row[1]
		app = row[5]
		inv = row[6]
		ipcs = str(row[4]).split()

		# remove duplicates
		mg_symbols = set()
		for i in ipcs:
			mg = i.split('/')[0]
			mg_symbols.add(mg)


		# year-month to number of patents
		# year-month to {ipc: number of patents}

		y_month_key = " ".join(appdate.split("/")[:2]) # this looks like "1984 04"
		print(y_month_key)

		if y_month_key in mon_pcount_dict.keys():
			mon_pcount_dict[y_month_key] = mon_pcount_dict[y_month_key] + 1
		else:
			mon_pcount_dict[y_month_key] = 1


		if y_month_key in mon_ipc_pcount_dict.keys():
			ipcs_this_mon = mon_ipc_pcount_dict[y_month_key]

			for i in mg_symbols:
				if i in ipcs_this_mon.keys():
					ipcs_this_mon[i] = ipcs_this_mon[i] + 1
				else:
					ipcs_this_mon[i] = 1

		else:
			# construct a ipc:patent_count dict
			ipc_pcount_dict = {}
			for i in mg_symbols:
				ipc_pcount_dict[i] = 1

			mon_ipc_pcount_dict[y_month_key] = ipc_pcount_dict


	# print(mon_pcount_dict)
	# print(mon_ipc_pcount_dict["1986 05"])

	s_file_1 = open("mon_pcount_dict.pkl", "wb")
	pickle.dump(mon_pcount_dict, s_file_1)
	s_file_1.close()

	s_file_2 = open("mon_ipc_pcount_dict.pkl", "wb")
	pickle.dump(mon_ipc_pcount_dict, s_file_2)
	s_file_2.close()








		

