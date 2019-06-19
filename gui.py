
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



def gui2fg():
    """Brings tkinter GUI to foreground on MacCall gui2fg()
    after creating main window and before mainloop() start"""
    if sys.platform == 'darwin':
        tmpl = 'tell application "System Events" to set frontmost of every process whose unix id is %d to true'
        os.system("/usr/bin/osascript -e '%s'" % (tmpl % os.getpid()))

class mainwin(tk.Tk):
    
    db = fetcher()
    
    def __init__(self):
        super().__init__()
        gui2fg()
        self.title('Gas Price APP')
        tk.Button(self, text='Plot', command=lambda: self.timeline(0)).grid(row=0, column=0, padx=15)
        tk.Button(self, text='Table', command=lambda: tablewin(self,self.db)).grid(row=0, column=1, padx=15)
        tk.Button(self, text='Analysis', command=lambda: self.timeline(2)).grid(row=0, column=2, padx=15)
        tk.Button(self, text='Cost', command=lambda:costwin(self,self.db)).grid(row=0, column=3, padx=15)
        tk.Button(self, text='Map', command=lambda:mapwin(self)).grid(row=0, column=4, padx=15)
    
    def timeline(self, choice):
        tl = tk.Toplevel()
        tk.Button(tl, text='Weekly', command=lambda: self.check(choice, 0)).grid(row=0, column=0, padx=15)
        tk.Button(tl, text='Montyly', command=lambda: self.check(choice, 1)).grid(row=0, column=1, padx=15)
        tk.Button(tl, text='Yearly', command=lambda: self.check(choice, 2)).grid(row=0, column=2, padx=15)
    
    def check(self, choice, timeline):
        if choice == 0:
            pw = plotwin(self, timeline, self.db, choice)
            pw.wait_window()
        else:
            pw = plotwin(self, timeline, self.db, choice)
            pw.wait_window()            
        

class plotwin(tk.Toplevel):
    
    plotclass = Plotting()
    stat = Analysis()
    
    def __init__(self, master, timeline, db, mainchoice):
        super().__init__(master)
        self.gastype = [tk.IntVar() for i in range(3)]
        self.canvas = None # for plotting
        self.timeline = timeline
        self.db = db
        self.areas = db.getArea()
        self.message = tk.StringVar
        
        f1 = tk.Frame(self) # frame 1 to group listbox and scrollbar
        tk.Label(f1, text='pick Areas and a gas type to plot').grid()
        s = tk.Scrollbar(f1)
        s.grid(row=1, column=1, sticky='NSW')        
        self.lb = tk.Listbox(f1, height=10, width=40, selectmode='multiple', yscrollcommand=s.set)
        self.lb.insert(tk.END, *self.areas)
        self.lb.grid(row=1, column=0)
        s.config(command=self.lb.yview)
        tk.Button(f1, text='OK', command=lambda:self.check(mainchoice)).grid()
        print(mainchoice)
        if mainchoice == 2:
            tk.Label(f1, textvariable=self.message).grid()
        f1.grid()
        
        f2 =  tk.Frame(self) # frame 1 to group Radiobutton
        tk.Label(f2, text='Gas Type').grid()
        self.gaslabel = ('regular', 'midgrade', 'premium')
        for i,tag in enumerate(self.gaslabel):
            tk.Checkbutton(f2, text=tag, variable=self.gastype[i]).grid(row=i+1, column=0)
        f2.grid(row=0, column=1)
        
        f3 = tk.Frame(self) # frame 3 to group plotting canvas
        self.canvasplot(f3)
        f3.grid(row=0, column=2)
    
    def check(self, mainchoice):
        if mainchoice == 0:
            self.plot()
        else:
            self.bargraph()
    
        
    def canvasplot(self, f3):
        #plotting canvas on frame 3
        fig = plt.figure(figsize=(8,6))
        ax = fig.add_subplot(1,1,1)
        self.canvas = FigureCanvasTkAgg(fig, master=f3)
        self.canvas.get_tk_widget().grid()  
            
    def plot(self):
        #callback of ok button, check user selection and get data from db.
        t = self.lb.curselection()
        plots = []
        if len(t) < 1 or all(intval.get()==0 for intval in self.gastype):
            tkmb.showerror("Error", 'Please select at least 1 choice(s)', parent=self)
        else:
            for area in t:
                for gt, intval in enumerate(self.gastype):
                    if intval.get() == 1:
                        #print('Area index:', area, 'gastype:', gt, 'timeline:',timeline)
                        data = self.db.getRecordsByAreaGasTime(area,gt,self.timeline)
                        newdata = self.parsingData(data)
                        plots.append([newdata, self.areas[area]+' & '+self.gaslabel[gt]])
            for i in plots:
                print(i)
            self.plotclass.lineGraph('Gas Price From 2000 to 2018', *plots)
            self.canvas.draw()
            plt.clf()
        
    def bargraph(self):
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
                    data = self.db.getRecordsByAreaGasTime(area,i,self.timeline)
                    newdata = self.parsingData(data)
                    if len(t)>1:
                        graph.append([newdata, self.areas[area]])
                    else:
                        graph.append([newdata, self.gaslabel[i]])
            stats = np.array(self.stat.getStats(*graph))
            self.plotclass.barGraph('Mean,Max,min of Gas prices', np.array(stats))
            self.canvas.draw()
            plt.clf()

                    
    def parsingData(self, data):
        newdata = ['/'.join(date) for date in [[str(one) for one in each] for each in [list(t[0:3-self.timeline]) for t in data]]]
        for i in range(len(data)):
            newdata[i] = (newdata[i], str(data[i][3]))
        return np.array(newdata)
            
class tablewin(tk.Toplevel):
    def __init__(self, master, db):
        '''show the main window'''
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
        records = self._f.getRecordsByAreaGasTime(self._areas[self._live.get()]-1, self._gas[self._gasType.get()]-1, self._time[self._timeType.get()]-1)
        title = '-'.join([self._live.get(), self._gasType.get()])
        tabledisplayWindow(self, records, title )
        
class tabledisplayWindow(tk.Toplevel):
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

        
class costwin(tk.Toplevel):
    def __init__(self, master, db):
        '''show the main window'''
        super().__init__(master)
        self._f = db
        
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
            prices = self._f.getRecordsByAreaGasTime(self._areas[self._live.get()], self._gas[self._gasType.get()]-1, 2)
            cost = miles / self._car[self._model.get()] * prices[-1][-1]
            self._cost.set(f"The cost is ${cost}.")
        except ValueError as e:
            tkmb.showerror("Error", "The miles must be number!")
            self.userEntry.delete(0, tk.END)
            
class mapwin(tk.Toplevel):

    def __init__(self, master):
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



mw  = mainwin()
mw.mainloop()
