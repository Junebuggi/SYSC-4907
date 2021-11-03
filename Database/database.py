import sqlite3
from sqlite3 import IntegrityError
from Models.video import Video
from Models.frame_data import FrameData

def create_videos_table():
    conn = sqlite3.connect('Database/test.db')
    c = conn.cursor()

    # Check if the videos table already exists
    c.execute("SELECT COUNT(name) FROM sqlite_master WHERE type='table' AND name='videos'")
    if c.fetchone()[0] == 0:
        c.execute('''CREATE TABLE videos (
                        id INTEGER PRIMARY KEY,
                        type TEXT,
                        subtype TEXT,
                        filename TEXT,
                        analysisTableName TEXT
                    )''')
        c.close()
        conn.commit()
    conn.close()

def insert_video(video):
    conn = sqlite3.connect('Database/test.db')
    c = conn.cursor()
    try:
        c.execute('INSERT INTO videos VALUES (?, ?, ?, ?, ?)',
                        (video.id, video.type, video.subtype, video.filename, video.analysisTableName))
        conn.commit()
    except AttributeError:
        print('Video to be inserted is not of type Video: {}'.format(type(video)))
    except IntegrityError:
        print('Video ID {} already exists in the videos table', video.id)
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
    c = conn.cursor()

    # Check if the analysis table already exists
    c.execute("SELECT COUNT(name) FROM sqlite_master WHERE type='table' AND name=?", (name,))
    if c.fetchone()[0] == 0:
        # Must use string formatting since sqlite3 doesn't support variable table names
        c.execute('''CREATE TABLE {} (
                        timeElapsed INTEGER PRIMARY KEY,
                        panTemp REAL,
                        panArea INTEGER,
                        numFood INTEGER,
                        foodTemp TEXT,
                        foodArea TEXT
                    )'''.format(name))
        c.close()
        conn.commit()
    conn.close()

def insert_frame_data(frameData, analysisTableName):
    conn = sqlite3.connect('Database/test.db')
    c = conn.cursor()
    try:
        # Must use string formatting since sqlite3 doesn't support variable table names
        c.execute('INSERT INTO {} VALUES (?, ?, ?, ?, ?, ?)'.format(analysisTableName),
                        (frameData.timeElapsed, frameData.panTemp, frameData.panArea,
                         frameData.numFood, frameData.foodTemp, frameData.foodArea))
        conn.commit()
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
    video1 = Video(1, 'Frying', 'Chicken', 'filename', 'AnalysisTable1')
    video2 = Video(2, 'Frying', 'Steak', 'filename', 'AnalysisTable2')
    insert_video(video1)
    insert_video(video2)
    fd1 = FrameData(10, 30, 40, 2, 'foodtemp', 'foodarea')
    insert_frame_data(fd1, 'AnalysisTable1')
    print(get_all_videos())
    print(get_all_frame_data('AnalysisTable1'))