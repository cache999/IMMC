"""script to download all data from Elo"""
import bs4
import urllib.request
import csv
import os
from collections import defaultdict

# ------------ Variable definitions -----------------
# Used for name_gen
MONTHS_DICT = {
    'January': '01',
    'February': '02', 'March': '03',
    'April': '04',
    'May': '05',
    'June': '06',
    'July': '07',
    'August': '08',
    'September': '09',
    'October': '10',
    'November': '11',
    'December': '12',
}

basedir = "elo_data/"
modified_dir = "elo_data_interpolated/"
basestr = "https://ratings.fide.com/toparc.phtml?cod="
# Range: 001 - 641, every 4th one
urls = [basestr + '0' * (2 - len(str(i))) + str(i) for i in range(1, 641+1, 4)]
num_pages = 640 // 4  # unused

# Identifiers to pick out the month-year
front_id = "Top 100 Players"
back_id = " FIDE"


# ---------------- Downloading data -----------------

def get_data(url):
    headers = "RankNameTitleCountryRatingGamesB-Year"
    webpage = str(urllib.request.urlopen(url).read())
    soup = bs4.BeautifulSoup(webpage)
    text = soup.get_text()

    # Obtain the month-year of data to use as file name
    text = text[text.find(front_id):]
    month_year = text[16:text.find(back_id)].split(' ')  # Skips the front_id, and back_id
    name = convert_time(month_year)

    text = text[text.find(headers):]  # Gets rid of everything before headers
    text = text[:text.find('\\n')]  # Gets rid of everything after the 100th player
    splitted = text.split('\xa0')[1:]


    parsed = [["Name", "Rating"]]
    for i in range(100):
        parsed.append(splitted[7 * i:7 * (i + 1)])
        player_name_components = parsed[i+1][1].split(', ')
        player_name = player_name_components[1] + ' ' + player_name_components[0]
        parsed[i+1] = [player_name, int(parsed[i+1][4])]  # Select only the name and rating

    with open(basedir + name + ".csv", "w", newline='', encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerows(parsed)

def convert_time(month_year):
    return month_year[1] + MONTHS_DICT[month_year[0]]

#for url in urls:
#    get_data(url)


# ---------------- Interpolation ------------------
# NOTE: This part of the code is super messy and complicated. Please call me to explain instead of reading it
# Helper function to generate file names from file_dex
def name_gen(file_dex):
    year = 2000 + (file_dex + 6) // 12  # +6 to adjust for start on 200007
    month = (file_dex + 6) % 12 + 1
    return str(year) + '0' * (len(str(month)) == 1) + str(month)

# The months where we want data; includes the month-year of true data
months_needed = []
years = list(range(2001, 2012+1))  # The data is only non-monthly before 2012
for m in range(7, 12+1):
    months_needed.append("2000" + '0' * (len(str(m)) == 1) + str(m))
for y in years:
    for m in range(1, 12+1):
        months_needed.append(str(y) + '0' * (len(str(m)) == 1) + str(m))

# Get a list of the data we already have
true_data_names = os.listdir(basedir)
for i in range(len(true_data_names)):
    true_data_names[i] = true_data_names[i][:-4]
true_data_names = true_data_names[:true_data_names.index("201301")]  # Truncate everything after 2013
num_true = len(true_data_names)

# map from true_name to its index (int)
mapping = [(true_entry, months_needed.index(true_entry)) for true_entry in true_data_names]

# Unused optimization - too many errors and complications
'''
# Download the data we have in the range Jul 2000 - Dec 2012
for name in true_data_names:
    with open(basedir + name + '.csv', mode="r", encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        current_data = list(reader)
    true_data[mapping[name]] = current_data
'''

# Interpolating the data. This part of the code is ultra-bad so pls call me to explain instead of reading
# Function that interpolates given frontdex and backdex
def interpolate(front, back):
    diff = back - front

    # Get front and back data
    with open(basedir + name_gen(front) + '.csv', mode="r", encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        front_data = list(reader)[1:]  # Skip header
        for i in range(len(front_data)):
            front_data[i][1] = float(front_data[i][1])
    with open(basedir + name_gen(back) + '.csv', mode="r", encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        back_data = list(reader)[1:]  # Skip header
        for i in range(len(back_data)):
            back_data[i][1] = float(back_data[i][1])

    # Interpolate
    front_name_list = [row[0] for row in front_data]
    back_name_list = [row[0] for row in back_data]
    for i in range(1, diff):  # There are diff - 1 elements in-between
        new_data = [["Name", "Rating"]]
        new_scores = []  # Unsorted for now, will sort after getting all the data in this array
        for row in front_data:
            name = row[0]
            if name in back_name_list:
                # Interpolation!!! Second term is i * (score in back_data). Divided by diff, then rounded
                new_scores.append([name, int(((diff - i) * row[1] +
                                          i * (back_data[back_name_list.index(name)][1])) / diff)])
            else:
                new_scores.append([name, row[1]])

        # Check the other list as well
        for row in back_data:
            if row[0] in front_name_list:
                continue
            else:
                new_scores.append([row[0], row[1]])

        # Sort all the entries in descending order of scores
        new_scores.sort(reverse=True, key=lambda x: x[1])
        new_scores = new_scores[:100]  # Only keep top 100
        new_data.extend(new_scores)

        with open(modified_dir + name_gen(front + i) + '.csv', mode="w", encoding="utf-8", newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            writer.writerows(new_data)

# For every two consecutive elements in true_data_names, finds the sublist of entries in months_needed in between
file_dex = 0
for i in range(num_true - 1):  # Skip last element
    frontdex, backdex = mapping[i][1], mapping[i+1][1]
    diff = backdex - frontdex
    if diff == 1:
        file_dex = backdex + 1
        continue
    else:  # there is a jump, so apply interpolation
        interpolate(frontdex, backdex)  # This function does ALL the heavy-lifting.
        file_dex += 1
