
"""
Name: Weiyuan Chen, Tianqi, Alvin
Date: 6/23/2019
Final Project
Discription: GUI of the project that has 6 functionalities which are show plots from 2000 to 2018,
show table with date and gas price, show mean,max,min in a bargraph, show a U.S. map of gas prices,
and show next week/month/year gas price pridiction. All functionalities will be visualized in a gui.
"""
import matplotlib
matplotlib.use('TkAgg')     # tell matplotlib to work with Tkinter
import tkinter as tk        # normal import of tkinter for GUI
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg  # tell matplotlib about Canvas object
import matplotlib.pyplot as plt   # regular plt import
import numpy as np                # regular numpy import
import tkinter.messagebox as tkmb
import sqlite3
from fetchData import fetcher 
from Plotting import Plotting, Analysis
import sys
import os
import tkinter.filedialog
import matplotlib.image as mpimg
import socket
import pickle

HOST = "localhost"      # on the same machine   
PORT = 5551             # as long as this is unassigned

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
        usagelist = (lambda:plotwin(self,self.db,0), lambda:tablewin(self,self.db), lambda:plotwin(self,self.db,1),
                          lambda:costwin(self,self.db), lambda:mapwin(self), lambda:predictwin(self,self.db))
        for i,f in enumerate(usagelist):
            tk.Button(self, text=usagelabel[i], command=f, font=30, height = 10, width = 10).grid(row=0, column=i, padx=15)
        

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
            
class tablewin(tk.Toplevel):
    def __init__(self, master, db):
        '''table button window to show different buttons for user choose'''
        super().__init__(master)
        self._f = db
        self._areas = dict( (y,x) for x,y in self._f.getAreaWithNum())
        self._gas = dict( (y,x) for x,y in self._f.getGasWithNum())
        self._time = dict( (y,x) for x,y in self._f.getTimeWithNum())
        #set window
        self.geometry("500x180+600+300")  
        self.title("Show data table")
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
        '''get the data and construct a displaywindow'''
        records = self._f.getRecordsByAreaGasTime(self._areas[self._live.get()]-1, self._gas[self._gasType.get()]-1, self._time[self._timeType.get()]-1)
        title = '-'.join([self._live.get(), self._gasType.get()])
        displaytableWindow(self, records, title )
        
class displaytableWindow(tk.Toplevel):
    def __init__(self, master, records, title):
        '''show to table data in a window'''
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
        '''save selected record to the file'''
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

        
class costwin(tk.Toplevel):
    def __init__(self, master, db):
        '''cost button window to show the cost by user choice and input'''
        super().__init__(master)
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
        '''calculate the cost'''
        try: 
            miles = float(self._miles.get().strip())
            prices = self._f.getRecordsByAreaGasTime(self._areas[self._live.get()]-1, self._gas[self._gasType.get()]-1, 1)
            cost = miles / self._car[self._model.get()] * prices[int(self._month.get())-13][-1]
            self._cost.set(f"The cost is ${round(cost,2)}.")
        except ValueError as e:
            tkmb.showerror("Error", "The miles must be a number!")
            self.userEntry.delete(0, tk.END) 
            
