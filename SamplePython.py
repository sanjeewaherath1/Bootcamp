def myfunc(n):
    return abs(n - 50)


thislist = [100, 50, 65, 82, 23]
thislist.sort(key=myfunc)
print(thislist)

rating_list = [0.0, 1.1, 2.0, 0.1, 0.0]

count = 0
for i in range(len(rating_list)):
    if rating_list[i] <= 0.0:
        count = count + 1

print('count', count)

non_zero_count = sum(1 for x in rating_list if x <= 0.0)
print(non_zero_count)
print(len(rating_list))

thislist = ["apple", "banana", "cherry", "orange", "kiwi", "melon", "mango"]
print(thislist[-3:])
if "apple" in thislist:
    print("Apple found")

thislist.sort()
print(thislist)
newlist = [x for x in thislist if 'a' in x]
print(newlist)

thislist = ["apple", "banana", "cherry", "orange", "kiwi", "mango"]
thislist[1:3] = ["blackcurrant", "watermelon", 'AAA']
print(thislist)

thislist = ["apple", "banana", "cherry"]
thislist.insert(2, "watermelon")
print(thislist)

thislist = ["apple", "banana", "cherry"]
tropical = ["mango", "pineapple", "cherry"]
thislist.extend(tropical)
print(thislist)

thislist = ["apple", "banana", "cherry"]
thislist.pop()
print(thislist)

thislist = ["apple", "banana", "cherry"]
print(thislist)
thislist.clear()
print(thislist)
'''
x = int(input("Enter a number: "))
for i in range (0,x) :
    print('hello world ', i)


# !/usr/bin/python
import os

for f1 in os.listdir("D:\\Research\\Python"):
    print(f1)

print(os.getcwd())

filename1 = "D:\\Research\\Python\\myfile.txt"
filename2 = "D:\\Research\\Python\\myfile1.txt"

print(filename1)
print( os.path.exists(filename1) )

with open(filename1) as f1:
    # file read can happen here

    print("file exists")

    print(f1.readlines())

with open(filename2, "w") as f2:
    print("file write happening here")

    f2.write("Sanjeewa \n Jeewani \n")


x = int(input("Enter a number: "))
import sys
if x > 2:
    print(sys.path)
    print(sys.version)

str1 = 'This is first string'
str2 = "This is second string"

print(str1)
print(str2)

print(type(x))
print(type(str(x)))
print(float(x))



# fruits = ["apple", "banana", "cherry"]
fruits = [1, 2, 3]
x, y, z = fruits
print(x)
print(y)
print(z)

# thistuple = ("apple", "banana", "cherry")
thistuple = (1, 2, 3, 4, 5)
print(thistuple[0])

thistuple = ("apple",)
print(type(thistuple))

#NOT a tuple
thistuple = ("apple")
print(type(thistuple))


def gcd(a, b):
    # Write your code here
    # print('call function a=', a, 'b=', b)
    if a > 0:
        # print( 'a non-negative', a)

        if b == 0:
            # print( 'b is zero', b)
            return a
        elif b > 0:
            # print('b is non-negative a%b', a % b)
            return gcd(b, a % b)
        else:
            # print('b is negative')
            return 0
    else:
        # print( 'a and b non-negative')
        return 0


# !/bin/python3

import math
import os
import random
import re
import sys


#
# Complete the 'gcd' function below.
#
# The function is expected to return an INTEGER.
# The function accepts following parameters:
#  1. INTEGER a
#  2. INTEGER b
#

def gcd(a, b):
    # Write your code here

    if a > 0:

        if b == 0:
            # As in equation, if b=0, return 1
            return a
        elif b > 0:
            # As in equation, otherwise, call GCD again
            return gcd(b, a % b)
        else:
            # b is not non-negative, return 0
            return 0
    else:
        # a is not non-negative, return 0
        return 0


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    a = int(input().strip())

    b = int(input().strip())

    result = gcd(a, b)

    fptr.write(str(result) + '\n')

    fptr.close()



import json

import sys

# Read input from STDIN
input_json = "".join([line for line in sys.stdin])
json_obj = json.loads(input_json) # Use `json_obj as a regular Python dictionary

# Enter your code here to process input_json, then print output to STDOUT


# Function to convert mass to pounds and round to nearest pound
def kg_to_lbs(kg_input):
    # convert the input in kg to lb and return
    return round(kg_input * 2.205)


# Extract required fields from the input
extracted_data = [
    {
        "id": item["id"],
        "name": item["name"],
        "year": item["year"][:4],
        "mass": kg_to_lbs(float(item["mass"])),
        "latitude": item["geolocation"]["coordinates"][0],
        "longitude": item["geolocation"]["coordinates"][1]
    }
    for item in json_obj
]

# Sort data by id in ascending order
sorted_data = sorted(extracted_data, key=lambda x: x["id"])

# Format the output as a single line separated by spaces
formatted_data = [
    f'{item["id"]} {item["name"]} {item["year"]} {item["mass"]} {item["latitude"]} {item["longitude"]}'
    for item in sorted_data
]

# Print the result
for line in formatted_data:
    print(line)













#!/bin/python3

import math
import os
import random
import re
import sys
import pandas as pd


# Complete the 'weighted_movie_rating' function below.
#
# The function is expected to return a FLOAT.
# The function accepts following parameters:
#  1. STRING movie_title
#  2. FLOAT rt_w
#  3. FLOAT rtu_w
#  4. FLOAT meta_w
#  5. FLOAT metau_w
#  6. FLOAT imdb_w
#
# The function already come with an implementation to download csv file and convert it into a dataframe object using pandas
#
# NEVER WORKED WITH PANDAS? NO PROBLEM! HERE ARE A FEW HELPFUL LINKS/POINTERS:
# https://pandas.pydata.org/pandas-docs/stable/user_guide/10min.html
#
# 1. Get cloumn names
# columns = df.columns
#
# 2. If you want to get values from a single column:
# column_values = df['column_name']
# OR
# column_values = df['column_name'].values.tolist()
#
# 3. Extract rows based on a rule
# df[df['column_name'] == value_of_interest]
#
# NOTE: csv file is loaded into variable called "df"

def weighted_movie_rating(movie_title, rt_w, rtu_w, meta_w, metau_w, imdb_w):
    # Loading the csv as a dataframe
    df = pd.read_csv("https://github.com/mircealex/Movie_ratings_2016_17/raw/master/fandango_score_comparison.csv")

    # Enter your code below. Use the data previously loaded to compute weighted average rating for given input

if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    movie_title = input()

    rt_w = float(input().strip())

    rtu_w = float(input().strip())

    meta_w = float(input().strip())

    metau_w = float(input().strip())

    imdb_w = float(input().strip())

    result = weighted_movie_rating(movie_title, rt_w, rtu_w, meta_w, metau_w, imdb_w)

    fptr.write(str(result) + '\n')

    fptr.close()

# !/bin/python3

import math
import os
import random
import re
import sys
import pandas as pd

'''

