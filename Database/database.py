import sqlite3
import os
from fnmatch import fnmatch
from sqlite3 import IntegrityError
from Models.video import Video
from Models.frame_data import FrameData
from ThermSAS import thermalImageProcessing

def generate_database():
    ''' Creates a database based on the Test Data folder.
    Deletes the database if it already exists.
    For each thermal video in the Test Data folder:
        1. Creates an analysis table.
        2. Adds records (FrameData) to the analysis table for each sampled frame.
        3. Adds a record (Video) to the videos master table.
    '''
    # Delete database if it already exists
    if os.path.exists('Database/test.db'):
        os.remove('Database/test.db')

    # Create videos master table
    create_videos_table()

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

        # Get the type of the video (e.g., Frying)
        type = filename.split('\\')[1]

        # Get the subtype of the video (e.g., Chicken)
        subtype = filename[filename.find('[')+1:filename.find(']')]

        # Create an analysis table whose name is based on the subtype
        analysisTableName = create_analysis_table(subtype)

        # Add frame data to the analysis table
        # TODO: Get FrameData from sampled video
        # frameData = []
        # insert_many_frame_data(frameData, analysisTableName)

        # Add a record to the videos master table
        video = Video(type, subtype, filename, analysisTableName)
        insert_video(video)

def create_videos_table():
    conn = sqlite3.connect('Database/test.db')
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
                            analysis_table_name TEXT
                        )''')
        c.close()
    conn.close()

def insert_video(video):
    conn = sqlite3.connect('Database/test.db')
    with conn:
        c = conn.cursor()
        try:
            c.execute('INSERT INTO videos VALUES (null, ?, ?, ?, ?)', video.get_as_record())
        except AttributeError:
            print('Video to be inserted is not of type Video: {}'.format(type(video)))
        except:
            print('An unexpected error occurred when inserting a record into the videos table')
        finally:
            c.close()
    conn.close()

def get_all_videos():
    conn = sqlite3.connect('Database/test.db')
    c = conn.cursor()
    c.execute('SELECT * FROM videos')
    videos = c.fetchall()
    c.close()
    conn.close()
    return videos

def get_video_by_id(id):
    conn = sqlite3.connect('Database/test.db')
    c = conn.cursor()
    c.execute('SELECT * FROM videos WHERE id=?', (id,))
    video = c.fetchone()
    c.close()
    conn.close()
    return video

def get_videos_by_type(type):
    conn = sqlite3.connect('Database/test.db')
    c = conn.cursor()
    c.execute('SELECT * FROM videos WHERE type=?', (type,))
    videos = c.fetchall()
    c.close()
    conn.close()
    return videos

def get_videos_by_subtype(subtype):
    conn = sqlite3.connect('Database/test.db')
    c = conn.cursor()
    c.execute('SELECT * FROM videos WHERE subtype=?', (subtype,))
    videos = c.fetchall()
    c.close()
    conn.close()
    return videos

def create_analysis_table(name):
    ''' Returns the modified name of the analysis table created for a given name.
    Appends a unique, incrementing index to the end of the analysis table name.

    Example:
        chicken => Chicken_Analysis_Table_1
        Chicken => Chicken_Analysis_Table_2
        ground beef => Ground_Beef_Analysis_Table_1
    '''
    # Replace spaces with underscores
    name = name.title().replace(' ', '_')

    # Index of the analysis table
    tableIndex = 1
    baseName = '{}_Analysis_Table'.format(name)

    conn = sqlite3.connect('Database/test.db')
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
                        food_area TEXT
                    )'''.format(name))
        c.close()
    conn.close()
    print('{} created'.format(name))
    return name

def insert_one_frame_data(frameData, analysisTableName):
    conn = sqlite3.connect('Database/test.db')
    with conn:
        c = conn.cursor()
        try:
            # Must use string formatting since sqlite3 doesn't support variable table names
            c.execute('INSERT INTO {} VALUES (?, ?, ?, ?, ?, ?)'.format(analysisTableName),
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
    conn = sqlite3.connect('Database/test.db')
    with conn:
        c = conn.cursor()
        try:
            # Must use string formatting since sqlite3 doesn't support variable table names
            c.executemany('INSERT INTO {} VALUES (?, ?, ?, ?, ?, ?)'.format(analysisTableName),
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
    conn = sqlite3.connect('Database/test.db')
    c = conn.cursor()
    c.execute('SELECT * FROM {}'.format(analysisTableName))
    frameData = c.fetchall()
    c.close()
    conn.close()
    return frameData

# Example
if __name__ == '__main__':
    generate_database()
    for video in get_all_videos():
        print(video)

    # create_videos_table()
    # create_analysis_table('AnalysisTable1')
    # create_analysis_table('AnalysisTable2')
    # video1 = Video('Frying', 'Chicken', 'filename', 'AnalysisTable1')
    # video2 = Video('Frying', 'Steak', 'filename', 'AnalysisTable2')
    # insert_video(video1)
    # insert_video(video2)
    # fd1 = FrameData(10, 30, 40, 2, 'foodtemp', 'foodarea')
    # fd2 = FrameData(20, 10, 5, 3, 'foodtemp2', 'foodarea2')
    # fd = [fd1, fd2]
    # insert_many_frame_data(fd, 'AnalysisTable1')
    # print(get_all_videos())
    # print(get_all_frame_data('AnalysisTable1'))