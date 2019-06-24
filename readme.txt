Team: 
Alvin Lin: data analysis / visualization / prediction(machine learning) / network
Weiyuan Chen: GUI, system
Tianqi Yang: web access, database
---------------------------------------------------------------
Description:
The projcet, Gas_Price_Analysis, has 6 functionalities which are show plots from 2000 to 2018, show table with date and gas price, show mean,max,min in a bargraph, show a U.S. map of gas prices, and show next week/month/year gas price pridiction. All functionalities will be visualized in a gui.

gui.py: shows the 6 functionalities as buttons and offers choice and input for user to choose.

buildCarMpg.py: fetch car’s mpg information from a web site and save the data in the database.

buildDatabase.py: fetch gas price records and save in the database.

fetchData.py: the class that finds the record from the database.

button-cost.py: the button that calculates the cost for the user in the main GUI

button-table.py: the button that shows the records that user want to see and could be saved in the file.

Plotting.py: This file has three major functions for scattered plot and bargraph, and they are Plotting.lineGraph(), Plotting.barGraph(), and Analysis.getStats(). The rest of the functions are for testing.

map.py: This file is to construct the map window after user click on “map” in the main window.

predict.py: This file is to construct the predict window after user click on “predict” in the main window. One of the method(handlePredict) is to ask server.py to give back the prediction result based on the input it sends.

server.py: This file will be executed first and listen to clients forever. It is to accept the data from the client and calculate the prediction and return it to user.

3 images for map: midgrade.png, premium.png, regular.png

3 csv files for testing: midgrade.csv, premium.csv, regular.csv
---------------------------------------------------------------
Usage:
1. Execute server.py and wait until “server ready” in the command line (this requires keras and sklearn installed, if you do not have it, you can skip server.py)
2. Execute gui.py(the last choice “predict” requires server.py, if you do not run server.py, do not click on that button)
note: if fail to open server.py, gui.py is still working with other 5 buttons

Problems for the prediction button and this migth be a solution in Windows system:
https://github.com/antoniosehk/keras-tensorflow-windows-installation
1.follow above link to install to step 7.
2.in command line type pip install keras
3.in command line type pip install tensorflow
Should be ok now

