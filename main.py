from pytube import YouTube
from tkinter import filedialog
from tkinter import ttk
from tkinter import *
import re
import threading

class Application:
    def __init__(self, root: Tk):
        self.root = root
        self.root.grid_rowconfigure(0, weight=2)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.config(bg="#ffdddd")

        top_label = Label(self.root, text="Youtube Download Manager", fg="orange", font=("Type Xero", 70))
        top_label.grid(pady=(0, 10))

        link_label = Label(self.root, text="Please paste any youtube video link below", font=("Calibri", 30))
        link_label.grid(pady=(0, 20))

        self.youtubeEntryVar = StringVar()
        self.youtubeEntry = Entry(self.root, width=70, textvariable=self.youtubeEntryVar,
                                  font=("Agency FB", 25), fg="red")
        self.youtubeEntry.grid(pady=(0, 15), ipady=2)

        self.youtubeEntryError = Label(self.root, text="", font=("Calibri", 20))
        self.youtubeEntryError.grid(pady=(0, 8))

        self.youtubeFileSaveLabel = Label(self.root, text="Choose Directory", font=("calibri", 30))
        self.youtubeFileSaveLabel.grid()

        self.youtubeFileDirectoryButton = Button(self.root, text="Directory", font=("Calibri", 15), command=self.openDirectory)
        self.youtubeFileDirectoryButton.grid(pady=(10, 3))

        self.fileLocationLabel = Label(self.root, text="", font=("Calibri", 25))
        self.fileLocationLabel.grid()

        self.youtubeChooseLabel = Label(self.root, text="Choose the Download Type", font=("Calibri", 25))
        self.youtubeChooseLabel.grid()

        self.downloadChoices = [("Audio Mp3", 1), ("Video MP4", 2)]

        self.choicesVar = StringVar()
        self.choicesVar.set(1)

        for text, mode in self.downloadChoices:
            self.youtubeChoices = Radiobutton(self.root, text=text, font=("calibri", 15),
                                              variable=self.choicesVar, value=mode)
            self.youtubeChoices.grid()

        self.downloadButton = Button(self.root, text="Download", width=10, font=("Calibri", 15),
                                     command=self.checkyoutubeLink)
        self.downloadButton.grid(pady=(30, 5))

    def checkyoutubeLink(self):
        self.matchyoutubeLink = re.match("^https://www.youtube.com/.", self.youtubeEntryVar.get())

        if not self.matchyoutubeLink:
            self.youtubeEntryError.config(text="Invalid Youtube Link", fg="red")
        elif not self.openDirectory:
            self.fileLocationLabel.config(text="Please Choose a Directory", fg="red")
        elif self.matchyoutubeLink and self.openDirectory:
            self.downloadWindow()

    def downloadWindow(self):
        self.newWindow = Toplevel(self.root)
        self.root.withdraw()
        self.newWindow.state("zoomed")
        self.newWindow.grid_rowconfigure(0, weight=0)
        self.newWindow.grid_columnconfigure(0, weight=1)

        self.app = SecondApp(self.newWindow, self.youtubeEntryVar.get(), self.folderName, self.choicesVar.get())


    def openDirectory(self):
        self.folderName = filedialog.askdirectory()

        if len(self.folderName) > 0:
            self.fileLocationLabel.config(text=self.folderName, fg="green")
            return True
        else:
            self.fileLocationLabel.config(text="Please Choose a Directory", fg="red")


class SecondApp():
    def __init__(self, downloadWindow: Tk, youtubeLink, folderName, choices):
        self.downloadWindow = downloadWindow
        self.youtubeLink = youtubeLink
        self.folderName = folderName
        self.choices = choices

        self.yt = YouTube(self.youtubeLink)

        if choices == "1":
            self.video_type = self.yt.streams.filter(only_audio=True)
            self.maxFileSize = self.video_type.filesize
        if choices == "2":
            self.video_type = self.yt.streams.first()
            self.maxFileSize = self.video_type.filesize

        self.loadingLabel = Label(self.downloadWindow, text="Downloading in Progress....", font=("Calibri", 40))
        self.loadingLabel.grid(pady=(100, 0))

        self.loadingPercent = Label(self.downloadWindow, text="0", fg="green", font=("calibri", 40))
        self.loadingPercent.grid(pady=(50, 0))

        self.progressbar = ttk.Progressbar(self.downloadWindow, length=500, orient="horizontal", mode="indeterminate")
        self.progressbar.grid(pady=(50, 0))
        self.progressbar.start()

        threading.Thread(target=self.yt.register_on_progress_callback(self.show_progress)).start()
        threading.Thread(target=self.downloadFile).start()

    def downloadFile(self):
        if self.choices == "1":
            self.yt.streams.filter(only_audio=True).first().download(self.folderName)

        if self.choices == "2":
            self.yt.streams.first().download(self.folderName)

    def show_progress(self, streams=None, chunks=None, filehandle=None, bytes_remaining=None):
        if bytes_remaining is not None:
            self.percentCount = float("%0.2f" % (100 - (100 * (bytes_remaining / self.maxFileSize))))
        else:
            self.percentCount = 0

        if(self.percentCount < 100):
            self.loadingPercent.config(text=str(self.percentCount))
        else:
            self.progressbar.stop()
            self.loadingLabel.grid_forget()
            self.progressbar.grid_forget()

            self.downloadFinished = Label(self.downloadWindow, text="Download Finished", font=("Calibri", 30))
            self.downloadFinished.grid(pady=(150, 0))

            self.downloadFileName = Label(self.downloadWindow, text=self.yt.title, font=("calibri", 30))
            self.downloadFileName.grid(pady=(50, 0))

            MB = float("%0.2f" % (self.maxFileSize / 1000000))
            self.downloadFileSize = Label(self.downloadWindow, text=str(MB), font=("Calibri", 30))
            self.downloadFileSize.grid(pady=(50, 0))






if __name__ == "__main__":
    window = Tk()
    window.title("Youtube Download Manager")
    # make the window maximized
    window.state("zoomed")

    app = Application(window)

    mainloop()
