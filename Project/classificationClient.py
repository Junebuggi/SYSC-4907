import database as db
import os
import tkinter as tk
from database import add_video_from_filename
from threading import Thread
from matplotlib.figure import Figure
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, 
NavigationToolbar2Tk)
from pandas import DataFrame
import classificationAnalyzer as CA
import numpy as np


class classifierGUI:
    def __init__(self):
        
        self.root = tk.Tk()
        self.canvas = -1
        self.plot1 = -1
        self.v = tk.IntVar()
        self.v.set(1)  # initializing the choice, i.e. Python

        vids = db.get_all_videos()
        self.scenarios = []
        i = 0
        for vid in vids:
            self.scenarios.append((i,vid[2], vid[4]))
            i += 1
        
        self.root.title("Classification Client")
        tk.Label(self.root, 
                text="""Choose a Cooking Scenario to Analyze!""",
                justify = tk.LEFT,
                padx = 20).pack()

        tk.Button(self.root, text = "Run", command = self.handleClassifyVideo).pack(anchor=tk.W)

        for idx, scenario, file in self.scenarios:
            tk.Radiobutton(self.root, 
                        text=scenario,
                        indicatoron = 0,
                        padx = 20, 
                        variable=self.v, 
                        command=self.ShowChoice,
                        value=idx).pack(anchor=tk.W)



        self.text = tk.Text(self.root, height = 8)
        self.text.pack(anchor=tk.E)
        self.createPlot()
        self.root.mainloop()

    def ShowChoice(self):
        df = CA.getTemperatureData(self.scenarios[self.v.get()][2])

    def handleClassifyVideo(self):
        df = CA.getTemperatureData(self.scenarios[self.v.get()][2])
        string, x, y, classification = CA.classification(df["Time"], df["Food"], df["Pan"])
        self.clearToTextInput(self.text)
        self.text.insert(tk.INSERT, string)
        print("Clicked")
        self.plot(x,y)

    def clearToTextInput(self, my_text):
        my_text.delete("1.0","end")

    def createPlot(self):
        fig = Figure(figsize = (6, 6),
                    dpi = 100)

        # the figure that will contain the plot
        self.plot1 = fig.add_subplot(111)
        fig.subplots_adjust(left=0.125, bottom=0.1, right=0.9, top=0.9, wspace=0.00001, hspace=0.0001)

        # creating the Tkinter canvas
        # containing the Matplotlib figure
        self.canvas = FigureCanvasTkAgg(fig,
                                master = self.root)  
        self.canvas.draw()
    
        # placing the canvas on the Tkinter window
        self.canvas.get_tk_widget().pack()
    
        # creating the Matplotlib toolbar
        toolbar = NavigationToolbar2Tk(self.canvas,
                                    self.root)
        toolbar.update()
    
        # placing the toolbar on the Tkinter window
        self.canvas.get_tk_widget().pack()

    def plot(self, x, y):
        # adding the subplot
        self.plot1.clear()
        
        self.plot1.plot(x, y, marker='x')  
        print(x)
        self.plot1.set_title("Graph of Surface Temperature Recorded over Time")
        self.plot1.set_xlabel("Time (in seconds)")
        self.plot1.set_ylabel("Temperature (C)")
        self.canvas.draw()



if __name__ == '__main__':
    classifierGUI()