# Complete the 'weighted_movie_rating' function below.
#
# The function is expected to return a FLOAT.
# The function accepts following parameters:
#  1. STRING movie_title
#  2. FLOAT rt_w
#  3. FLOAT rtu_w
#  4. FLOAT meta_w
#  5. FLOAT metau_w
#  6. FLOAT imdb_w
#
# The function already come with an implementation to download csv file and convert it into a dataframe object using pandas
#
# NEVER WORKED WITH PANDAS? NO PROBLEM! HERE ARE A FEW HELPFUL LINKS/POINTERS:
# https://pandas.pydata.org/pandas-docs/stable/user_guide/10min.html
#
# 1. Get cloumn names
# columns = df.columns
#
# 2. If you want to get values from a single column:
# column_values = df['column_name']
# OR
# column_values = df['column_name'].values.tolist()
#
# 3. Extract rows based on a rule
# df[df['column_name'] == value_of_interest]
#
# NOTE: csv file is loaded into variable called "df"

'''
def weighted_movie_rating(movie_title, rt_w, rtu_w, meta_w, metau_w, imdb_w):
    print('Weights In', rt_w, rtu_w, meta_w, metau_w, imdb_w)
    if 0.0 <= rt_w <= 1.0 and 0.0 <= rtu_w <= 1.0 and 0.0 <= meta_w <= 1.0 and 0.0 <= metau_w <= 1.0 and 0.0 <= imdb_w <= 1.0:

        # Loading the csv as a dataframe
        df = pd.read_csv("https://github.com/mircealex/Movie_ratings_2016_17/raw/master/fandango_score_comparison.csv")

        # Enter your code below. Use the data previously loaded to compute weighted average rating for given input
        movie_data = df[df['FILM'] == movie_title]

        if movie_data.empty:
            print("Empty data frame")
            return round(0.0, 2)

        rating_columns = ['RottenTomatoes', 'RottenTomatoes_User', 'Metacritic', 'Metacritic_User', 'IMDB']
        rating_columns_normlized = ['RT_norm', 'RT_user_norm', 'Metacritic_norm', 'Metacritic_user_nom', 'IMDB_norm']
        print("Data:", movie_data[rating_columns])
        print("Data N:", movie_data[rating_columns_normlized])

        rating_list = movie_data[rating_columns_normlized].values.tolist()
        # rating_list = movie_data[rating_columns].values.tolist()

        print("Rating list", rating_list[0] != 0.0)
        non_zero_count = sum(1 for x in rating_list[0] if x > 0.0)
        print("Rating non-zero count", non_zero_count)
        # print("Non zero entrie", sum(rating_list[0][] != 0.0))
        weighted_avg = (rating_list[0][0] * rt_w + rating_list[0][1] * rtu_w + rating_list[0][2] * meta_w +
                        rating_list[0][3] * metau_w + rating_list[0][4] * imdb_w) / non_zero_count

        print(weighted_avg)
        return round(weighted_avg, 2)
    else:
        print('Weights not in range', rt_w, rtu_w, meta_w, metau_w, imdb_w)
        return round(0.0, 2)


if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    movie_title = input()

    rt_w = float(input().strip())

    rtu_w = float(input().strip())

    meta_w = float(input().strip())

    metau_w = float(input().strip())

    imdb_w = float(input().strip())

    result = weighted_movie_rating(movie_title, rt_w, rtu_w, meta_w, metau_w, imdb_w)

    fptr.write(str(result) + '\n')

    fptr.close()
'''
