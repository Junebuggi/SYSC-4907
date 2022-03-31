import database as db
import os
import matplotlib.pyplot as plt
from pandas import DataFrame
import numpy as np
from matplotlib import pyplot as plt
from scipy.signal import find_peaks
import math
from scipy import stats

def getTemperatureData(Analysis_Table_Name):
    df = DataFrame(db.get_all_frame_data(Analysis_Table_Name))
    df.drop(df.columns[[2,3,5,6]], axis = 1, inplace = True)
    df.columns = ["Time", "Pan", "Food"]
    df["Food"] = df["Food"].apply(lambda x: x.replace("[", ""))
    df["Food"] = df["Food"].apply(lambda x: x.replace("]", ""))
    #df = df[df['Food'] != ""] 
    df["Food"] = df["Food"].apply(lambda x: x.split(",")[-1])
    df["Food"] = df["Food"].apply(lambda x: round(float(x),1) if x != "" else x)
    df["Pan"] = df["Pan"].apply(lambda x: round(float(x),1))
    return df

 #Classification Main Function
    

def classification(x, y, yPan, order = 1):
    classification = ""
    xFinal = x.copy().values.tolist()
    yFinal = y.copy().values.tolist()
    yPanFinal = yPan.copy().values.tolist()
    returnString = ""
    #Check if increasing
    result = np.polyfit(x, yPan, order)
    slope = result[-2]
    #Increasing
    if slope > 0.1:
        df = DataFrame()
        df["Time"] = x
        df["Food"] = y
        df = df[df["Food"]!= ""]
        x = df["Time"].values.tolist()
        y = df["Food"].values.tolist()
        
            #Now check for spikes
        peaks, _ = find_peaks(np.gradient(np.gradient(y)))
        #plt.plot(x,y)
        #plt.show()
        if (len(peaks) >= 1):
            rho = np.corrcoef(x,y)

            pieces = peakPieceWiseDivide(x,y, peaks)
            prevSlope = None
            for x,y in pieces:
                slope, intercept = np.polyfit(x, y, 1)
                duration = int(x[-1])-int(x[0])
                string = "A slope of {}C is observed for {} seconds\n".format((round(float(slope),2)), duration)
                returnString += string
                if(slope > 0.4 and duration >= 20 and prevSlope != None and prevSlope*1.3 < slope):
                        returnString += "Flip Detected at ~{}-{} seconds\n".format(x[0], x[1])
                prevSlope = slope
            if rho[0][1] > 0.9:
                returnString += "Boiling\n"
                classification = "Boiling"
                return  returnString, xFinal, yFinal, classification
            else:
                
                returnString += "Frying\n"
                classification = "Frying"
                return  returnString, xFinal, yFinal, classification

        else:
            returnString += "Boiling\n"
            returnString += "No peaks observed\n"
            classification = "Boiling"
        
        return  returnString, xFinal, yFinal, classification
    
        
            
    #Decreasing or staying the same
    else:
        y = yPan
        if(abs(slope) < 0.1):
            if(len(y) > 40):
                returnString += "Send notification! Stove on too long!\n"
                classification = "On Too Long"
            else:
                classification = "Steady Temperature"
                returnString += "Stove is at steady temperature and not unattended\n"
        else:
            returnString += "Stove is cooling down\n"
            curve_fit = np.polyfit(x, np.log(y), 1)
            roomTempTime = np.log(22/math.e**curve_fit[1])/curve_fit[0]
            returnString += "Time remaining until stove is room temperature (22 C) is " + str(int(roomTempTime - len(x)*10)) + " seconds\n"
            classification = "Cooling Down"
            return returnString, xFinal, yPanFinal, classification
    return  returnString, xFinal, yPanFinal, classification
    

def peakPieceWiseDivide(x,y, peaks):
    pieces = []
    last = 0
    for p in peaks:
        piece = [x[last:p+1], y[last:p+1]]
        pieces.append(piece)
        last = p
    
    piece = [x[last:len(x)], y[last:len(x)]]
    pieces.append(piece)

    return pieces

"""
Documentation: TO-DO
Pass it the table name and it will return the classification as a string
"""
def classifyTable(tableName):
    df = getTemperatureData(tableName)
    str, x, y, classif = classification(df["Time"], df["Food"], df["Pan"])
    return classif

if __name__ == '__main__':
    # df = getTemperatureData("Cool_Down_Analysis_Table_1")
    # string, x, y, classification = classification(df["Time"], df["Food"], df["Pan"])
    # #print(str + "\n")

    # df = getTemperatureData("Water_Analysis_Table_1")
    # string, x, y, classification = classification(df["Time"], df["Food"], df["Pan"])
    # #print(str + "\n")


    # df = getTemperatureData("Egg_Analysis_Table_1")
    # string, x, y, classification = classification(df["Time"], df["Food"], df["Pan"])
    # #print(str + "\n")

    # df = getTemperatureData("Safety_Test_Analysis_Table_1")
    # string, x, y, classification = classification(df["Time"], df["Food"], df["Pan"])
    # #print(str + "\n")
    print(classifyTable("Safety_Test_Analysis_Table_1"))

    df = getTemperatureData("Safety_Test_Analysis_Table_2")
    string, x, y, classification = classification(df["Time"], df["Food"], df["Pan"])
    #print(str + "\n")
