class Video:
    ''' An instance of Video represents a thermal video in its entirety.
    Each instance of Video contains the following fields:
        id (INTEGER) - The video ID (primary key)
        type (TEXT) - The style of cooking
        subtype (TEXT) - The type of food being cooked
        filename (TEXT) - The filename of the video
        analysisTableName (TEXT) - The name of the analysis table that contains the FrameData of the video
    '''
    def __init__(self, id, type, subtype, filename, analysisTableName):
        self._id = id
        self._type = type
        self._subtype = subtype
        self._filename = filename
        self._analysisTableName = analysisTableName

    @property
    def id(self):
        return self._id

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