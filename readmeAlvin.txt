Team: 
Alvin Lin: data analysis / visualization / prediction(machine learning) / network
Weiyuan Chen: GUI, system
Tianqi Yang: web access, database


Usage:
1. Execute server.py and wait until “server ready” in the command line (this requires keras and sklearn installed, if you do not have it, you can skip server.py)
2. Execute gui.py(the last choice “predict” requires server.py, if you do not run server.py, do not click on that button)


Description:
Plotting.py: This file has three major functions for scattered plot and bargraph, and they are Plotting.lineGraph(), Plotting.barGraph(), and Analysis.getStats(). The rest of the functions are for testing.


Map.py: This file is to construct the map window after user click on “map” in the main window.


Predict.py: This file is to construct the predict window after user click on “predict” in the main window. One of the method(handlePredict) is to ask server.py to give back the prediction result based on the input it sends.


Server.py: This file will be executed first and listen to clients forever. It is to accept the data from the client and calculate the prediction and return it to user.