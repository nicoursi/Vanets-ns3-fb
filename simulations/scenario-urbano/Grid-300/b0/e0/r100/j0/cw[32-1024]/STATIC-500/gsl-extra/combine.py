import os
import csv

# Folder containing the CSV files
folder_path = '.'  # change this to your actual folder path
output_file = 'compiled.csv'

with open(output_file, 'w', newline='') as outfile:
    writer = csv.writer(outfile)

    for filename in os.listdir(folder_path):
        if filename.endswith('.csv'):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, 'r', newline='') as infile:
                reader = csv.reader(infile)
                rows = list(reader)
                if len(rows) >= 2:
                    second_row = rows[1]
                    writer.writerow(second_row)
