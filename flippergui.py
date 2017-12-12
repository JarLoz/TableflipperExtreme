import tkinter as tk
from tkinter import filedialog
import sys
import os
import flipper
import threading
from queue import Queue
from deckconverter import queue
from PIL import ImageTk, Image
import json

class FlipperGui(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master, padx=12, pady=3)

        if getattr(sys, 'frozen', False) :
            self.baseDir = os.path.dirname(sys.executable)
        else:
            self.baseDir = os.path.dirname(os.path.realpath(__file__))

        self.loadConfig()

        self.master = master
        self.queue = queue.initQueue()

        self.grid()
        self.logoImage = ImageTk.PhotoImage(Image.open('logo.png'))

        self.logoLabel = tk.Label(self, image=self.logoImage)
        self.logoLabel.grid(row=0, column=0, columnspan=5)

        self.deckNameLabel = tk.Label(self, text='Deckname')
        self.deckNameLabel.grid(row=1, column=0, sticky=tk.W)

        self.deckNameEntry = tk.Entry(self, width=60)
        self.deckNameEntry.grid(row=1, column=1, columnspan=3, stick=tk.W)
        self.deckNameEntry.insert(0,'Deck')

        self.inputLabel = tk.Label(self, text='File or URL')
        self.inputLabel.grid(row=2, column=0, sticky=tk.W)

        self.inputEntry = tk.Entry(self, width=60)
        self.inputEntry.grid(row=2, column=1, columnspan=3, sticky=tk.W)

        self.inputButton = tk.Button(self, text='Browse', command=self.openFile)
        self.inputButton.grid(row=2, column=4, sticky=tk.E)

        self.outputLabel = tk.Label(self, text='Output folder (optional)')
        self.outputLabel.grid(row=3, column=0, sticky=tk.W)

        self.outputEntry = tk.Entry(self, width=60)
        self.outputEntry.grid(row=3, column=1, columnspan=3, sticky=tk.W)
        self.outputEntry.insert(0,self.config['outputFolder'])

        self.outputButton = tk.Button(self, text='Browse', command=self.openFolder)
        self.outputButton.grid(row=3, column=4, sticky=tk.E)

        self.imgurLabel = tk.Label(self, text='ImgurID (optional)')
        self.imgurLabel.grid(row=4, column=0, sticky=tk.W)

        self.imgurEntry = tk.Entry(self, width=60)
        self.imgurEntry.grid(row=4, column=1, columnspan=3, sticky=tk.W)
        if self.config['imgurId']:
            self.imgurEntry.insert(0,self.config['imgurId'])
        self.imgurEntry.config(state='disabled')

        self.dropboxLabel = tk.Label(self, text='Dropbox Token(optional)')
        self.dropboxLabel.grid(row=5, column=0, sticky=tk.W)

        self.dropboxEntry = tk.Entry(self, width=60)
        self.dropboxEntry.grid(row=5, column=1, columnspan=3, sticky=tk.W)
        if self.config['dropboxToken']:
            self.dropboxEntry.insert(0,self.config['dropboxToken'])
        self.dropboxEntry.config(state='disabled')

        self.basicsLabel = tk.Label(self, text='Basic lands')
        self.basicsLabel.grid(row=6, column=0, sticky=tk.W)

        basicsOptions = ('guru','unstable','alpha','core')
        self.basicsVar = tk.StringVar()
        self.basicsVar.set(self.config['basicSet'])
        self.basicsMenu = tk.OptionMenu(self, self.basicsVar, *basicsOptions)
        self.basicsMenu.grid(row=6, column=1, columnspan=2, sticky=tk.W)

        self.hiresVar = tk.IntVar()
        self.hiresVar.set(int(self.config['hires']))
        self.hiresCheckbutton = tk.Checkbutton(self, text='High Resolution', variable=self.hiresVar)
        self.hiresCheckbutton.grid(row=7, column=0, sticky=tk.W)

        self.reprintsVar = tk.IntVar()
        self.reprintsVar.set(int(self.config['reprints']))
        self.reprintsCheckbutton = tk.Checkbutton(self, text='Reprints', variable=self.reprintsVar)
        self.reprintsCheckbutton.grid(row=7, column=1, sticky=tk.W)

        self.nocacheVar = tk.IntVar()
        self.nocacheVar.set(int(self.config['nocache']))
        self.nocacheCheckbutton = tk.Checkbutton(self, text='No cache', variable=self.nocacheVar)
        self.nocacheCheckbutton.grid(row=7, column=2, sticky=tk.W)

        self.imgurVar = tk.IntVar()
        self.imgurCheckbutton = tk.Checkbutton(self, text='Imgur Upload', variable=self.imgurVar)
        self.imgurCheckbutton.grid(row=7, column=3, sticky=tk.W)
        self.imgurVar.trace('w', self.imgurVarCallback)

        self.dropboxVar = tk.IntVar()
        self.dropboxCheckbutton = tk.Checkbutton(self, text='Dropbox Upload', variable=self.dropboxVar)
        self.dropboxCheckbutton.grid(row=7, column=4, sticky=tk.W)
        self.dropboxVar.trace('w', self.dropboxVarCallback)

        self.progressLabel = tk.Label(self, text='Ready')
        self.progressLabel.grid(row=8, column=0, columnspan=4, sticky=tk.W)

        self.generateButton = tk.Button(self, text='Generate', command=self.generate)
        self.generateButton.grid(row=8, column=4, sticky=tk.E)

        self.processQueue()

    def processQueue(self):
        while self.queue.qsize():
            msg = self.queue.get(0)
            if msg['type'] == 'done':
                self.saveConfig()
                self.enableInputs()
                self.updateProgressLabel('All done!')
            elif msg['type'] == 'error':
                self.enableInputs()
                self.updateProgressLabel(msg['text'], fg='red')
            elif msg['type'] == 'message':
                self.updateProgressLabel(msg['text'])
        self.master.after(100, self.processQueue)

    def openFile(self):
        filename = filedialog.askopenfilename(initialdir=self.baseDir,parent=self,title='Decklist')
        self.inputEntry.delete(0, tk.END)
        self.inputEntry.insert(0, filename)

    def openFolder(self):
        dirname = filedialog.askdirectory(initialdir=self.baseDir,parent=self,title='Output directory')
        self.outputEntry.delete(0, tk.END)
        self.outputEntry.insert(0, dirname)

    def generate(self):
        inputStr = self.inputEntry.get()
        deckName = self.deckNameEntry.get()
        outputFolder = self.outputEntry.get()
        if len(inputStr) == 0:
            self.updateProgressLabel('Must give filename or URL', fg='red')
            return
        if len(deckName) == 0:
            self.updateProgressLabel('Must give a deckname', fg='red')
            return
        if len(outputFolder) and not os.path.isdir(outputFolder):
            self.updateProgressLabel('Output folder must exist', fg='red')
            return
        if self.imgurVar.get():
            imgurId = self.imgurEntry.get()
            if len(imgurId) == 0:
                self.updateProgressLabel('Must have ImgurID', fg='red')
                return
        else:
            imgurId = None
        if self.dropboxVar.get():
            dropboxToken = self.dropboxEntry.get()
            if len(dropboxToken) == 0:
                self.updateProgressLabel('Must have Dropbox Token', fg='red')
                return
        else:
            dropboxToken = None
        hires = bool(self.hiresVar.get())
        reprints = bool(self.reprintsVar.get())
        nocache = bool(self.nocacheVar.get())
        basicSet = self.basicsVar.get()
        self.config['imgurId'] = imgurId
        self.config['dropboxToken'] = dropboxToken
        self.config['outputFolder'] = outputFolder
        self.config['hires'] = hires
        self.config['reprints'] = reprints
        self.config['nocache'] = nocache
        self.config['basicSet'] = basicSet
        self.thread = threading.Thread(target=flipper.generate,args=(inputStr, deckName, hires, reprints, nocache, imgurId, dropboxToken, outputFolder, basicSet))
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
        self.imgurEntry.config(state='disabled')
        self.dropboxCheckbutton.config(state='disabled')
        self.dropboxEntry.config(state='disabled')

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
        self.dropboxCheckbutton.config(state='normal')

        self.updateImgurEntry()
        self.updateDropboxEntry()

    def imgurVarCallback(self, name, index, mode):
        self.updateImgurEntry()

    def updateImgurEntry(self):
        imgur = bool(self.imgurVar.get())
        if imgur:
            self.imgurEntry.config(state='normal')
        else:
            self.imgurEntry.config(state='disabled')

    def dropboxVarCallback(self, name, index, mode):
        self.updateDropboxEntry()

    def updateDropboxEntry(self):
        dropbox = bool(self.dropboxVar.get())
        if dropbox:
            self.dropboxEntry.config(state='normal')
        else:
            self.dropboxEntry.config(state='disabled')

    def updateProgressLabel(self, message, fg='black'):
        self.progressLabel['text'] = message
        self.progressLabel['fg'] = fg

    def loadConfig(self):
        if os.path.isfile('config.json'):
            # We have some kind of saved config, let's use it.
            with open('config.json', 'r',encoding='utf8') as infile:
                self.config = json.load(infile)
        else:
            # Use defaults.
            self.config = {
                    'imgurId':None,
                    'dropboxToken':None,
                    'outputFolder':'',
                    'hires' : False,
                    'reprints' : False,
                    'nocache' : False,
                    'basicSet' : 'guru'
                    }

    def saveConfig(self):
        with open('config.json', 'w', encoding='utf8') as outfile:
            json.dump(self.config, outfile)

def main():
    flipper.initApp()
    root = tk.Tk()
    root.title('Tableflipper Extreme')
    app = FlipperGui(master=root)
    root.mainloop()

if __name__ == '__main__':
    sys.exit(main())
