import os
import csv
from collections import defaultdict
import matplotlib.pyplot as plt

# ------------- Changeable parameters --------------
# top n players' median are taken, i.e. for n=10 the 5.5-th rating is the median
n = 10
# power of the integrand
k = 2

# In units of months; 1 is the smallest. Currently useless
time_step = 1


# ------------- Importing data ---------------------
# Imports data from /chessmetrics_data_parsed
dataset = []
basepath = "chessmetrics_data_parsed/"
for entry in os.listdir(basepath):
    dataset.append(basepath + entry)


# ------------- Calculate integral -----------------

# Initialize variables
dom_ratings = defaultdict(float)
current_pass = 0
# Positions of medians, counted from 0
medians = [n//2 - 1, n//2] if n % 2 == 0 else [n//2, n//2]

# Calculate the integral
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
            diff = int(row[1]) - median_val
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
