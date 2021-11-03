class Video:
    ''' An instance of Video represents a thermal video in its entirety.
    Video records are stored in the videos master table.

    Each instance of Video contains the following fields:
        id (INTEGER) - The video ID (auto incremented primary key)
        type (TEXT) - The style of cooking (e.g., Frying)
        subtype (TEXT) - The type of food being cooked (e.g., Chicken)
        filename (TEXT) - The filename of the video
        analysisTableName (TEXT) - The name of the analysis table that contains the FrameData of the video
    '''
    def __init__(self, type, subtype, filename, analysisTableName):
        self._type = type
        self._subtype = subtype
        self._filename = filename
        self._analysisTableName = analysisTableName

    @property
    def type(self):
        return self._type

    @property
    def subtype(self):
        return self._subtype

    @property
    def filename(self):
        return self._filename

    @property
    def analysisTableName(self):
        return self._analysisTableName

    def get_as_record(self):
        return (self.type, self.subtype, self.filename, self.analysisTableName)