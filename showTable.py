#######################################################
#CIS 41B      Final Project
#File Name:   showTable.py
#Author:      Tianqi Yang
#Time:        6/13/2019
#Description: show tata base
#######################################################
import tkinter.filedialog
import tkinter.messagebox as tkmb
import tkinter as tk
import fetchData
import os
class mainWindow(tk.Tk):
    def __init__(self):
        '''show the main window'''
        super().__init__()
        self._f = fetchData.fetcher()
        self._areas = dict( (y,x) for x,y in self._f.getAreaWithNum())
        self._gas = dict( (y,x) for x,y in self._f.getGasWithNum())
        self._time = dict( (y,x) for x,y in self._f.getTimeWithNum())
        #set window
        self.geometry("500x180+600+300")  
        self.title("Calculate Cost")
        self.grab_set()
        self.focus_set()
        #frame1
        frame1 = tk.Frame(self)
        tk.Label(frame1, text='The city data you want to see:').grid(row=0, column=0)
        area = [ i for i in self._areas.keys() ]
        self._live = tk.StringVar()
        self._live.set(area[0])
        tk.OptionMenu(frame1, self._live, *area ).grid(row=0, column=1, padx=10)
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
        tk.Label(frame3, text='the time of data by').grid(row=0, column=0)
        time = [ i for i in self._time.keys() ]
        self._timeType = tk.StringVar()
        self._timeType.set(time[0])
        tk.OptionMenu(frame3, self._timeType, *time).grid(row=0, column=1, padx=10)       
        frame3.pack(pady=10)
        #ok button
        tk.Button(self, text="Show", fg='blue', command = self.showRecoreds).pack(pady=6)
        #cost label
        self._cost = tk.StringVar()
        tk.Label(self, textvariable=self._cost).pack()

    def showRecoreds(self):
        records = self._f.getRecordsByAreaGasTime(self._areas[self._live.get()]-1, self._gas[self._gasType.get()]-1, self._time[self._timeType.get()]-1)
        title = '-'.join([self._live.get(), self._gasType.get()])
        displayWindow(self, records, title )
        
class displayWindow(tk.Toplevel):
    def __init__(self, master, records, title):
        '''initial the park window'''
        super().__init__(master)
        self._records = records
        self._fileName = title
        self.geometry("+800+300")
        self.title(title)
        tk.Label(self, text="Select records to save to file").grid()
        frame = tk.Frame(self)
        scroll= tk.Scrollbar(frame, orient=tk.VERTICAL)
        self.grab_set()
        self.focus_set()
        self._box = tk.Listbox(frame, height=10,width=25, selectmode="multiple", yscrollcommand=scroll.set)
        self._select = []
        for i in self._records:
            year, month, date, price = [ str(k) for k in i]
            if len(month) == 1: month = '0' + month
            if len(date) == 1: date = '0' + date
            if month =="None":
                item = ''.join(['Time: ', year,', price: ',price])
            elif date == "None":
                item = ''.join(['Time: ', year, '/', month, ', price: ', price])
            else:
                item = ''.join(['Time: ', year, '/', month, '/', date, ', price: ', price])
            self._box.insert(tk.END, item)
            self._select.append(item)
        scroll.config(command=self._box.yview)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self._box.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        frame.grid()
        tk.Button(self, text="OK", fg='blue', command=self.writeFile).grid()
        
    def writeFile(self):
        '''save parks to the file'''
        selection = self._box.curselection()
        if len(selection) ==0:
            tkmb.showerror("Error", "At least choice one item!")
        else:
            directory = tk.filedialog.askdirectory(initialdir= 'path')
            if directory != '':
                where = ''.join([directory, '/', self._fileName, '.txt'])
                exists = os.path.isfile(where)
                if exists:
                    tkmb.showinfo('Warning', 'The file will be overwritten!', parent=self)
                with open(where, 'w') as file:
                    for i in selection:
                        file.write(self._select[i])
                        file.write('\n')
                self.destroy()
    
app = mainWindow()
app.mainloop()