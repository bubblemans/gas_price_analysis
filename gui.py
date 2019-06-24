
"""
Name: Weiyuan Chen
Date: 6/23/2019
Final Project
Discription: GUI of the project that has 6 functionalities which are show plots from 2000 to 2018,
show table with date and gas price, show mean,max,min in a bargraph, show a U.S. map of gas prices,
and show next week/month/year gas price pridiction. All functionalities will be visualized in a gui.
"""
import tkinter as tk 
import sys
import os
from fetchData import fetcher 
from plotwin import plotwin
import predictwin
import tablewin
import costwin
import mapwin

def gui2fg():
    """Brings tkinter GUI to foreground on MacCall gui2fg()
    after creating main window and before mainloop() start"""
    if sys.platform == 'darwin':
        tmpl = 'tell application "System Events" to set frontmost of every process whose unix id is %d to true'
        os.system("/usr/bin/osascript -e '%s'" % (tmpl % os.getpid()))

class mainwin(tk.Tk):
    
    db = fetcher() #database module
    
    def __init__(self):
        '''show 6 buttons in the main window and let user to choose one'''
        super().__init__()
        gui2fg()
        self.title('Gas Price APP')
        usagelabel = ('Plot','Table','Analysis','Cost','Map','Prediction')
        usagelist = (lambda:plotwin(self,self.db,0), lambda:tablewin.mainWindow(self,self.db), lambda:plotwin(self,self.db,1),
                          lambda:costwin.mainWindow(self,self.db), lambda:mapwin.Map(self), lambda:predictwin.PredictWin(self,self.db))
        for i,f in enumerate(usagelist):
            tk.Button(self, text=usagelabel[i], command=f, font=30, height = 10, width = 10).grid(row=0, column=i, padx=15)
        
            

if __name__ == '__main__':
    mw  = mainwin()
    mw.mainloop()
