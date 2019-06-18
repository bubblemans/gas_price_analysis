import numpy as np
import matplotlib
matplotlib.use('TkAgg')               
import tkinter as tk                      	
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg  
import matplotlib.pyplot as plt	
import tkinter.messagebox as tkmb
import csv
import requests
from bs4 import BeautifulSoup


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

	# draw one or more line graphs
	# param: a title string, a np.array of 2D np.array(date and gas price) and a label string(see example below)
	# ret: none
	def lineGraph(self, title, *args):
		# args = [(np.array([date, gas_price]), label)]
		# ex: np.array([[["11/24/1995", "2.534"],
		# 				["12/01/1995", "2.236"]], "regular"])
		for y in args:
			plt.plot(y[0][:,0], y[0][:,1].astype(np.float), markeredgewidth=0.01,label=y[1])
		plt.title(title)
		plt.xlabel("Date")
		plt.ylabel("gas price")
		plt.xticks(rotation=90, fontsize=5)
		maxV = args[0][0].shape[0]
		plt.xticks(np.arange(0,maxV,20))
		plt.legend(loc="best")
		# plt.show()

	# draw one or more overlapping bar graph that contains mean, max, and min values
	# param: a title string, a 2D np.array of mean, max, min, and location(see example below)
	# ret: none
	def barGraph(self,title,stat_list):
		# stat_list = np.array([mean,max,min,location or gas_type])
		# ex: np.array([["2.235", "3.235", "1.124", "CA"],
		# 			    ["2.645", "3.532", "1.346", "NY"]])
		for i in range(3):
			if i == 0:
				plt.bar(stat_list[:,3],stat_list[:,i].astype(np.float),color="g",alpha=0.8,label="mean")
			if i == 1:
				plt.bar(stat_list[:,3],stat_list[:,i].astype(np.float),color="y",alpha=0.5,label="max")
			if i == 2:
				plt.bar(stat_list[:,3],stat_list[:,i].astype(np.float),color="b",alpha=0.5,label="min")

		plt.title(title)
		plt.legend(loc="best")
		plt.xticks(rotation=45)
		# plt.show()

class Analysis():
	def __init__(self):
		pass

	# get stats of mean, max, min
	# param: one or more tuples of a 2D np.array(date and gas_price) and a label
	#	    ex: (np.array([["11/24/1995", "2.534"],
	# 				       ["12/01/1995", "2.236"]]), "premium")
	# ret: a list of mean, max, min, and label ex: [["2.235", "3.235", "1.124", "CA"],
	# 											    ["2.645", "3.532", "1.346", "NY"]]
	def getStats(self,*args):
		stats = []
		for arg in args:
			n = arg[0][:,1].astype(np.float)
			stats.append([np.mean(n), n.max(), n.min(), arg[1]])
		return stats
	# calculate the cost of gas based on the given mpg, gas_price, and distance
	# param: mpg(float), gas_price(float), distance(float)
	# return: the cost of gas(float)
	def calculateCost(self, mpg, gas_price, distance):
		return float(distance/mpg*gas_price)

class WebScrape():
	# fetch gas price in different states in the US
	# , and this method is specifically for map graph in Tableau
	def __init__(self):
		# headers = {'Accept-Language': 'en-US;q=0.7,en;q=0.3',}
		# page = requests.get("https://gasprices.aaa.com/state-gas-price-averages/",headers=headers)
		session = requests.Session()
		page = session.get('https://gasprices.aaa.com/state-gas-price-averages/', headers={'User-Agent': 'Mozilla/5.0'})
		print(page.status_code)
		soup = BeautifulSoup(page.content, "lxml")
		records = []
		record = []
		count = 0
		for tag in soup.select("tbody tr td"):
			count += 1
			record.append(tag.text.strip())
			if count % 5 == 0:
				records.append(record)
				record = []

		# print(records)
		with open("state.csv", "w") as csvFile:
			writer = csv.writer(csvFile)
			writer.writerows(records)

if __name__ == '__main__':
	reg_list = parse("Regular.csv")
	mid_list = parse("Midgrade.csv")
	pre_list = parse("Premium.csv")

	plotting = Plotting()
	# plotting.lineGraph("Weekly gas price", (np.array(reg_list),"regular")
	# 	,(np.array(mid_list),"midgrade"),(np.array(pre_list),"premium"))

	analyze = Analysis()
	stats = analyze.getStats((np.array(reg_list),"regular"), 
		(np.array(mid_list),"midgrade"),(np.array(pre_list),"premium"), (np.array(pre_list),"premium12"))
	plotting.barGraph("mean vs max vs min", np.array(stats))
	# WebScrape()










