#######################################################
#CIS 41B      Final Project
#File Name:   buildDatabase.py
#Author:      Tianqi Yang
#Time:        6/13/2019
#Description: fetch data from database
#######################################################
import sqlite3
REGULAR='Regular'
MIDGRADE='Midgrade'
PREMIUM='Premium'
WEEKLY='Weekly'
MONTHLY='Monthly'
ANNUAL='Annual'
gasTypes=( REGULAR, MIDGRADE, PREMIUM )
timeTypes=( WEEKLY, MONTHLY, ANNUAL)
class fetcher:
    def __init__(self):
        self._conn = sqlite3.connect('data.db')
        self._cur = self._conn.cursor()
        self._cur.execute("PRAGMA table_info(Records)")
        self._areaList = self.getArea()

    def close(self):
        self._conn.commit()
        self._conn.close()
        
    def getArea(self):
        self._cur.execute('SELECT areaName FROM Area')
        return [i[0] for i in self._cur.fetchall()]
    
    def getRecordsByAreaGasTime(self, areaIndex, gasIndex, timeIndex):
        '''
        fetch data by area, gas, and time and return a list of data
        '''
        self._cur.execute('''SELECT Records.dateYear, Records.dateMonth, Records.date, Records.price
                            FROM Records JOIN Area JOIN GasType JOIN TimeType 
                            ON Records.areaId = Area.areaCode AND Area.areaName = "{}"
                            AND Records.gasType = GasType.gasCode AND GasType.gasName = "{}"
                            AND Records.timeType = TimeType.timeCode AND TimeType.timeName = "{}" 
                          '''.format(self._areaList[areaIndex], gasTypes[gasIndex], timeTypes[timeIndex] ))
        return self._cur.fetchall()
    
    def getCarMpg(self):
        '''
        return a list of car name and its mpg 
        '''
        self._cur.execute('SELECT * FROM CarMpg')
        return [ (i[0], i[1]) for i in self._cur.fetchall()]
    
f = fetcher()
#print(f.getRecordsByAreaGasTime(1,1,1))#Monthly, East Coast (PADD 1)
print(f.getCarMpg())
f.close()