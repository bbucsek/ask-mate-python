import csv


def read_csv(filename):
    dict_list= []
    with open(filename, 'r') as csv_file:
        data = csv.DictReader(csv_file)
        for row in data:
            new_dict = {}
            for k, v in row.items():
                new_dict[k] = v
            dict_list.append(new_dict)
    return dict_list

def write_csv(dict_list, filename, headers):
    with open(filename, 'w') as csv_file:
        writer = csv.DictWriter(csv_file, headers)
        writer.writeheader()
        writer.writerows(dict_list)