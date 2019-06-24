# Written by Alvin Lin on 06/24/19
# this file is to written for testing for predictWin.py
# this file configures the predictWin UI setting
# and it behaves like a client to interact with server.py
import matplotlib.pyplot as plt 
import tkinter as tk
import fetchData
import socket
import pickle

HOST = "localhost"      # on the same machine   
PORT = 5551             # as long as this is unassigned

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

class PredictWin(tk.Tk):
	def __init__(self):
		'''show the main window'''
		super().__init__()
		self._f = fetchData.fetcher()
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
		with socket.socket() as s:
			s.connect((HOST, PORT))
			mesg = str(self._areas[self._live.get()]-1) + "," + str(self._gas[self._gasType.get()]-1) + "," + self._time.get()
			s.send(mesg.encode('utf-8'))
			fromServer = pickle.loads(s.recv(1024))
			self.updateLabel("The next "+self._time.get()[0:-2]+" gas price "+"is "+str(fromServer))
			s.close()

	def updateLabel(self, fromServer):
		self.result.config(text=fromServer)
		self.update()


if __name__ == '__main__':
	win = PredictWin()
	win.mainloop()

	





