"""Takes the average of CMR and ELO for Jul 2000 - Jan 2005"""
import os
import csv

new_dir = "averaged_ratings/"

# Load CMR
cmr_data = []
cmr_dir = "chessmetrics_data_parsed/"
for entry in os.listdir(cmr_dir):
    cmr_data.append(cmr_dir + entry)
start = cmr_data.index(cmr_dir + "200007.csv")
end = cmr_data.index(cmr_dir + "200501.csv")
cmr_data = cmr_data[start:end+1]

# Load ELO
elo_data = []
elo_dir = "elo_data_interpolated/"
for entry in os.listdir(elo_dir):
    elo_data.append(elo_dir + entry)
start = elo_data.index(elo_dir + "200007.csv")
end = elo_data.index(elo_dir + "200501.csv")
elo_data = elo_data[start:end+1]

# Combining both
for cmr, elo in zip(cmr_data, elo_data):
    # Get front and back data
    with open(cmr, mode="r", encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        cmr_data_entry = list(reader)[1:]  # Skip header
        for i in range(len(cmr_data_entry)):
            cmr_data_entry[i][1] = float(cmr_data_entry[i][1])
    with open(elo, mode="r", encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        elo_data_entry = list(reader)[1:]  # Skip header
        for i in range(len(elo_data_entry)):
            elo_data_entry[i][1] = float(elo_data_entry[i][1])

    cmr_name_list = [row[0] for row in cmr_data_entry]
    elo_name_list = [row[0] for row in elo_data_entry]
    filename = elo[22:-4]  # 22 is to account for the substring that is the path

    new_scores = []
    new_data = [["Name", "Rating"]]

    # Check cmr list first
    for row in cmr_data_entry:
        name = row[0]
        if name in elo_name_list:
            # Crucial formula to combine both metrics
            # Currently using: arithmetic mean (A+B)/2
            score = int(0.5 * (float(row[1]) + float(elo_data_entry[elo_name_list.index(name)][1])))
            new_scores.append([name, score])
        else:
            new_scores.append([name, int(row[1])])

    # Check the other list as well
    for row in elo_data_entry:
        if row[0] in cmr_name_list:
            continue
        else:
            new_scores.append([row[0], int(row[1])])

    # Sort the data (see elo_data_gen.py)
    new_scores.sort(reverse=True, key=lambda x: x[1])
    new_scores = new_scores[:100]  # Only keep top 100
    new_data.extend(new_scores)

    # Write stuff!
    with open(new_dir + filename + '.csv', mode="w", encoding="utf-8", newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerows(new_data)
