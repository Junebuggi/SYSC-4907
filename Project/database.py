import sqlite3
import os
from fnmatch import fnmatch
from sqlite3 import IntegrityError
from Models.video import Video
from Models.frame_data import FrameData
from thermalImageProcessing import processVideo
from classifier import classifyStaticVideo
from classificationAnalyzer import classifyTable

DATABASE = 'Project/thermal_cooking.db'

def generate_database():
    ''' Create a database based on the Test Data folder.
    Delete the database if it already exists.
    For each thermal video in the Test Data folder:
        1. Create an analysis table.
        2. Add records (FrameData) to the analysis table for each sampled frame.
        3. Add a record (Video) to the videos master table.
    
    Args:
        None
    
    Returns:
        None
    '''
    # Delete database if it already exists
    if os.path.exists(DATABASE):
        print('Removing existing database {}'.format(DATABASE))
        os.remove(DATABASE)

    # Get all filenames of thermal videos in Test Data folder
    TEST_DATA_FOLDER = 'Test Data'
    PATTERN = '*.mp4'
    filenames = []

    for path, subdirs, files in os.walk(TEST_DATA_FOLDER):
        for name in files:
            if fnmatch(name, PATTERN):
                filenames.append(os.path.join(path, name))

    # Iterate through each video
    for filename in filenames:
        add_video_from_filename(filename)



def create_videos_table():
    ''' Create the master videos table.
    The master videos table stores high-level information about thermal videos.
    This inlcudes the style of cooking (e.g., frying), the food being cooked (e.g., chicken), the
    filepath of the thermal video, the corresponding analysis table, and the registered stove ID.
    
    Args:
        None
    
    Returns:
        None
    '''
    conn = sqlite3.connect(DATABASE)
    with conn:
        c = conn.cursor()
        # Check if the videos table already exists
        c.execute("SELECT COUNT(name) FROM sqlite_master WHERE type='table' AND name='videos'")
        if c.fetchone()[0] == 0:
            c.execute('''CREATE TABLE videos (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            type TEXT,
                            subtype TEXT,
                            filename TEXT,
                            analysis_table_name TEXT,
                            classification TEXT,
                            stoveId INTEGER
                        )''')
        c.close()
    conn.close()



def insert_video(video):
    ''' Insert a video into the master videos table.
    
    Args:
        video (Video): The video to insert
    
    Returns:
        None
    '''
    # Create videos table if it does not already exist
    create_videos_table()

    conn = sqlite3.connect(DATABASE)
    with conn:
        c = conn.cursor()
        try:
            c.execute('INSERT INTO videos VALUES (null, ?, ?, ?, ?, ?, ?)', video.get_as_record())
            print('Successfully inserted video {}'.format(video.filename))
        except AttributeError:
            print('Video to be inserted is not of type Video: {}'.format(type(video)))
        except:
            print('An unexpected error occurred when inserting a record into the videos table')
        finally:
            c.close()
    conn.close()



def get_all_videos():
    ''' Get all the videos from the master videos table.
    
    Args:
        None
    
    Returns:
        list: All videos in the master videos table
    '''
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT * FROM videos')
    videos = c.fetchall()
    c.close()
    conn.close()
    return videos



def get_video_by_id(id):
    ''' Get a video by its ID from the master videos table.
    
    Args:
        id (int): The ID to search for
    
    Returns:
        Video: The video with the ID provided
    '''
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT * FROM videos WHERE id=?', (id,))
    video = c.fetchone()
    c.close()
    conn.close()
    return video



def get_videos_by_type(type):
    ''' Get all the videos from the master videos table with the
    type provided (e.g., frying).
    
    Args:
        type (str): The type to search for
    
    Returns:
        list: All videos in the master videos table with the type
    '''
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT * FROM videos WHERE type=?', (type,))
    videos = c.fetchall()
    c.close()
    conn.close()
    return videos



def get_videos_by_subtype(subtype):
    ''' Get all the videos from the master videos table with the
    subtype provided (e.g., chicken).
    
    Args:
        subtype (str): The subtype to search for
    
    Returns:
        list: All videos in the master videos table with the subtype
    '''
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT * FROM videos WHERE subtype=?', (subtype,))
    videos = c.fetchall()
    c.close()
    conn.close()
    return videos



def get_videos_by_stoveId(stoveId):
    ''' Get all the videos from the master videos table with the
    registered stove ID.
    
    Args:
        stoveId (str): The stove ID to search for
    
    Returns:
        list: All videos in the master videos table with the stove ID
    '''
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT * FROM videos WHERE stoveId=?', (stoveId,))
    videos = c.fetchall()
    c.close()
    conn.close()
    return videos



