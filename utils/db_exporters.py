import csv


def influx2csv(query_set, csv_path):
    raw_data = query_set.get_points()
    first = next(raw_data)
    with open(csv_path, 'w', newline='') as export_file:
        writer = csv.DictWriter(export_file, first.keys())
        writer.writeheader()
        writer.writerow(first)
        for data in raw_data:
            writer.writerow(data)
