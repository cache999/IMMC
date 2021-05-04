import os
import csv
from collections import defaultdict
import matplotlib.pyplot as plt

# ------------- Changeable parameters --------------
# top n players' median are taken, i.e. for n=10 the 5.5-th rating is the median
n = 10
# power of the integrand
k = 2
# Bounds of the integral, written [year][month]
lower_lim = "195001"
upper_lim = "202105"

# In units of months; 1 is the smallest. Currently useless
time_step = 1


# ---------- Determine integration mode ------------
# Checks bounds of integration to select correct integration mode
# NOTE: May not need this, if we already do all the changes in the data processing.
def check_integration_mode(lower, upper):
    divide_years = False
    return

# ------------- Importing data ---------------------
# Imports data from /final_ratings
dataset = []
basepath = "final_ratings/"
for entry in os.listdir(basepath):
    dataset.append(basepath + entry)

# Filter the data based on bounds
lower_index = dataset.index(basepath + lower_lim + '.csv')
upper_index = dataset.index(basepath + upper_lim + '.csv')
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
# Positions of medians, counted from 0
medians = [n//2 - 1, n//2] if n % 2 == 0 else [n//2, n//2]

# Calculate the integral
# Assumes all the files listed in dataset are incremented monthly
for month in dataset:
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
