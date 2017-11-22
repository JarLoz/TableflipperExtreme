import tkinter as tk
from tkinter import filedialog
import sys
import os
import flipper
import threading
from deckconverter import queue
from PIL import ImageTk, Image

class FlipperGui(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master, padx=12, pady=3)

        self.master = master
        self.queue = queue.initQueue()

        self.grid()
        self.logoImage = ImageTk.PhotoImage(Image.open('logo.png'))

        self.logoLabel = tk.Label(self, image=self.logoImage)
        self.logoLabel.grid(row=0, column=0, columnspan=5)

        self.deckNameLabel = tk.Label(self, text='Deckname')
        self.deckNameLabel.grid(row=1, column=0, sticky=tk.W)

        self.deckNameEntry = tk.Entry(self, width=60)
        self.deckNameEntry.grid(row=1, column=1, columnspan=3)
        self.deckNameEntry.insert(0,'Deck')

        self.inputLabel = tk.Label(self, text='File or URL')
        self.inputLabel.grid(row=2, column=0, sticky=tk.W)

        self.inputEntry = tk.Entry(self, width=60)
        self.inputEntry.grid(row=2, column=1, columnspan=3)

        self.inputButton = tk.Button(self, text='Browse', command=self.openFile)
        self.inputButton.grid(row=2, column=4, sticky=tk.E)

        self.outputLabel = tk.Label(self, text='Output folder')
        self.outputLabel.grid(row=3, column=0, sticky=tk.W)

        self.outputEntry = tk.Entry(self, width=60)
        self.outputEntry.grid(row=3, column=1, columnspan=3)

        self.outputButton = tk.Button(self, text='Browse', command=self.openFile)
        self.outputButton.grid(row=3, column=4, sticky=tk.E)

        self.hiresVar = tk.IntVar()
        self.hiresCheckbutton = tk.Checkbutton(self, text='High Resolution', variable=self.hiresVar)
        self.hiresCheckbutton.grid(row=4, column=0, sticky=tk.W)

        self.reprintsVar = tk.IntVar()
        self.reprintsCheckbutton = tk.Checkbutton(self, text='Reprints', variable=self.reprintsVar)
        self.reprintsCheckbutton.grid(row=4, column=1, sticky=tk.W)

        self.nocacheVar = tk.IntVar()
        self.nocacheCheckbutton = tk.Checkbutton(self, text='No cache', variable=self.nocacheVar)
        self.nocacheCheckbutton.grid(row=4, column=2, sticky=tk.W)

        self.imgurVar = tk.IntVar()
        self.imgurCheckbutton = tk.Checkbutton(self, text='Imgur Upload', variable=self.imgurVar)
        self.imgurCheckbutton.grid(row=4, column=3, sticky=tk.W)

        self.progressLabel = tk.Label(self, text='Ready')
        self.progressLabel.grid(row=5, column=0, columnspan=4, sticky=tk.W)

        self.generateButton = tk.Button(self, text='Generate', command=self.generate)
        self.generateButton.grid(row=5, column=4, sticky=tk.E)

        self.processQueue()

    def processQueue(self):
        while self.queue.qsize():
            try:
                msg = self.queue.get(0)
                if msg['type'] == 'done':
                    self.enableInputs()
                    self.updateProgressLabel('All done!')
                elif msg['type'] == 'error':
                    self.enableInputs()
                    self.updateProgressLabel(msg['text'], fg='red')
                elif msg['type'] == 'message':
                    self.updateProgressLabel(msg['text'])
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
        hires = bool(self.hiresVar.get())
        reprints = bool(self.reprintsVar.get())
        nocache = bool(self.nocacheVar.get())
        imgur = bool(self.imgurVar.get())
        self.thread = threading.Thread(target=flipper.generate,args=(inputStr, deckName))
        self.thread.start()
        self.disableInputs()
        self.updateProgressLabel('Generating....')
    
    def disableInputs(self):
        self.inputEntry.config(state='disabled')
        self.inputButton.config(state='disabled')
        self.deckNameEntry.config(state='disabled')
        self.generateButton.config(state='disabled')

        self.outputEntry.config(state='disabled')
        self.outputButton.config(state='disabled')
        self.hiresCheckbutton.config(state='disabled')
        self.reprintsCheckbutton.config(state='disabled')
        self.nocacheCheckbutton.config(state='disabled')
        self.imgurCheckbutton.config(state='disabled')

    def enableInputs(self):
        self.inputEntry.config(state='normal')
        self.inputButton.config(state='normal')
        self.deckNameEntry.config(state='normal')
        self.generateButton.config(state='normal')

        self.outputEntry.config(state='normal')
        self.outputButton.config(state='normal')
        self.hiresCheckbutton.config(state='normal')
        self.reprintsCheckbutton.config(state='normal')
        self.nocacheCheckbutton.config(state='normal')
        self.imgurCheckbutton.config(state='normal')

    def updateProgressLabel(self, message, fg='black'):
        self.progressLabel['text'] = message
        self.progressLabel['fg'] = fg


def main():
    flipper.initApp()
    root = tk.Tk()
    root.title('Tableflipper Extreme')
    app = FlipperGui(master=root)
    root.mainloop()

if __name__ == '__main__':
    sys.exit(main())
