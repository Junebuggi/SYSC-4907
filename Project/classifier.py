from numpy.lib.function_base import average
from classification import Classification
import numpy as np

def classifyStaticVideo(frameData):
    classifications = {}
    prevPanTemp = None

    for frame in frameData:
        timeElapsed, panTemp, panArea, numFood, foodTemp, foodArea = frame

        # Open element or empty pan
        if numFood == 0:

            # Initialize prevPanTemp to be the panTemp of the first sample
            if prevPanTemp is None: prevPanTemp = panTemp
            
            # Determine if the open element or empty pan is heating up or cooling down
            if panTemp >= prevPanTemp:
                classifications[timeElapsed] = Classification.HEATING_UP.name
            else:
                classifications[timeElapsed] = Classification.COOLING_DOWN.name

        # Food is present; Determine if the food is being fried, boiled, or braised
        else:
            # Convert string of food temps to a list of floats
            foodTempList = foodTemp[1:len(foodTemp)-1].split(',')
            foodTempList = [float(foodTempElement.strip()) for foodTempElement in foodTempList]

            # Classify cooking method based on temperature difference between pan and food
            if average(foodTempList) < panTemp - 50:
                classifications[timeElapsed] = Classification.FRYING.name
            elif panTemp - 50 <= average(foodTempList) < panTemp - 20:
                classifications[timeElapsed] = Classification.BOILING.name
            elif panTemp - 20 <= average(foodTempList) < panTemp:
                classifications[timeElapsed] = Classification.BRAISING.name
            else:
                classifications[timeElapsed] = Classification.UNKNOWN.name

        # Store pan temp so we can detect if we are heating up or cooling down
        prevPanTemp = panTemp

    return classifications