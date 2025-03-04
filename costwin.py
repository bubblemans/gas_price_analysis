#######################################################
#CIS 41B      Final Project
#File Name:   button-cost.py
#Author:      Tianqi Yang
#Time:        6/13/2019
#Description: calculate cost for user
#######################################################
import tkinter.messagebox as tkmb
import tkinter as tk

class mainWindow(tk.Toplevel):
    def __init__(self, master, db):
        '''show the main window'''
        super().__init__()
        self._f = db
        self._areas = dict( (y,x) for x,y in self._f.getAreaWithNum())
        self._gas = dict( (y,x) for x,y in self._f.getGasWithNum())
        self._car = dict( (x,y) for x,y in self._f.getCarMpg())
        #set window
        self.geometry("500x270+600+300")
        self.title("Calculate Cost")
        self.grab_set()
        self.focus_set()
        #frame
        frame = tk.Frame(self)
        tk.Label(frame, text='You live in :').grid(row=0, column=0)
        area = [ i for i in self._areas.keys() ]
        self._live = tk.StringVar()
        self._live.set(area[0])
        tk.OptionMenu(frame, self._live, *area ).grid(row=0, column=1, padx=10)
        frame.pack(pady=10)        
        #frame1
        frame1 = tk.Frame(self)
        tk.Label(frame1, text='Your car model is:').grid(row=0, column=0)
        options = [ i for i in self._car.keys() ]
        self._model = tk.StringVar()
        self._model.set(options[0])
        tk.OptionMenu(frame1, self._model, *options).grid(row=0, column=1, padx=10)
        frame1.pack(pady=10)
        #frame2
        frame2 = tk.Frame(self)
        tk.Label(frame2, text='gas type is:').grid(row=0, column=0)
        gas = [ i for i in self._gas.keys() ]
        self._gasType = tk.StringVar()
        self._gasType.set(gas[0])
        tk.OptionMenu(frame2, self._gasType, *gas).grid(row=0, column=1, padx=10)
        frame2.pack(pady=10)
        #frame3
        frame3 = tk.Frame(self)
        self._miles = tk.StringVar(0)
        self.userEntry = tk.Entry(frame3, textvariable=self._miles, width=4)
        self.userEntry.grid(row=1, column=0)
        tk.Label(frame3, text='miles drove in 2018/').grid(row=1, column=1)
        self._month = tk.StringVar()
        self._month.set(1)
        chooseMonth = tk.OptionMenu(frame3, self._month, *range(1,13)).grid(row=1, column=3)
        frame3.pack(pady=10)
        #ok button
        tk.Button(self, text="OK", fg='blue', command = self.calculate).pack(pady=6)
        #cost label
        self._cost = tk.StringVar()
        tk.Label(self, textvariable=self._cost).pack()
        
    def calculate(self):
        try: 
            miles = float(self._miles.get().strip())
            prices = self._f.getRecordsByAreaGasTime(self._areas[self._live.get()]-1, self._gas[self._gasType.get()]-1, 1)
            cost = miles / self._car[self._model.get()] * prices[int(self._month.get())-13][-1]
            self._cost.set(f"The cost is ${round(cost,2)}.")
        except ValueError as e:
            tkmb.showerror("Error", "The miles must be a number!")
            self.userEntry.delete(0, tk.END)  