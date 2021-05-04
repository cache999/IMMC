"""Currently successfully parses all data from the first data sheet"""
import os
import csv

basepath = "chessmetrics_data_#2_csv/"
set2 = []
for entry in os.listdir(basepath):
    set2.append(basepath + entry)

def name_gen(file_count):
    year = str(1965 + ((file_count + 9) // 12))  # 1965 instead of 1950 for second sheet
    month = str((file_count - 3) % 12 + 1)  # weird formulas to adjust for start on Nov 1965
    return year + '0' * (len(month) == 1) + month

def name_gen_2(file_name):  # quick fix, only for datasheet 1
    num = file_name[28:-4]
    return name_gen(int(num))


file_count = 0
for file in set2:
    line_count = 0
    name = name_gen_2(file)  # year-month of current file
    parsed_arr = [["Player Name", "Rating"]]
    with open(file, mode="r", encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for _ in range(6):  # Skips headers
            next(reader)
            line_count = line_count + 1
        for row in reader:
            parsed_arr.append(row[1:3])
            line_count = line_count + 1

    # Validate that the data is the right length
    if line_count != 106:
        print(file_count)
        raise ValueError

    # Write in another csvfile in parsed
    with open("chessmetrics_data_parsed/" + name + ".csv", mode="w", encoding="utf-8", newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        # writer.writerows(parsed)
        writer.writerows(parsed_arr)

    file_count = file_count + 1


'''used in v1a for the first data sheet
# Obtain a list of all csvfiles in the first dataset
basepath = "chessmetrics_data_#1_csv/"
set1 = []
for entry in os.listdir(basepath):
    set1.append(basepath + entry)
# print(set1)

def name_gen(file_count):
    year = str(1950 + (file_count // 12))
    month = str(file_count % 12 + 1)
    return year + '0' * (len(month) == 1) + month
# print(name_gen(12))

# v1b fixed weird duplicate data error with sheets 22 and 23
def name_gen_2(file_name):  # quick fix, only for datasheet 1
    num = file_name[28:-4]
    if not num.isnumeric():
        return "195002"
    elif num == "01":
        return "195001"
    elif num == "22":
        return "196511"
    elif num == "23":
        return "196512"
    elif int(num) < 22:
        return name_gen(int(num))
    elif int(num) > 23:
        return name_gen(int(num) - 2)

file_count = 0
for file in set1:
    line_count = 0
    name = name_gen_2(file)  # year-month of current file
    # print(name)
    parsed_arr = [["Player Name", "Rating"]]
    with open(file, mode="r", encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for _ in range(6):  # Skips headers
            next(reader)
            line_count = line_count + 1
        for row in reader:
            parsed_arr.append(row[1:3])
            line_count = line_count + 1

    # Validate that the data is the right length
    if line_count != 106:
        print(file_count)
        raise ValueError

    # Write in another csvfile in parsed
    with open("chessmetrics_data_parsed/" + name + ".csv", mode="w", encoding="utf-8", newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        # writer.writerows(parsed)
        writer.writerows(parsed_arr)

    file_count = file_count + 1
'''
