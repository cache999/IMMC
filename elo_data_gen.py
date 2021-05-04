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
'''
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
        parsed[i+1] = [player_name, parsed[i+1][4]]  # Select only the name and rating

    with open(basedir + name + ".csv", "w", newline='', encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerows(parsed)

def convert_time(month_year):
    return month_year[1] + MONTHS_DICT[month_year[0]]

for url in urls:
    get_data(url)
'''

# ---------------- Interpolation ------------------
# The months where we want data; includes the month-year of true data
months_needed = []
years = list(range(2001, 2012+1))  # The data is only non-monthly before 2012
for m in range(7, 12+1):
    months_needed.append("2000" + '0' * (len(str(m)) == 1) + str(m))
for y in years:
    for m in range(1, 12+1):
        months_needed.append(str(y) + '0' * (len(str(m)) == 1) + str(m))

# Get a list of the data we already have
true_data = os.listdir(basedir)
for i in range(len(true_data)):
    true_data[i] = true_data[i][:-4]
true_data = true_data[:true_data.index("201301")]  # Truncate everything after 2013
num_true = len(true_data)

# Interpolating the data
mapping = [(true_entry, months_needed.index(true_entry)) for true_entry in true_data]
# For every two consecutive elements in true_data, find the sublist of entries in months_needed in between
file_dex = 0
for i in range(num_true - 1):  # Skip last element
    frontdex, backdex = mapping[i][1], mapping[i+1][1]
    diff = backdex - frontdex
    if diff == 1:
        file_dex = backdex + 1
        continue
    else:  # there is a jump, so apply interpolation

        pass

    file_dex += 1

# Helper function to generate file names from file_dex
def name_gen(file_dex):
    year = 2000 + (file_dex + 6) // 12  # +6 to adjust for start on 200007
    month = (file_dex + 6) % 12 + 1
    return str(year) + '0' * (len(str(month)) == 1) + str(month)

# Interpolating given frontdex and backdex
def interpolate(front, back):
    diff = back - front
    for i in range(1, diff):  # There are diff - 1 elements in-between
        new_data = [["Name", "Rating"]]
        with open(basedir + name_gen(front) + '.csv', mode="r") as csvfile:
            reader = csv.reader(csvfile, delimiter=',', encoding="utf-8")
            front_data = list(reader)
            print(front_data)
interpolate(3, 6)
