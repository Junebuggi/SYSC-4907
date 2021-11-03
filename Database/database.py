import sqlite3
from sqlite3 import IntegrityError
from Models.video import Video
from Models.frame_data import FrameData

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
    conn = sqlite3.connect('Database/test.db')
    with conn:
        c = conn.cursor()
        # Check if the analysis table already exists
        c.execute("SELECT COUNT(name) FROM sqlite_master WHERE type='table' AND name=?", (name,))
        if c.fetchone()[0] == 0:
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

def insert_frame_data(frameData, analysisTableName):
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
    create_videos_table()
    create_analysis_table('AnalysisTable1')
    create_analysis_table('AnalysisTable2')
    video1 = Video('Frying', 'Chicken', 'filename', 'AnalysisTable1')
    video2 = Video('Frying', 'Steak', 'filename', 'AnalysisTable2')
    insert_video(video1)
    insert_video(video2)
    fd1 = FrameData(10, 30, 40, 2, 'foodtemp', 'foodarea')
    insert_frame_data(fd1, 'AnalysisTable1')
    print(get_all_videos())
    print(get_all_frame_data('AnalysisTable1'))