#######################################################
#CIS 41B      Final Project
#File Name:   builCarMpg.py
#Author:      Tianqi Yang
#Time:        6/17/2019
#Description: fetch cars' mpg for different types car
#######################################################
import requests
from  bs4  import BeautifulSoup
import sqlite3
import time
LINK = "https://www.cars.com/articles/best-and-worst-gas-mileage-2018-1420698621218/"
page = requests.get(LINK)
soup = BeautifulSoup(page.content, "lxml")
carsMpg = [ i.get_text() for elem in soup.find_all( 'tr', class_=['row1','row2'])  for i in elem.find_all('td') ]
conn = sqlite3.connect('data.db')
cur = conn.cursor()
cur.execute("DROP TABLE IF EXISTS CarMpg")
cur.execute('''CREATE TABLE CarMpg(
            carName TEXT,
            mpg INTEGER)''')
for k in range(1, len(carsMpg), 3):
    cur.execute('''INSERT INTO CarMpg VALUES (?, ?)''', (carsMpg[k], int(carsMpg[k+1])))
conn.commit()
print('done')