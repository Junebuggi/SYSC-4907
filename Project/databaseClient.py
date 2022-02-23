import os
from tkinter import Tk, Button, Frame, Label, StringVar, filedialog, DISABLED, NORMAL
from database import add_video_from_filename
from threading import Thread

class DatabaseClient(Frame):
    ''' This class launches a GUI that allows users to easily add one or multiple thermal videos
    to the thermal cooking database using File Explorer. For each thermal video selected,
    the thermal processing algorithm is executed and the analytical data is stored in the
    database.
    '''
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.pack()
        self.makeWidgets()

    def makeWidgets(self):
        ''' Create the GUI.

        Args:
            None
        
        Returns:
            None
        '''
        self.btnAddVideos = Button(self, text='Add Videos', command=self.handleAddVideos)
        self.btnAddVideos.pack()
        self.txtStatus = StringVar(value='STATUS : Ready')
        self.lblStatus = Label(self, textvariable=self.txtStatus, bg='green', fg='white')
        self.lblStatus.pack()

    def handleAddVideos(self):
        ''' Callback for the Add Videos button.
        Opens File Explorer and then starts the analysis task once the user selects some files.

        Args:
            None
        
        Returns:
            None
        '''
        # Get videos to be added to the database
        filenames = filedialog.askopenfilenames(parent=self, title='Choose files',
                                                initialdir=os.getcwd(), filetypes=[('MP4', '*.mp4')])

        # Disable the "Add Videos" button until the import is done
        self.disableGUI()

        # Create a thread so that the GUI does not get blocked
        TaskAddVideos(self, filenames).start()

    def update(self):
        ''' Enable the GUI once anlaysis is complete.

        Args:
            None
        
        Returns:
            None
        '''
        self.enableGUI()

    def enableGUI(self):
        ''' Enable the GUI.

        Args:
            None

        Returns:
            None
        '''
        self.btnAddVideos['state'] = NORMAL
        self.txtStatus.set('STATUS : Ready')
        self.lblStatus.config(bg='green', fg='white')

    def disableGUI(self):
        ''' Disable the GUI.

        Args:
            None
        
        Returns:
            None
        '''
        self.btnAddVideos['state'] = DISABLED
        self.txtStatus.set('STATUS : Busy')
        self.lblStatus.config(bg='red', fg='white')



class TaskAddVideos(Thread):

    def __init__(self, caller, filenames):
        ''' Analyze selected thermal videos and store their analytical data into the database.

        Args:
            caller (DatabaseClient): The caller of this task
            filenames (list): The list of thermal videos to add to the database
        
        Returns:
            None
        '''
        super().__init__()
        self.caller = caller
        self.filenames = filenames

        # Verify that the caller has an update() method
        update_op = getattr(self.caller, 'update', None)
        if not callable(update_op):
            raise AttributeError('The object that is calling this task does not have an update() method')

    def run(self):
        ''' Add the analytical data to the database for each thermal video.
        Enable the GUI once done.

        Args:
            None

        Returns:
            None
        '''
        for filename in self.filenames:
            add_video_from_filename(filename)
        self.caller.update()
            


def main():
    root = Tk()
    root.title('Database Client')
    root.geometry('500x200')
    client = DatabaseClient(root)
    client.mainloop()

if __name__ == '__main__':
    main()