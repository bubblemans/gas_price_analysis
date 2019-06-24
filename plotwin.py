"""
Name: Weiyuan Chen
Date: 6/23/2019
Final Project
Discription: plot window for both Plot button and Analysis button to either plot dot plot or bargraph
"""
import matplotlib
matplotlib.use('TkAgg')     # tell matplotlib to work with Tkinter
import tkinter as tk        # normal import of tkinter for GUI
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg  # tell matplotlib about Canvas object
import matplotlib.pyplot as plt   # regular plt import
import numpy as np                # regular numpy import
import tkinter.messagebox as tkmb
from Plotting import Plotting, Analysis

class plotwin(tk.Toplevel):
    
    plotclass = Plotting() # plot and bar graph function module
    stat = Analysis() # calcualte mean,max,min module
    
    def __init__(self, master, db, mainchoice):
        '''Three frames of this plotting window
           Argument: master window, database, mainchoice for plot or bargraph
        '''
        super().__init__(master)
        self.gastype = [tk.IntVar() for i in range(3)]
        self.canvas = None # for plotting
        self.timeline = tk.IntVar()
        self.db = db
        self.areas = db.getArea()
        
        f1 = tk.Frame(self) # frame 1 to group listbox and scrollbar
        tk.Label(f1, text='Pick Areas, gas types and a timeline').grid()
        s = tk.Scrollbar(f1)
        s.grid(row=1, column=1, sticky='NSW')        
        self.lb = tk.Listbox(f1, height=10, width=40, selectmode='multiple', yscrollcommand=s.set)
        self.lb.insert(tk.END, *self.areas)
        self.lb.grid(row=1, column=0)
        s.config(command=self.lb.yview)
        tk.Button(f1, text='OK', command=lambda:self.check(mainchoice)).grid()
        if mainchoice == 1:
            self.statsave = []
            tk.Button(f1, text='Show Statistic in Text', command=lambda:self.showstat()).grid()
        f1.grid()
        
        f2 =  tk.Frame(self) # frame 1 to group Radiobutton
        tk.Label(f2, text='Gas Type').grid()
        tk.Label(f2, text='Timeline').grid(row=0, column=1, padx=15)
        self.gaslabel = ('regular', 'midgrade', 'premium')
        timelinelabel = ('Weekly', 'Monthly', 'Yearly')
        for i,tag in enumerate(self.gaslabel):
            tk.Checkbutton(f2, text=tag, variable=self.gastype[i]).grid(row=i+1, column=0)
        for i,tag in enumerate(timelinelabel):
            tk.Radiobutton(f2, text=tag, variable=self.timeline, value=i).grid(row=i+1, column=1)
        f2.grid(row=0, column=1)
        
        f3 = tk.Frame(self) # frame 3 to group plotting canvas
        self.canvasplot(f3)
        f3.grid(row=0, column=2)
        self.grab_set()
        self.focus_set()
    
    def check(self, mainchoice):
        '''check the mainchoice is 0 or 1 for plot or bargraph'''
        if mainchoice == 0:
            self.plot()
        else:
            self.bargraph()
    
        
    def canvasplot(self, f3):
        '''build a canvas for plot and bargraph'''
        #plotting canvas on frame 3
        fig = plt.figure(figsize=(8,6.5))
        ax = fig.add_subplot(1,1,1)
        self.canvas = FigureCanvasTkAgg(fig, master=f3)
        self.canvas.get_tk_widget().grid()  
            
    def plot(self):
        '''callback of ok button, check user selection and get data from db and call dot plot function to plot'''
        t = self.lb.curselection()
        plots = []
        if len(t) < 1 or all(intval.get()==0 for intval in self.gastype):
            tkmb.showerror("Error", 'Please select at least 1 choice(s)', parent=self)
        else:
            for area in t:
                for gt, intval in enumerate(self.gastype):
                    if intval.get() == 1:
                        #print('Area index:', area, 'gastype:', gt, 'timeline:',timeline)
                        data = self.db.getRecordsByAreaGasTime(area,gt,self.timeline.get())
                        newdata = self.parsingData(data)
                        plots.append([newdata, self.areas[area]+' & '+self.gaslabel[gt]])
            self.plotclass.lineGraph('Gas Price From 2000 to 2018', *plots)
            self.canvas.draw()
            plt.clf()
        
    def bargraph(self):
        '''callback of ok button, check user selection, get data from db calculate stats, and call bargraph function to plot'''
        t = self.lb.curselection()
        graph = []
        gastypechoice = [intval.get() for intval in self.gastype if intval.get() == 1]
        if len(t) < 1 or len(gastypechoice) == 0:
            tkmb.showerror("Error", 'Please select at least 1 choice(s)', parent=self)
        elif len(t) > 1 and len(gastypechoice) >1:
            tkmb.showerror("Error", 'Please only select one Area or one Gastype', parent=self)  
        else:
            for area in t:
                for i in range(len(gastypechoice)):
                    data = self.db.getRecordsByAreaGasTime(area,i,self.timeline.get())
                    newdata = self.parsingData(data)
                    if len(t)>1:
                        graph.append([newdata, self.areas[area]])
                    else:
                        graph.append([newdata, self.gaslabel[i]])
            self.statsave = np.array(self.stat.getStats(*graph))
            self.plotclass.barGraph('Mean,Max,min of Gas prices', np.array(self.statsave))
            self.canvas.draw()
            plt.clf()
            
    def showstat(self):
        '''toplevel win for showing mean,max,min'''
        if len(self.statsave) != 0:
            swin = tk.Toplevel(self)
            for s in self.statsave:
                message = f'{s[3]}: Mean/Max/Min = {round(float(s[0]),3)}/{s[1]}/{s[2]}'
                tk.Label(swin, text=message).grid()

                    
    def parsingData(self, data):
        '''change data in a format to use'''
        newdata = ['/'.join(date) for date in [[str(one) for one in each] for each in [list(t[0:3-self.timeline.get()]) for t in data]]]
        for i in range(len(data)):
            newdata[i] = (newdata[i], str(data[i][3]))
        return np.array(newdata)