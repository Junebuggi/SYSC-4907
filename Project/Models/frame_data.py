class FrameData:
    ''' An instance of FrameData represents a frame that is sampled from a thermal video.
    FrameData records are stored in an analysis table pertaining to the specific thermal video file.

    Each instance of FrameData contains the following fields:
        timeElapsed (INTEGER) - The elapsed time (in seconds) since the beginning of the time the frame was sampled (primary key)
        panTemp (REAL) - The average temperature of the pan (in Celsius)
        panArea (INTEGER) - The area of the pan (in pixels)
        numFood (INTEGER) - The number of food elements
        foodTemp (TEXT) - The string representation of an array containing temperatures (in Celsius) of each identified food
        foodArea (TEXT) - The string representation of an array containing the areas (in pixels) of each identified food
    '''
    def __init__(self, timeElapsed, panTemp, panArea, numFood, foodTemp, foodArea):
        self._timeElapsed = timeElapsed
        self._panTemp = panTemp
        self._panArea = panArea
        self._numFood = numFood
        self._foodTemp = foodTemp
        self._foodArea = foodArea

    @property
    def timeElapsed(self):
        return self._timeElapsed

    @property
    def panTemp(self):
        return self._panTemp

    @property
    def panArea(self):
        return self._panArea

    @property
    def numFood(self):
        return self._numFood

    @property
    def foodTemp(self):
        return self._foodTemp

    @property
    def foodArea(self):
        return self._foodArea

    def get_as_record(self):
        return (self.timeElapsed, self.panTemp, self.panArea, self.numFood, self.foodTemp, self.foodArea)
