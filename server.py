# Written by Alvin Lin on 06/24/19
# this file is to contruct a local server and calculate the machine learning 
# model and return the prediction to the client
from pandas import DataFrame
from pandas import concat
import csv
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from keras.layers.recurrent import LSTM
from keras.layers.core import Dense, Dropout
from math import sqrt
from sklearn.metrics import mean_squared_error
import socket
import fetchData
import pickle

HOST = "localhost"      # on the same machine   
PORT = 5551             # as long as this is unassigned

class Predict():
	def __init__(self):
		self._f = fetchData.fetcher()
		pass
 
	def series_to_supervised(self, data, n_in=1, n_out=1, dropnan=True):
		"""
		Frame a time series as a supervised learning dataset.
		Arguments:
			data: Sequence of observations as a list or NumPy array.
			n_in: Number of lag observations as input (X).
			n_out: Number of observations as output (y).
			dropnan: Boolean whether or not to drop rows with NaN values.
		Returns:
			Pandas DataFrame of series framed for supervised learning.
		author: Jason Brownlee
		"""
		n_vars = 1 if type(data) is list else data.shape[1]
		df = DataFrame(data)
		cols, names = list(), list()
		# input sequence (t-n, ... t-1)
		for i in range(n_in, 0, -1):
			cols.append(df.shift(i))
			names += [('var%d(t-%d)' % (j+1, i)) for j in range(n_vars)]
		# forecast sequence (t, t+1, ... t+n)
		for i in range(0, n_out):
			cols.append(df.shift(-i))
			if i == 0:
				names += [('var%d(t)' % (j+1)) for j in range(n_vars)]
			else:
				names += [('var%d(t+%d)' % (j+1, i)) for j in range(n_vars)]
		# put it all together
		agg = concat(cols, axis=1)
		agg.columns = names
		# drop rows with NaN values
		if dropnan:
			agg.dropna(inplace=True)
		return agg

	# use machine learning to predict the next period's gas price
	# param: a list of gas prices in float
	# return: the next period's gas price and root mean square error
	def predictError(self, values):
		# convert time-seried to supervised
		reframed = self.series_to_supervised(values)
		# print(values)
		# print(reframed)

		scaler = MinMaxScaler(feature_range=(0, 1))
		scaled = scaler.fit_transform(reframed)

		# split into train and test sets
		values = scaled
		# n_train_days = 2 * 365
		n_train_days = int(len(values) * 0.9)
		train = values[:n_train_days, :]
		test = values[n_train_days:, :]
		# split into input and outputs
		train_X, train_y = train[:, :-1], train[:, -1]
		test_X, test_y = test[:, :-1], test[:, -1]
		# reshape input to be 3D [samples, timesteps, features]
		train_X = train_X.reshape((train_X.shape[0], 1, train_X.shape[1]))
		test_X = test_X.reshape((test_X.shape[0], 1, test_X.shape[1]))
		# print(train_X.shape, train_y.shape, test_X.shape, test_y.shape)

		# design network
		model = Sequential()
		model.add(LSTM(50, input_shape=(train_X.shape[1], train_X.shape[2])))
		model.add(Dense(1))
		model.compile(loss='mae', optimizer='adam')
		# fit network
		history = model.fit(train_X, train_y, epochs=50, batch_size=91, validation_data=(test_X, test_y), verbose=2,
		                    shuffle=False)

		# make a prediction
		yhat = model.predict(test_X)
		# print(yhat)
		test_X = test_X.reshape((test_X.shape[0], test_X.shape[2]))
		# invert scaling for forecast
		inv_yhat = np.concatenate((test_X[:, 0:], yhat), axis=1)
		inv_yhat = scaler.inverse_transform(inv_yhat)
		inv_yhat = inv_yhat[:, -1]
		# print(inv_yhat)
		# invert scaling for actual
		test_y = test_y.reshape((len(test_y), 1))
		inv_y = np.concatenate((test_X[:, 0:], test_y), axis=1)
		inv_y = scaler.inverse_transform(inv_y)
		inv_y = inv_y[:, -1]
		# calculate RMSE
		rmse = sqrt(mean_squared_error(inv_y, inv_yhat))

		# for i in range(len(inv_yhat)):
		# 	print(inv_y[i], inv_yhat[i])
		# print(inv_yhat[-1])
		return inv_yhat[-1], rmse

	def fetchData(self, fromClient):
		params = fromClient.split(",")
		period = 0
		if params[2] == "Weekly":
			period = 0
		elif params[2] == "Monthly":
			period = 1
		elif params[2] == "Yearly":
			period = 2

		data = self._f.getRecordsByAreaGasTime(int(params[0]), int(params[1]), int(period))
		values = [float(row[3]) for row in data]
		result, error = self.predictError(values)

		return result



if __name__ == '__main__':
	predict_obj = Predict()
	# # get data
	# testList = parse("Regular.csv")
	# values = [float(row[1]) for row in testList]
	# reg_predcit, reg_error = predict_obj.predictError(values)

	# testList = parse("Midgrade.csv")
	# values = [float(row[1]) for row in testList]
	# mid_predict, mid_error = predict_obj.predictError(values)

	# testList = parse("Premium.csv")
	# values = [float(row[1]) for row in testList]
	# pre_predict, pre_error = predict_obj.predictError(values)

	# print(reg_error, mid_error, pre_error, (reg_error+mid_error+pre_error)/3)
	# print(reg_predcit, mid_predict, pre_predict)

	with socket.socket() as s:
		s.bind((HOST, PORT))
		while True:
			s.listen()
			print("server ready")
			(conn, addr) = s.accept()
			fromClient = conn.recv(1024).decode('utf-8')
			mesg = predict_obj.fetchData(fromClient)
			conn.send(pickle.dumps(mesg))







	

