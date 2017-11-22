import tkinter as tk
from tkinter import filedialog
import sys
import os
import flipper
import threading
import queue

class FlipperGui(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master, padx=12, pady=3)

        self.master = master
        self.queue = queue.Queue()

        self.grid()

        self.inputLabel = tk.Label(self, text='File or URL')
        self.inputLabel.grid(row=0, column=0, sticky=tk.W)

        self.inputEntry = tk.Entry(self, width=60)
        self.inputEntry.grid(row=0, column=1)

        self.inputButton = tk.Button(self, text='Browse', command=self.openFile)
        self.inputButton.grid(row=0, column=2, sticky=tk.E)

        self.deckNameLabel = tk.Label(self, text='Deckname')
        self.deckNameLabel.grid(row=1, column=0, sticky=tk.W)

        self.deckNameEntry = tk.Entry(self, width=60)
        self.deckNameEntry.grid(row=1, column=1)
        self.deckNameEntry.insert(0,'Deck')

        self.progressLabel = tk.Label(self, text='Ready')
        self.progressLabel.grid(row=2, column=1, sticky=tk.W)

        self.generateButton = tk.Button(self, text='Generate', command=self.generate)
        self.generateButton.grid(row=2, column=2, sticky=tk.E)

        self.processQueue()

    def processQueue(self):
        while self.queue.qsize():
            try:
                msg = self.queue.get(0)
                if msg == 'done':
                    self.enableInputs()
                    self.updateProgressLabel('All done!')
                else:
                    self.updateProgressLabel(msg)
            except Queue.Empty:
                pass
        self.master.after(100, self.processQueue)

    def openFile(self):
        currentdir = os.path.dirname(os.path.realpath(__file__))
        filename = filedialog.askopenfilename(initialdir=currentdir,parent=self,title='Decklist')
        self.inputEntry.delete(0, tk.END)
        self.inputEntry.insert(0, filename)

    def generate(self):
        inputStr = self.inputEntry.get()
        deckName = self.deckNameEntry.get()
        if len(inputStr) == 0:
            self.updateProgressLabel('Must give filename or URL')
            return
        if len(deckName) == 0:
            self.updateProgressLabel('Must give a deckname')
            return
        self.thread = threading.Thread(target=flipper.generate,args=(inputStr, deckName),kwargs={'queue':self.queue})
        self.thread.start()
        self.disableInputs()
        self.updateProgressLabel('Generating....')
    
    def disableInputs(self):
        self.inputEntry.config(state='disabled')
        self.inputButton.config(state='disabled')
        self.deckNameEntry.config(state='disabled')
        self.generateButton.config(state='disabled')

    def enableInputs(self):
        self.inputEntry.config(state='normal')
        self.inputButton.config(state='normal')
        self.deckNameEntry.config(state='normal')
        self.generateButton.config(state='normal')

    def updateProgressLabel(self, message):
        self.progressLabel['text'] = message


root = tk.Tk()
root.title('Tableflipper Extreme')
app = FlipperGui(master=root)
root.mainloop()
