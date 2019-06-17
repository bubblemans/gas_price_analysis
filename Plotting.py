import numpy as np
import matplotlib
matplotlib.use('TkAgg')               
import tkinter as tk                      	
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg  
import matplotlib.pyplot as plt	
import tkinter.messagebox as tkmb
import csv


# parse a csv file
# param: filename
# ret: a 2D list of date and gas price. ex: [["11/24/1995", "1.694"]]
def parse(filename):
	records = []

	with open(filename, "r") as csvFile:
		csvreader = csv.reader(csvFile)
		for row in csvreader:
			records.append(row)
		records.reverse()
		return records[:-5]


class Plotting():
	def __init__(self):
		pass

	def lineGraph(self, title, *args):
		# args = [(np.array([date, gas_price]), label)]
		for y in args:
			plt.plot(y[0][:,0], y[0][:,1].astype(np.float), markeredgewidth=0.01,label=y[1])
		plt.title(title)
		plt.xlabel("Date")
		plt.ylabel("gas price")
		plt.xticks(rotation=90, fontsize=5)
		maxV = args[0][0].shape[0]
		plt.xticks(np.arange(0,maxV,20))
		plt.legend(loc="best")
		plt.show()

	def barGraph(self,title,stat_list):
		# stat_list = np.array([mean,max,min,location or gas_type])
		for i in range(3):
			if i == 0:
				plt.bar(stat_list[:,3],stat_list[:,i].astype(np.float),color="g",alpha=0.8,label="mean")
			if i == 1:
				plt.bar(stat_list[:,3],stat_list[:,i].astype(np.float),color="y",alpha=0.5,label="max")
			if i == 2:
				plt.bar(stat_list[:,3],stat_list[:,i].astype(np.float),color="b",alpha=0.5,label="min")

		plt.title(title)
		plt.legend(loc="best")
		plt.show()

class Analysis():
	def __init__(self):
		pass

	def getStats(self,*args):
		stats = []
		for arg in args:
			n = arg[0][:,1].astype(np.float)
			stats.append([np.mean(n), n.max(), n.min(), arg[1]])
		return stats

	def calculateCost(self, mpg, gas_price, distance):
		return distance/mpg*gas_price

if __name__ == '__main__':
	reg_list = parse("Regular.csv")
	mid_list = parse("Midgrade.csv")
	pre_list = parse("Premium.csv")

	plotting = Plotting()
	# plotting.lineGraph("Weekly gas price", (np.array(reg_list),"regular")
	# 	,(np.array(mid_list),"midgrade"),(np.array(pre_list),"premium"))

	analyze = Analysis()
	stats = analyze.getStats((np.array(reg_list),"regular"), 
		(np.array(mid_list),"midgrade"),(np.array(pre_list),"premium"))
	plotting.barGraph("mean vs max vs min", np.array(stats))










