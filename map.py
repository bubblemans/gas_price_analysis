import numpy as np
import matplotlib
matplotlib.use('TkAgg')               
import tkinter as tk                        
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg  
import matplotlib.pyplot as plt 
import tkinter.messagebox as tkmb
import matplotlib.image as mpimg

class Map(tk.Tk):

    def __init__(self):
        super().__init__()
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

win = Map()
win.mainloop()







