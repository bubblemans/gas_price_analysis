#######################################################
#CIS 41B      Final Project
#File Name:   costButton.py
#Author:      Tianqi Yang
#Time:        6/13/2019
#Description: calculate cast for user
#######################################################
import tkinter.filedialog
import tkinter.messagebox as tkmb
import tkinter as tk
import requests
import json
import threading
import queue
import fetchData
class mainWindow(tk.Tk):
    def __init__(self):
        '''show the main window'''
        super().__init__()
        self._f = fetchData.fetcher()
        self._areas = dict( (y,x) for x,y in self._f.getAreaWithNum())
        self._gas = dict( (y,x) for x,y in self._f.getGasWithNum())
        self._car = dict( (x,y) for x,y in self._f.getCarMpg())
        #set window
        self.geometry("500x200+600+300")  
        self.title("Calculate Cost")
        self.grab_set()
        self.focus_set()
        #frame
        frame = tk.Frame(self)
        tk.Label(frame, text='You live in :').grid(row=0, column=0)
        area = [ i for i in self._areas.keys() ]
        self._live = tk.StringVar()
        self._live.set(area[0])
        set1 = tk.OptionMenu(frame, self._live, *area )
        set1.grid(row=0, column=1, padx=10)
        frame.pack()        
        #frame1
        frame1 = tk.Frame(self)
        tk.Label(frame1, text='Your car model is:').grid(row=0, column=0)
        options = [ i for i in self._car.keys() ]
        self._model = tk.StringVar()
        self._model.set(options[0])
        set2 = tk.OptionMenu(frame1, self._model, *options)
        set2.grid(row=0, column=1, padx=10)
        frame1.pack()  
        #frame2
        frame2 = tk.Frame(self)
        tk.Label(frame2, text='gas type is:').grid(row=0, column=0)
        gas = [ i for i in self._gas.keys() ]
        self._gasType = tk.StringVar()
        self._gasType.set(gas[0])
        set3 = tk.OptionMenu(frame2, self._gasType, *gas)
        set3.grid(row=0, column=1, padx=10)
        frame2.pack()          
        #frame3
        frame3 = tk.Frame(self)
        self._miles = tk.StringVar(0)
        self.userEntry = tk.Entry(frame3, textvariable=self._miles)
        self.userEntry.grid(row=1, column=0)
        tk.Label(frame3, text='miles drove in 2018/').grid(row=1, column=1)
        self._month = tk.StringVar()
        self._month.set(1)
        chooseMonth = tk.OptionMenu(frame3, self._month, *range(1,13)).grid(row=1, column=3)
        frame3.pack()
        #ok button
        tk.Button(self, text="OK", fg='blue', command = self.calculate).pack()
        #cost label
        self._cost = tk.StringVar()
        tk.Label(self, textvariable=self._cost).pack()
        
    def calculate(self):
        try: 
            miles = float(self._miles.get().strip())
            prices = self._f.getRecordsByAreaGasTime(self._areas[self._live.get()], self._gas[self._gasType.get()], 2)
            cost = miles / self._car[self._model.get()] * prices[-1][-1]
            self._cost.set(f"The cost is ${cost}.")
        except ValueError as e:
            tkmb.showerror("Error", "The miles must be number!")
            self.userEntry.delete(0, tk.END)  
            
app = mainWindow()
app.mainloop()