import os
from tkinter import Tk, Button, Frame, Label, StringVar, filedialog, DISABLED, NORMAL
from database import add_video_from_filename
from threading import Thread

class DatabaseClient(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.pack()
        self.makeWidgets()

    def makeWidgets(self):
        self.btnAddVideos = Button(self, text='Add Videos', command=self.handleAddVideos)
        self.btnAddVideos.pack()
        self.txtStatus = StringVar(value='STATUS : Ready')
        self.lblStatus = Label(self, textvariable=self.txtStatus, bg='green', fg='white')
        self.lblStatus.pack()

    def handleAddVideos(self):
        # Get videos to be added to the database
        filenames = filedialog.askopenfilenames(parent=self, title='Choose files',
                                                initialdir=os.getcwd(), filetypes=[('MP4', '*.mp4')])

        # Disable the "Add Videos" button until the import is done
        self.disableGUI()

        # Create a thread so that the GUI does not get blocked
        TaskAddVideos(self, filenames).start()

    def update(self):
        self.enableGUI()

    def enableGUI(self):
        self.btnAddVideos['state'] = NORMAL
        self.txtStatus.set('STATUS : Ready')
        self.lblStatus.config(bg='green', fg='white')

    def disableGUI(self):
        self.btnAddVideos['state'] = DISABLED
        self.txtStatus.set('STATUS : Busy')
        self.lblStatus.config(bg='red', fg='white')

class TaskAddVideos(Thread):
    def __init__(self, caller, filenames):
        super().__init__()
        self.caller = caller
        self.filenames = filenames

        # Verify that the caller has a notify() method
        update_op = getattr(self.caller, 'update', None)
        if not callable(update_op):
            raise AttributeError('The object that is calling this task does not have an update() method')

    def run(self):
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