class mapwin(tk.Toplevel):

    def __init__(self, master):
        '''a window to show the gas prices in U.S. map'''
        super().__init__(master)
        self.title("Map")

        # radiobutton
        choiceFrame = tk.Frame(self)
        choiceFrame.grid(row=0, column=0, sticky="w")
        self.controlVar = tk.IntVar()
        RB1 = tk.Radiobutton(choiceFrame, text="Regular", variable=self.controlVar, value=1)
        RB2 = tk.Radiobutton(choiceFrame, text="Midgrade", variable=self.controlVar, value=2)
        RB3 = tk.Radiobutton(choiceFrame, text="Premium", variable=self.controlVar, value=3)
        self.controlVar.set(1)

        RB1.grid(row=0, column=0, sticky="w")
        RB2.grid(row=1, column=0, sticky="w")
        RB3.grid(row=2, column=0, sticky="w")

        # OK button
        OK = tk.Button(choiceFrame, text="OK", command=self.handleOK)
        OK.grid(row=3, column=0)

        # map figure
        fig = plt.figure(figsize=(9,6))
        img=mpimg.imread("regular.png")
        imgplot = plt.imshow(img)
        canvas = FigureCanvasTkAgg(fig, master=self)    
        canvas.get_tk_widget().grid(row=0, column=1, sticky="e")    
        canvas.draw()  

    def handleOK(self):
        '''Ok button for different gas type'''
        if self.controlVar.get() == 1:
            fig = plt.figure(figsize=(9,6))
            img=mpimg.imread("regular.png")
            imgplot = plt.imshow(img)
            canvas = FigureCanvasTkAgg(fig, master=self)    
            canvas.get_tk_widget().grid(row=0, column=1, sticky="e")    
            canvas.draw()  
            self.update()
        elif self.controlVar.get() == 2:
            fig = plt.figure(figsize=(9,6))
            img=mpimg.imread("midgrade.png")
            imgplot = plt.imshow(img)
            canvas = FigureCanvasTkAgg(fig, master=self)    
            canvas.get_tk_widget().grid(row=0, column=1, sticky="e")    
            canvas.draw()  
            self.update()
        elif self.controlVar.get() == 3:
            fig = plt.figure(figsize=(9,6))
            img=mpimg.imread("premium.png")
            imgplot = plt.imshow(img)
            canvas = FigureCanvasTkAgg(fig, master=self)    
            canvas.get_tk_widget().grid(row=0, column=1, sticky="e")    
            canvas.draw()  
            self.update()

class predictwin(tk.Toplevel):
    def __init__(self, master, db):
        '''prediction button window to let user make a choice'''
        super().__init__(master)
        self._f = db
        self._areas = dict( (y,x) for x,y in self._f.getAreaWithNum())
        self._gas = dict( (y,x) for x,y in self._f.getGasWithNum())

    # set window
        self.geometry("500x250+600+300")
        self.title("Predict")
        self.grab_set()
        self.focus_set()

        # period type
        pframe = tk.Frame(self)
        tk.Label(pframe, text='Time period').grid(row=0, column=0, sticky="w")
        period = ["Weekly", "Monthly", "Yearly"]
        self._time = tk.StringVar()
        self._time.set(period[0])
        tk.OptionMenu(pframe, self._time, *period ).grid(row=0, column=1, padx=10)
        pframe.pack(pady=10)

        # area
        frame = tk.Frame(self)
        tk.Label(frame, text='You live in :').grid(row=0, column=0, sticky="w")
        area = [ i for i in self._areas.keys() ]
        self._live = tk.StringVar()
        self._live.set(area[0])
        tk.OptionMenu(frame, self._live, *area ).grid(row=0, column=1, padx=10)
        frame.pack(pady=10)

        # gas type
        frame2 = tk.Frame(self)
        tk.Label(frame2, text='gas type is:').grid(row=0, column=0, sticky="w")
        gas = [ i for i in self._gas.keys() ]
        self._gasType = tk.StringVar()
        self._gasType.set(gas[0])
        tk.OptionMenu(frame2, self._gasType, *gas).grid(row=0, column=1, padx=10)
        frame2.pack(pady=10)

        # Predict button
        button = tk.Button(self, text="Predict", command=self.handlePredict)
        button.pack(pady=10)

        # result label
        self.result = tk.Label(self)
        self.result.pack(pady=10)

    def handlePredict(self):
        '''connet to a server to make the prediction'''
        with socket.socket() as s:
            s.connect((HOST, PORT))
            mesg = str(self._areas[self._live.get()]-1) + "," + str(self._gas[self._gasType.get()]-1) + "," + self._time.get()
            s.send(mesg.encode('utf-8'))
            fromServer = pickle.loads(s.recv(1024))
            self.updateLabel("The next "+self._time.get()[0:-2]+" gas price "+"is "+str(fromServer))
            s.close()

    def updateLabel(self, fromServer):
        '''update a text label'''
        self.result.config(text=fromServer)
        self.update()

if __name__ == '__main__':
    mw  = mainwin()
    mw.mainloop()