def create_analysis_table(name):
    ''' Return the modified name of the analysis table created for a given name.
    Appends a unique, incrementing index to the end of the analysis table name.

    Example:
        chicken => Chicken_Analysis_Table_1
        Chicken => Chicken_Analysis_Table_2
        ground beef => Ground_Beef_Analysis_Table_1

    Arg:
        name (str): The original name of the analysis table
    
    Returns:
        string: The modified name of the analysis table
    '''
    # Replace spaces with underscores
    name = name.title().replace(' ', '_')

    # Index of the analysis table
    tableIndex = 1
    baseName = '{}_Analysis_Table'.format(name)

    conn = sqlite3.connect(DATABASE)
    with conn:
        c = conn.cursor()
        while True:
            # Format the analysis table name to include an index
            name = '{}_{}'.format(baseName, tableIndex)
            # Check if the analysis table already exists
            c.execute("SELECT COUNT(name) FROM sqlite_master WHERE type='table' AND name=?", (name,))
            if c.fetchone()[0] == 0:
                break
            # Increment the analysis table index until the table name is unique
            tableIndex += 1
        # Must use string formatting since sqlite3 doesn't support variable table names
        c.execute('''CREATE TABLE {} (
                        time_elapsed INTEGER PRIMARY KEY,
                        pan_temp REAL,
                        pan_area INTEGER,
                        num_food INTEGER,
                        food_temp TEXT,
                        food_area TEXT,
                        classification TEXT
                    )'''.format(name))
        c.close()
    conn.close()
    print('{} created'.format(name))
    return name



def insert_one_frame_data(frameData, analysisTableName):
    ''' Insert a FrameData record into an analysis table.
    
    Args:
        frameData (FrameData): The FrameData to insert
        analysisTableName (str): The name of the analysis table to insert to
    
    Returns:
        None
    '''
    conn = sqlite3.connect(DATABASE)
    with conn:
        c = conn.cursor()
        try:
            # Must use string formatting since sqlite3 doesn't support variable table names
            c.execute('INSERT INTO {} VALUES (?, ?, ?, ?, ?, ?, ?)'.format(analysisTableName),
                       frameData.get_as_record())
        except AttributeError:
            print('Frame data to be inserted is not of type FrameData: {}'.format(type(frameData)))
        except IntegrityError:
            print('A record with a Time Elapsed of {} already exists in analysis table {}'.format(
                frameData.timeElapsed, analysisTableName))
        finally:
            c.close()
    conn.close()



def insert_many_frame_data(frameDataList, analysisTableName):
    ''' Insert multiple FrameData records into an analysis table.
    
    Args:
        frameData (FrameData): The FrameData to insert
        analysisTableName (str): The name of the analysis table to insert to
    
    Returns:
        None
    '''
    conn = sqlite3.connect(DATABASE)
    with conn:
        c = conn.cursor()
        try:
            # Must use string formatting since sqlite3 doesn't support variable table names
            c.executemany('INSERT INTO {} VALUES (?, ?, ?, ?, ?, ?, ?)'.format(analysisTableName),
                       [frameData.get_as_record() for frameData in frameDataList])
        except AttributeError:
            print('Frame data to be inserted is not a list of FrameData: {}'.format(type(frameDataList)))
        except IntegrityError:
            print('A record in the frame data set contains a time_elapsed that already '\
                  'exists in analysis table {}'.format(analysisTableName))
        finally:
            c.close()
    conn.close()



def get_all_frame_data(analysisTableName):
    ''' Get all FrameData records from an analysis table.
    
    Args:
        analysisTableName (str): The analysis table containing the FrameData
    
    Returns:
        list: All FrameData in an analysis table
    '''
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT * FROM {}'.format(analysisTableName))
    frameData = c.fetchall()
    c.close()
    conn.close()
    return frameData



def add_video_from_filename(filename):
    ''' Analyzes a video given its filename and stores its analytical data
    (FrameData records) into the database.

    The provided filename must contain the 'Test Data' folder as part of its path.

    Args:
        filename (str): The filename of the video to analyze and store

    Returns:
        None
    '''
    # Replace '\\' with '/' to handle incoming filenames
    filename = filename.replace('\\', '/')

    # Trim leading path up until the Test Data folder
    filename = filename[filename.find('Test Data'):]

    # Get the type of the video (e.g., Frying)
    type = filename.split('/')[1]

    # Get the subtype of the video (e.g., Chicken)
    subtype = filename[filename.find('[')+1:filename.find(']')]

    # Create an analysis table whose name is based on the subtype
    analysisTableName = create_analysis_table(subtype)

    # Set stove ID to 1 since we only have one stove
    stoveId = 1

    # Get frame data from video
    frameData = processVideo(filename, 10)

    # Classify frame data at each elapsed time interval
    frameByFrameClassifications = classifyStaticVideo(frameData)

    # Add frame data to the analysis table
    frameDataObjs = []
    for (timeElapsed, panTemp, panArea, numFood, foodTemp, foodArea) in frameData:
        frameByFrameClassification = frameByFrameClassifications[timeElapsed]
        newFrameData = FrameData(timeElapsed, panTemp, panArea, numFood, foodTemp, foodArea, frameByFrameClassification)
        frameDataObjs.append(newFrameData)

    insert_many_frame_data(frameDataObjs, analysisTableName)

    # Add a record to the videos master table
    overallClassification = classifyTable(analysisTableName)
    video = Video(type, subtype, filename, analysisTableName, overallClassification, stoveId)
    insert_video(video)


# Example
if __name__ == '__main__':
    frameData = get_all_frame_data('Three_Mushrooms_Analysis_Table_1')
    result = classifyStaticVideo(frameData)
    print(result)