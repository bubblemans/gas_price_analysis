#######################################################
#CIS 41B      Final Project
#File Name:   buildDatabase.py
#Author:      Tianqi Yang
#Time:        6/13/2019
#Description: fetch gas price from website and save in
# the database
#######################################################
import requests
from  bs4  import BeautifulSoup
import sqlite3
import time

REGULAR='Regular'
MIDGRADE='Midgrade'
PREMIUM='Premium'
WEEKLY = 'Weekly'
MONTHLY = 'Monthly'
ANNUAL = 'Annual'
MAINLINK = "https://www.eia.gov/dnav/pet/pet_pri_gnd_dcus_nus_w.htm"
BASELINK = 'https://www.eia.gov/dnav/pet'

links = { }
gasTypes = ( REGULAR, MIDGRADE, PREMIUM )
timeTypes = ( WEEKLY, MONTHLY, ANNUAL)

conn = sqlite3.connect('data.db')
cur = conn.cursor()

page = requests.get(MAINLINK)
soup = BeautifulSoup(page.content, "lxml")

startTime = time.time()
#table 1
cur.execute("DROP TABLE IF EXISTS Area")
cur.execute('''CREATE TABLE Area(
            areaCode INTEGER PRIMARY KEY UNIQUE,
            areaName TEXT)''')
#save data to table 1
for index, elem in enumerate(soup.find_all('option'), 1):
    if elem.get_text().strip() not in timeTypes: 
        links[elem.get_text().strip()] = f"https://www.eia.gov/dnav/pet/{elem['value']}"
        cur.execute('''INSERT INTO Area VALUES (?, ?)''', ( index , elem.get_text().strip() ))
        
#table 2
cur.execute("DROP TABLE IF EXISTS GasType")
cur.execute('''CREATE TABLE GasType(
            gasCode INTEGER PRIMARY KEY UNIQUE,
            gasName TEXT)''')
#save data to table 2
for index, elem in enumerate(gasTypes, 1):
    cur.execute('''INSERT INTO GasType VALUES (?, ?)''', ( index , elem ))

#table 3
cur.execute("DROP TABLE IF EXISTS TimeType")
cur.execute('''CREATE TABLE TimeType(
            timeCode INTEGER PRIMARY KEY UNIQUE,
            timeName TEXT)''')
#save data to table 3
for index, elem in enumerate(timeTypes, 1):
    cur.execute('''INSERT INTO TimeType VALUES (?, ?)''', ( index , elem )) 
    
#table 4
cur.execute("DROP TABLE IF EXISTS Records")
cur.execute('''CREATE TABLE Records(
           dateYear INTEGER,
           dateMonth INTEGER,
           date INTEGER,
           price REAL,
           areaId INTEGER,
           gasType INTEGER,
           timeType INTEGER,
           FOREIGN KEY (areaId) REFERENCES Area(areaCode),
           FOREIGN KEY(gasType) REFERENCES GasType(gasCode),
           FOREIGN KEY(timeType) REFERENCES TimeType(timeCode)  
           )''')
#save data to table 4
areaIndex = 1
month, date, price = '', '', ''
for area_links in links.values():
    sub_page = requests.get(area_links)
    sub_soup = BeautifulSoup(sub_page.content, "lxml")
    sub_links =  soup.find_all('a', class_='Hist')
    needed_links = [sub_links[3]['href'], sub_links[6]['href'], sub_links[9]['href'] ]
    gasIndex = 1
    for sub_sub_link in needed_links:
        sub_temp = f"{BASELINK}{sub_sub_link[1:]}"
        sub_sub_page = requests.get(sub_temp)
        sub_sub_soup = BeautifulSoup(sub_sub_page.content, "lxml") 
        timeType = 1    
        for a in sub_sub_soup.body.find_all('a', class_='NavChunk'):
            differentTime = f"{BASELINK}/hist/{a['href']}"
            differentTime_page = requests.get(differentTime)
            differentTime_soup = BeautifulSoup(differentTime_page.content, "lxml")            
            if timeType == 1:
                for i in differentTime_soup.body.find_all('tr'):
                    k = i.find_all('td', class_='B6')
                    if len(k) != 0 or i.get_text() == '': 
                        year = int(k[0].get_text().strip()[:4])
                        if 2000 <= year <= 2018:
                            j = i.find_all('td')
                            for m in range(1, len(j), 2):
                                month, date, price= j[m].get_text()[:2], j[m].get_text()[3:], j[m+1].get_text()
                                if month != '' and date != '' and price != '':
                                    print( year, int(month), int(date), float(price), areaIndex, gasIndex, timeType)
                                    cur.execute('INSERT INTO Records VALUES ( ? ,?, ?, ?, ?, ?, ?)',
                                                ( year, int(month), int(date), float(price), areaIndex, gasIndex, timeType))
            elif timeType == 2:
                for i in differentTime_soup.body.find_all('tr'):
                    k = i.find_all('td', class_='B4')
                    if isinstance(k, list) and len(k) > 0 :
                        if 2000 <= int(k[0].get_text().strip()) <= 2018:
                            j = i.find_all('td')
                            year = j[0].get_text().strip()
                            for m in range(1, len(j)):
                                print( int(year), m, float(j[m].get_text()), areaIndex, gasIndex, timeType)
                                cur.execute('''INSERT INTO Records 
                                                (dateYear, dateMonth, price, areaId, gasType, timeType) VALUES ( ?, ?, ?, ?, ?, ?)''',
                                                ( int(year), m, float(j[m].get_text()), areaIndex, gasIndex, timeType))
            else:
                for i in differentTime_soup.body.find_all('tr'):
                    k = i.find_all('td', class_='B4')
                    if isinstance(k, list) and len(k) > 0 :
                        target_year = int(k[0].get_text().strip()[:4])
                        if 2000 <= target_year <= 2018:
                            j = i.find_all('td')
                            for m in range(1, len(j)):
                                if j[m].get_text() != '':
                                    print( target_year, float(j[m].get_text() ), areaIndex, gasIndex, timeType)
                                    cur.execute('''INSERT INTO Records 
                                                    ( dateYear, price, areaId, gasType, timeType) VALUES (?, ?, ?, ?, ?)''',
                                                    ( target_year, float(j[m].get_text() ), areaIndex, gasIndex, timeType))
                                    target_year+=1                                
            timeType += 1
        gasIndex += 1
    areaIndex += 1
print(f'Time:{round(time.time()-startTime,2)}s')
conn.commit()

