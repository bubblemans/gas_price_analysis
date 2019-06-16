
import matplotlib
matplotlib.use('TkAgg')     # tell matplotlib to work with Tkinter
import tkinter as tk        # normal import of tkinter for GUI
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg  # tell matplotlib about Canvas object
import matplotlib.pyplot as plt   # regular plt import
import numpy as np                # regular numpy import
import tkinter.messagebox as tkmb
import sqlite3
from fetchData import fetcher 
import sys
import os


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
        #self.minsize(700,400)
        tk.Button(self, text='Plot', command=lambda: self.timeline(0)).grid(row=0, column=0, padx=15)
        tk.Button(self, text='Table', command=lambda: self.timeline(1)).grid(row=0, column=1, padx=15)
        tk.Button(self, text='Analysis', command=self.analysis).grid(row=0, column=2, padx=15)
    
    def timeline(self, choice):
        tl = tk.Toplevel()
        tk.Button(tl, text='Weekly', command=lambda: self.check(choice, 0)).grid(row=0, column=0, padx=15)
        tk.Button(tl, text='Montyly', command=lambda: self.check(choice, 1)).grid(row=0, column=1, padx=15)
        tk.Button(tl, text='Yearly', command=lambda: self.check(choice, 2)).grid(row=0, column=2, padx=15)
    
    def check(self, choice, timeline):
        if choice == 0:
            pw = plotwin(self, timeline, self.db)
            pw.wait_window()
        else:
            tw = tablewin(self)
        
    
    def analysis(self):
        aw = analysiswin(self)

class plotwin(tk.Toplevel):
    
    def __init__(self, master, timeline, db):
        super().__init__(master)
        self.gastype = tk.IntVar()
        areas = db.getArea()
        self.canvas = None # for plotting
        
        f1 = tk.Frame(self) # frame 1 to group listbox and scrollbar
        tk.Label(f1, text='pick Areas and a gas type to plot').grid()
        s = tk.Scrollbar(f1)
        s.grid(row=1, column=1, sticky='NSW')        
        self.lb = tk.Listbox(f1, height=10, width=40, selectmode='multiple', yscrollcommand=s.set)
        self.lb.insert(tk.END, *areas)
        self.lb.grid(row=1, column=0)
        s.config(command=self.lb.yview)
        tk.Button(f1, text='OK', command=lambda: self.plot(timeline,db)).grid()
        f1.grid()
        
        f2 =  tk.Frame(self) # frame 1 to group Radiobutton
        tk.Label(f2, text='Gas Type').grid()
        gaslabel = ('87', '89', '91')
        for i,tag in enumerate(gaslabel):
            tk.Radiobutton(f2, text=tag, variable=self.gastype, value=i).grid(row=i+1, column=0)
        f2.grid(row=0, column=1)
        
        f3 = tk.Frame(self) # frame 3 to group plotting canvas
        self.canvasplot(f3)
        f3.grid(row=0, column=2)
        
        
    def canvasplot(self, f3):
        #plotting canvas on frame 3
        fig = plt.figure(figsize=(6,4))
        ax = fig.add_subplot(1,1,1)
        self.canvas = FigureCanvasTkAgg(fig, master=f3)
        self.canvas.get_tk_widget().grid()
  
    #demo testing 
    def test1(self, n):
        plt.xlabel('year')
        arr = np.array([1,2,3,4,5])
        for i in range(n):
            plt.plot(arr*i)          
            
    def plot(self, timeline, db):
        #callback of ok button, check user selection and plot on the canvas
        t = self.lb.curselection()
        if len(t) < 1 or self.gastype.get() == None:
            tkmb.showerror("Error", 'Please select at least 1 choice(s)', parent=self)
        for i in t:
            print('Area index:', i)
            self.test1(i)
            self.canvas.draw()
            
class tablewin(tk.Toplevel):
    
    def __init__(self, master):
        super().__init__(master)
        pass
    
class analysiswin(tk.Toplevel):
    
    def __init__(self, master):
        super().__init__(master)
        pass

mw  = mainwin()
mw.mainloop()
