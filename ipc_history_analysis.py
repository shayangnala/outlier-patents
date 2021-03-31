import csv
from time import sleep
from tqdm import tqdm

ALL_PATENTS_FILE = "/Users/shayangnala/py_crawler/outlier_patent/pat_all_granted.csv"
# ALL_PATENTS_FILE = "/Users/shayangnala/py_crawler/outlier_patent/test_input.csv"

mgcomb_dict = {}

ipc_usage_dict = {}

ipc_comb_dict = {}

def register_ipc_usage(ipcs):
	for i in ipcs:
		if i in ipc_usage_dict.keys():
			ipc_usage_dict[i] = ipc_usage_dict[i] + 1
		else:
			ipc_usage_dict[i] = 1

		# print("Debug new 2: ", i, " count---", ipc_usage_dict[i])

def register_ipc_comb(ipcs):
	for i in ipcs:
		other_ipcs = ipcs-set([i])
		# print("Debug new 1: i--", i , " other_ipcs--", other_ipcs)
		if i in ipc_comb_dict.keys():
			ipc_comb_dict[i].update(other_ipcs)
		else:
			ipc_comb_dict[i] = set(other_ipcs)


def compute_interdependence(ipcs):
	## what if it is not ever combined with others
	sum_ei = 0
	for i in ipcs:
		if (i in ipc_comb_dict.keys()) & (i in ipc_usage_dict.keys()):
			sum_ei = sum_ei + len(ipc_comb_dict[i])/ipc_usage_dict[i]

	interdependence = 0
	if sum_ei != 0:
		interdependence = round(len(ipcs)/sum_ei, 2)

	# print("Debug new 3: ipcs---", ipcs, " sum_ei---", sum_ei, " interd---", interdependence)

	return interdependence


# read in all patents and process
with open(ALL_PATENTS_FILE) as all_patents_file:
	reader = csv.reader(all_patents_file)

	# print ("Debug 0 total count of rows: ", row_count)
	header_row = next(reader) # reader the header row

	# pbar = tqdm(total=row_count)

	for row in reader:
		apn = str(row[0])
		appdate = row[1]
		app = row[5]
		inv = row[6]
		ipcs = str(row[4]).split()

		mg_symbols = set()
		for i in ipcs:
			mg = i.split('/')[0]
			mg_symbols.add(mg)
			# turn the set into a string with main group symbols in sorted order
			mg_string = " ".join(sorted(list(mg_symbols)))

		interd = compute_interdependence(mg_symbols)

		if mg_string in mgcomb_dict.keys():
			mgcomb_dict[mg_string].append(apn+"+"+appdate+"+"+app+"+"+inv+"+"+str(interd))
		else:
			mgcomb_dict[mg_string] = [apn+"+"+appdate+"+"+app+"+"+inv+"+"+str(interd)]

		print("Debug 1: ", apn, " ", appdate, " ", mg_string, " ", app, " ", inv, " ", interd)

		# ipc usage
		register_ipc_usage(mg_symbols)

		# ipc combination
		register_ipc_comb(mg_symbols)

		# update the progress bar
		# sleep(0.1)
		# pbar.update(1)

	# pbar.close()

output_file_name = "ipc_history_analysis_output.csv"
# output the result
with open(output_file_name, 'w') as output_csv:
	writer = csv.writer(output_csv)
	# write header row
	writer.writerow(["mg_comb", "interd_score", "num_first_patents", "first patents", "app", "inv", "num_usage", "usage history", "appdate", "first_follower_date", "first_follower_app", "first_follower_inv", "second_follower_date", "third_follower_date", "fourth_follower_date", "fifth_follower_date"])

	for comb in mgcomb_dict.keys():
		# write to a file
		patents = mgcomb_dict[comb]
	
		usages = []

		orig_p = patents[0].split("+")
		orig_apn = orig_p[0].strip()
		orig_appdate = orig_p[1].strip()
		orig_app = orig_p[2].strip()
		orig_inv = orig_p[3].strip()
		interd = orig_p[4]
		first_patents = [orig_apn]
		first_apps = [orig_app]
		first_invs = [orig_inv]

		i = 1
		while i < len(patents):
			item = patents[i]

			this_p = item.split("+")
			this_apn = this_p[0].strip()
			this_appdate = this_p[1].strip()
			this_app = this_p[2].strip()
			this_inv = this_p[3].strip()

			if this_appdate == orig_appdate:
				first_patents.append(this_apn)
				first_apps.append(this_app)
				first_invs.append(this_inv)
				i = i + 1
				continue

			# follower cannot be the same as the originator
			if this_app != orig_app and this_inv != orig_inv:
				usages.append(this_apn+"+"+this_appdate+"+"+this_app+"+"+this_inv)

			i = i + 1

		if len(usages) > 4:
			first_follower_date = usages[0].split("+")[1]
			second_follower_date = usages[1].split("+")[1]
			third_follower_date = usages[2].split("+")[1]
			fourth_follower_date = usages[3].split("+")[1]
			fifth_follower_date = usages[4].split("+")[1]
			writer.writerow([comb, interd, len(first_patents), " ".join(first_patents), "|".join(first_apps), "|".join(first_invs), len(usages), " ".join(usages), orig_appdate, first_follower_date, usages[0].split("+")[2], usages[0].split("+")[3], second_follower_date, third_follower_date, fourth_follower_date, fifth_follower_date])
		elif len(usages) > 3:
			first_follower_date = usages[0].split("+")[1]
			second_follower_date = usages[1].split("+")[1]
			third_follower_date = usages[2].split("+")[1]
			fourth_follower_date = usages[3].split("+")[1]
			writer.writerow([comb, interd, len(first_patents), " ".join(first_patents), "|".join(first_apps), "|".join(first_invs), len(usages), " ".join(usages), orig_appdate, first_follower_date, usages[0].split("+")[2], usages[0].split("+")[3], second_follower_date, third_follower_date, fourth_follower_date])
		elif len(usages) > 2:
			first_follower_date = usages[0].split("+")[1]
			second_follower_date = usages[1].split("+")[1]
			third_follower_date = usages[2].split("+")[1]
			writer.writerow([comb, interd, len(first_patents), " ".join(first_patents), "|".join(first_apps), "|".join(first_invs), len(usages), " ".join(usages), orig_appdate, first_follower_date, usages[0].split("+")[2], usages[0].split("+")[3], second_follower_date, third_follower_date])
		elif len(usages) > 1:
			first_follower_date = usages[0].split("+")[1]
			second_follower_date = usages[1].split("+")[1]
			writer.writerow([comb, interd, len(first_patents), " ".join(first_patents), "|".join(first_apps), "|".join(first_invs), len(usages), " ".join(usages), orig_appdate, first_follower_date, usages[0].split("+")[2], usages[0].split("+")[3], second_follower_date])
		elif len(usages) > 0:
			first_follower_date = usages[0].split("+")[1]
			writer.writerow([comb, interd, len(first_patents), " ".join(first_patents), "|".join(first_apps), "|".join(first_invs), len(usages), " ".join(usages), orig_appdate, first_follower_date, usages[0].split("+")[2], usages[0].split("+")[3]])
		else:
			writer.writerow([comb, interd, len(first_patents), " ".join(first_patents), "|".join(first_apps), "|".join(first_invs), len(usages), " ".join(usages), orig_appdate])


print("Output file: " + output_file_name)






