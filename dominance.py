import os
import csv
from collections import defaultdict
import matplotlib.pyplot as plt

# ------------- Changeable parameters --------------
# top n players' median are taken, i.e. for n=10 the 5.5-th rating is the median
n = 10
# power of the integrand
k = 10
# Bounds of the integral, written [year][month]. Leave blank to integrate over all the data
lower_lim = "184301"
upper_lim = "202105"
try:
    assert lower_lim <= upper_lim
except AssertionError:
    print("Error - lower limit must be <= upper limit")

# In units of months; 1 is the smallest. Currently useless
time_step = 1

# ------------- Importing data ---------------------
# Imports data from /final_ratings
basepath = "final_ratings/"
len_basepath = len(basepath)

if lower_lim == upper_lim:
    dataset = [basepath + lower_lim + '.csv']
else:
    dataset = []
    for entry in os.listdir(basepath):
        dataset.append(basepath + entry)

    # Filter the data based on bounds
    try:
        lower_index = dataset.index(basepath + lower_lim + '.csv')
    except ValueError:
        lower_index = -1

    try:
        upper_index = dataset.index(basepath + upper_lim + '.csv')
    except ValueError:
        upper_index = -1

    if lower_index != -1:
        dataset = dataset[lower_index:]
    if upper_index != -1:
        if upper_index == len(dataset) - 1:  # last element:
            dataset = dataset[:-1]
        else:
            dataset = dataset[:upper_index]

# ------------- Calculate integral -----------------

# Initialize variables
dom_ratings = defaultdict(float)
current_pass = 0
'''
# Helper function to get number of months between two year-months:
def find_interval(first, last):
    years = int(first[:4]), int(last[:4])
    months = int(first[4:]), int(last[4:])
    diff_year = years[1] - years[0]
    diff_month = months[1] - months[0]
    return diff_year * 12 + diff_month + 1
interval = find_interval(dataset[0][len_basepath:-4], dataset[-1][len_basepath:-4])
'''

# Positions of medians, counted from 0
medians = [n//2 - 1, n//2] if n % 2 == 0 else [n//2, n//2]
def use_month_filter(month_year):
    if month_year >= "195001":
        return True
    else:
        with open(basepath + month_year + '.csv', mode="r", encoding="utf-8") as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            row_count = sum(1 for row in reader)
            row_count = row_count - 2  # Remove header and adjust for zero-indexed median value
            if row_count < medians[1]:
                return False
        return True

# Calculate the integral
# Assumes all the files listed in dataset are incremented monthly
for month in dataset:
    # Filter the month
    month_year = month[len(basepath):-4]
    if not use_month_filter(month_year):
        continue
    else:
        # Calculates the ratings for every player that is in the dataset
        with open(month, mode="r", encoding="utf-8") as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            rows = list(reader)[1:]

            # Calculate the median
            median_val = 0
            for pos in medians:
                median_val += int(rows[pos][1])
            median_val /= 2

            # Calculates ratings for every player
            for row in rows:
                name = row[0]
                diff = float(row[1]) - median_val
                diff /= 100  # Scale the numbers down; the gaps are usually around 10^1 or 10^2
                if diff < 0:
                    diff = 0
                dom_ratings[name] += pow(diff, k)


# ------------- Display results --------------------
print("There are", len(dom_ratings), "unique players")

# Bar chart with matplotlib
# Only display the top 10 players

sorted_arr = [[k, dom_ratings[k]] for k in sorted(dom_ratings, key=dom_ratings.get, reverse=True)]
truncated = sorted_arr[:10]  # only keep top 10 players
pairs = list(map(list, zip(*truncated)))  # Transpose the list to get key array and val array

fig = plt.figure(figsize=(12, 4))  # set canvas size
plt.tick_params(axis='x', labelsize=5)  # Set the x-axis label size

plt.bar(*pairs)
plt.show()
fig.savefig('temp.png', dpi=fig.dpi)  # Saves figure to same directory
