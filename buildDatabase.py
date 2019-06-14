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

#table 1
cur.execute("DROP TABLE IF EXISTS area")
cur.execute('''CREATE TABLE area(
            areaCode INTEGER PRIMARY KEY UNIQUE,
            areaName TEXT)''')
#save data to table 1
for index, elem in enumerate(soup.find_all('option'), 1):
    if elem.get_text().strip() not in timeTypes: 
        links[elem.get_text().strip()] = f"https://www.eia.gov/dnav/pet/{elem['value']}"
        cur.execute('''INSERT INTO area VALUES (?, ?)''', ( index , elem.get_text().strip() ))
#table 2
cur.execute("DROP TABLE IF EXISTS gasTypeTable")
cur.execute('''CREATE TABLE gasTypeTable(
            gasCode INTEGER PRIMARY KEY UNIQUE,
            gasName TEXT)''')
#save data to table 2
for index, elem in enumerate(gasTypes, 1):
    cur.execute('''INSERT INTO gasTypeTable VALUES (?, ?)''', ( index , elem ))

#table 3
cur.execute("DROP TABLE IF EXISTS timeTypeTable")
cur.execute('''CREATE TABLE timeTypeTable(
            timeCode INTEGER PRIMARY KEY UNIQUE,
            timeName TEXT)''')
#save data to table 3
for index, elem in enumerate(timeTypes, 1):
    cur.execute('''INSERT INTO timeTypeTable VALUES (?, ?)''', ( index , elem )) 
    
#table 4
cur.execute("DROP TABLE IF EXISTS record")
cur.execute('''CREATE TABLE record(
           id INTEGER NOT NULL PRIMARY KEY UNIQUE,
           dateYear INTEGER,
           dateMonth INTEGER,
           date INTEGER,
           price REAL,
           areaId INTEGER,
           gasType INTEGER,
           timeType INTEGER,
           FOREIGN KEY (areaId) REFERENCES area(areaCode),
           FOREIGN KEY(gasType) REFERENCES gasTypeTable(gasCode),
           FOREIGN KEY(timeType) REFERENCES timeTypeTable(timeCode)  
           )''')
startTime = time.time()
#save data to table 4
index = 1
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
                                    #index, year, month, date, price, areaId, gasType, timeType                          
                                    print( index, year, int(month), int(date), float(price), areaIndex, gasIndex, timeType)
                                    cur.execute('INSERT INTO record VALUES (?, ? ,?, ?, ?, ?, ?, ?)', ( index, year, int(month), int(date), float(price), areaIndex, gasIndex, timeType))
                                    index += 1
            elif timeType == 2:
                for i in differentTime_soup.body.find_all('tr'):
                    k = i.find_all('td', class_='B4')
                    if isinstance(k, list) and len(k) > 0 :
                        if 2000 <= int(k[0].get_text().strip()) <= 2018:
                            j = i.find_all('td')
                            year = j[0].get_text().strip()
                            for m in range(1, len(j)):
                                price = j[m].get_text()
                                print( index, int(year), m, float(j[m].get_text()), areaIndex, gasIndex, timeType)
                                cur.execute('''INSERT INTO record 
                                                (id, dateYear, dateMonth, price, areaId, gasType, timeType)
                                                VALUES
                                                (?, ?, ?, ?, ?, ?, ?)''',
                                                ( index, int(year), m, float(j[m].get_text()), areaIndex, gasIndex, timeType)
                                            )
                                index += 1          
            else:
                for i in differentTime_soup.body.find_all('tr'):
                    k = i.find_all('td', class_='B4')
                    if isinstance(k, list) and len(k) > 0 :
                        target_year = int(k[0].get_text().strip()[:4])
                        if 2000 <= target_year <= 2018:
                            j = i.find_all('td')
                            for m in range(1, len(j)):
                                if j[m].get_text() != '':
                                    print( index, target_year, float(j[m].get_text() ), areaIndex, gasIndex, timeType)
                                    cur.execute('''INSERT INTO record 
                                                    (id, dateYear, price, areaId, gasType, timeType)
                                                    VALUES
                                                    (?, ?, ?, ?, ?, ?)''',
                                                    ( index, target_year, float(j[m].get_text() ), areaIndex, gasIndex, timeType)
                                                )
                                    target_year+=1                                
                                    index += 1                                
            timeType += 1
        gasIndex += 1
    areaIndex += 1
print(f'Time:{round(time.time()-startTime,2)}s')
conn.commit()