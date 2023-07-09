import playlist_parsing, playlist_creation, config
from tkinter import *
from tkinter import ttk
import sys, threading

class GUI():
    def __init__(self,root):
        #bool for whether GUI is running
        self.running = True
        self.__root = root
        self.__root.title('Appropriate Song Separator')
        title_label = ttk.Label(self.__root, text = 'Appropriate Song Separator', font='Daytona 35 bold', justify=CENTER)
        title_label.pack(padx=5,pady=5)

        self.__style = ttk.Style()
        self.__style.configure('TButton', font = ('Daytona',12,'bold'))
        self.__style.configure('Header.TLabel', font = ('Daytona',18,'bold'))
        
        generalFrame=ttk.Frame(self.__root)
        generalFrame.pack(padx=5,pady=5)
        #need to decide upper or lower case based on whether YT or YT Music is selected
        self.private = BooleanVar()
        self.buildGeneralGUI(generalFrame,self.private)
        endFrame = ttk.Frame(self.__root)
        endFrame.pack(padx=5,pady=5)
        self.buildEndFrame(endFrame)

    def buildGeneralGUI(self,master,private):
        """
        Builds the part of the GUI that applies for all types of playlists
        @param master : root application
        @private : bool indicating whether the user wants the playlist to be private
        """
        ttk.Label(master,text='If you have it, paste the list of appropriate song IDs from a previous run:').grid(row=0,column=0)
        self.prevRunAppropIDsEntry = ttk.Entry(master,width=100)
        self.prevRunAppropIDsEntry.grid(row=1,column=0)
        ttk.Label(master,text='Enter or paste in the link of the playlist you want the program to analyze:').grid(row=2,column=0)
        self.linkEntry = ttk.Entry(master,width=100)
        self.linkEntry.grid(row=3,column=0)
        #for spacing
        ttk.Frame(master).grid(row=4,column=0,pady=5)
        ttk.Label(master,text='Select the streaming service of the playlist:').grid(row=5,column=0)
        self.streamingServiceDropDown = ttk.Combobox(master,values=['Spotify','YouTube Music','YouTube'])
        self.streamingServiceDropDown.grid(row=6,column=0)
        ttk.Label(master,text='Enter the link for a premade playlist(optional, but highly recommended for YouTube, and for Spotify the playlist MUST be private) or skip to the next entry to create a new one:').grid(row=7,column=0)
        self.premadePlaylistLinkEntry = ttk.Entry(master,width=100)
        self.premadePlaylistLinkEntry.grid(row=8,column=0)
        ttk.Label(master,text='Enter a title for the new playlist:').grid(row=9,column=0)
        self.titleEntry = ttk.Entry(master,width=40)
        self.titleEntry.grid(row=10,column=0)
        ttk.Label(master,text="Enter a description for the new playlist (optional):").grid(row=11,column=0)
        self.descripEntry = ttk.Entry(master,width=50)
        self.descripEntry.grid(row=12,column=0)
        self.privateCheckbutton = ttk.Checkbutton(master,text='Check this if you want the playlist to be private (YouTube and YouTube Music only)',variable=private)
        self.privateCheckbutton.grid(row=13,column=0)
        
    def separatePlaylist(self):
        """
        Integrates the backend with the front end by collecting and parsing user input and calling the appropriate functions from playlist_parsing and playlist_creation
        """
        self.outputTextBox.insert(END,"Processing playlist, make sure to check the command line/terminal (For Windows: PowerShell) that you ran this on for any updates.\n\n")
        streamingService = self.streamingServiceDropDown.get()
        prevRunAppropIDs = self.prevRunAppropIDsEntry.get()
        if streamingService=='Spotify':
            #this variable like the other ones at the top of the following conditionals concerning streaming services won't be used as parameters if 'not prevRunAppropIDs' is False
            spotifyGetRet=None
            if not prevRunAppropIDs:
                spotifyGetRet = playlist_parsing.getAppropSpotifySongs(self.linkEntry.get())
                if type(spotifyGetRet)==str:
                    self.outputTextBox.insert(END,str(spotifyGetRet)+'\n\n')
            if type(spotifyGetRet)!=str:
                message, strAppropSongIDs, newLink = playlist_creation.createSpotifyPlaylist(self.premadePlaylistLinkEntry.get(),self.titleEntry.get(),self.descripEntry.get(),spotifyGetRet if not prevRunAppropIDs else prevRunAppropIDs,config.spotifyUserID)
                if 'Error:' in message:
                    outputTBMessage = message + " Appropriate Song IDs: " + strAppropSongIDs
                    if newLink:
                        outputTBMessage+=newLink
                    self.outputTextBox.insert(END,outputTBMessage+'\n\n')
                else:
                    self.outputTextBox.insert(END,message + '\n\n')
        elif streamingService=='YouTube Music':
            ytMusicGetRet = 0
            if not prevRunAppropIDs:
                ytMusicGetRet = playlist_parsing.getAppropYTMusicSongs(self.linkEntry.get())
                if type(ytMusicGetRet)==str:
                    self.outputTextBox.insert(END,ytMusicGetRet+'\n\n')
            if type(ytMusicGetRet)!=str:
                message, remainingAppropSongIDs = playlist_creation.createYTMusicPlaylist(ytMusicGetRet if not prevRunAppropIDs else prevRunAppropIDs,self.premadePlaylistLinkEntry.get(),self.titleEntry.get(),self.descripEntry.get(),self.private.get())
                if remainingAppropSongIDs != None:
                    self.outputTextBox.insert(END,message + '\n\nRemaining Appropriate Song IDs: ' + remainingAppropSongIDs + '\n\n')
                else:
                    self.outputTextBox.insert(END,message+'\n\n')
        elif streamingService=='YouTube':
            ytGetRet = []
            if not prevRunAppropIDs:
                ytGetRet= playlist_parsing.getAppropYTSongs(self.linkEntry.get())
                if type(ytGetRet)==str:
                    self.outputTextBox.insert(END, ytGetRet+'\n\n')
            if type(ytGetRet)!=str:
                message, remainingAppropSongIDs, link = playlist_creation.createYTPlaylist(ytGetRet if not prevRunAppropIDs else prevRunAppropIDs,self.premadePlaylistLinkEntry.get(),self.titleEntry.get(),self.descripEntry.get(),self.private.get())
                if type(message)==str and type(remainingAppropSongIDs)==str:
                    self.outputTextBox.insert(END,message+'\n\nRemaining Appropriate Song IDs: '+remainingAppropSongIDs+'\n\n'+link+'\n\n')
                elif remainingAppropSongIDs==None:
                    self.outputTextBox.insert(END,message+'\n\n')
                else:
                    self.outputTextBox.insert(END,'Remaining Appropriate Song IDs: '+remainingAppropSongIDs+'\n\n')
        else:
            self.outputTextBox.insert(END,'The streaming service entered is either not available or not valid.\n\n')
        print('Done.')

    def runSongSeparatorThread(self):
        """
        Enables the GUI to run as one thread and the backend to run as another
        """

        threading.Thread(target=self.separatePlaylist).start()

    
    def buildEndFrame(self,master):
        """
        Builds the last two parts of the GUI
        """

        self.separateButton = ttk.Button(master,text='Separate Appropriate Music',command=self.runSongSeparatorThread)
        self.separateButton.grid(row=0,column=0)   
        ttk.Label(master,text='Output:').grid(row=1,column=0)
        self.outputTextBox = Text(master,width=150,height=15)
        self.outputTextBox.grid(row=2,column=0)
        sys.stdout = TextRedirector(self.outputTextBox,'stdout')

class TextRedirector(object):
    """
    Sets up object that sys.stdout is assigned as so that printed errors are redirected to a tkinter widget's text field
    Credit to Bryan Oakley on https://stackoverflow.com/questions/12351786/how-to-redirect-print-statements-to-tkinter-text-widget
    """
    def __init__(self,widget:Text,tag='stdout'):
        self.widget=widget
        self.tag = tag

    def write(self,text):
        self.widget.configure(state='normal')
        self.widget.insert('end',text,(self.tag,))
    #created to avoid the exception that appears when there is no flush method
    def flush(self):
        pass

if __name__=='__main__':
    root = Tk()
    app = GUI(root)
    root.mainloop()
    exit(0)
