import PlaylistParsing, PlaylistCreation, config
from tkinter import *
from tkinter import ttk
import sys, threading
#add conditional for if appropSongIDs is inputted
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
        self.prevRunAppropIDs = StringVar()
        self.newLink = StringVar()
        self.playlistTitle = StringVar()
        self.descrip = StringVar()
        self.buildGeneralGUI(generalFrame,self.prevRunAppropIDs,self.newLink,self.playlistTitle,self.descrip)

        ytOptionsFrame = ttk.Frame(self.__root)
        ytOptionsFrame.pack(padx=5,pady=5)
        #need to decide upper or lower case based on whether YT or YT Music is selected
        self.private = BooleanVar()
        
        endFrame = ttk.Frame(self.__root)
        endFrame.pack(padx=5,pady=5)
        self.buildEndFrame(endFrame)

    def buildGeneralGUI(self,master,prevRunAppropIDs,newLink,playlistTitle,descrip):
        """
        Builds the part of the GUI that applies for all types of playlists
        """
        ttk.Label(master,text='If you have it, paste the list of appropriate song IDs from a previous run:').grid(row=0,column=0)
        self.prevRunAppropIDsEntry = ttk.Entry(master,width=100,textvariable=prevRunAppropIDs)
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
        self.premadePlaylistLinkEntry = ttk.Entry(master,width=100,textvariable=newLink)
        self.premadePlaylistLinkEntry.grid(row=8,column=0)
        ttk.Label(master,text='Enter a title for the new playlist:').grid(row=9,column=0)
        self.titleEntry = ttk.Entry(master,width=40,textvariable=playlistTitle)
        self.titleEntry.grid(row=10,column=0)
        ttk.Label(master,text="Enter a description for the new playlist (optional):").grid(row=11,column=0)
        self.descripEntry = ttk.Entry(master,width=50,textvariable=descrip)
        self.descripEntry.grid(row=12,column=0)
        self.privateCheckbutton = ttk.Checkbutton(master,text='Check this if you want the playlist to be private (YouTube and YouTube Music only)',variable=private)
        self.privateCheckbutton.grid(row=0,column=0)
        
    def separatePlaylist(self):
        self.outputTextBox.insert(END,"Processing playlist, make sure to check the command line/terminal (For Windows: PowerShell) that you ran this on for any updates.\n\n")
        streamingService = self.streamingServiceDropDown.get()
        if streamingService=='Spotify':
            spotifyGetRet = PlaylistParsing.getAppropSpotifySongs(self.linkEntry.get())
            if type(spotifyGetRet)==str:
                self.outputTextBox.insert(END,str(spotifyGetRet)+'\n\n')
            else:
                message, strAppropSongIDs, newLink = PlaylistCreation.createSpotifyPlaylist(self.premadePlaylistLinkEntry.get(),self.titleEntry.get(),self.descripEntry.get(),spotifyGetRet,config.spotifyUserID)
                if 'Error:' in message:
                    outputTBMessage = message + " Appropriate Song IDs: " + strAppropSongIDs
                    if newLink:
                        outputTBMessage+=newLink
                    self.outputTextBox.insert(END,outputTBMessage+'\n\n')
                else:
                    self.outputTextBox.insert(END,message + '\n\n')
        elif streamingService=='YouTube Music':
            ytMusicGetRet,ytMusicResource = PlaylistParsing.getAppropYTMusicSongs(self.linkEntry.get())
            if ytMusicResource==None:
                self.outputTextBox.insert(END,ytMusicGetRet+'\n\n')
            else:
                message, remainingAppropSongIDs = PlaylistCreation.createYTMusicPlaylist(ytMusicResource,ytMusicGetRet,self.premadePlaylistLinkEntry.get(),self.titleEntry.get(),self.descripEntry.get(),self.private.get())
                if remainingAppropSongIDs != None:
                    self.outputTextBox.insert(END,message + '\n\nRemaining Appropriate Song IDs: ' + remainingAppropSongIDs + '\n\n')
                else:
                    self.outputTextBox.insert(END,message+'\n\n')
        elif streamingService=='YouTube':
            ytGetRet, appropSongIDs, timeOfFirstReq = PlaylistParsing.getAppropYTSongs(self.linkEntry.get())
            if appropSongIDs==None:
                self.outputTextBox.insert(END, ytGetRet+'\n\n')
            else:
                message, remainingAppropSongIDs, link = PlaylistCreation.createYTPlaylist(ytGetRet,appropSongIDs,self.premadePlaylistLinkEntry.get(),self.titleEntry.get(),self.descripEntry.get(),self.private.get(),timeOfFirstReq)
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
        threading.Thread(target=self.separatePlaylist).start()

    
    def buildEndFrame(self,master):
        self.separateButton = ttk.Button(master,text='Separate Appropriate Music',command=self.runSongSeparatorThread)
        self.separateButton.grid(row=0,column=0)   
        ttk.Label(master,text='Output (Ignore any messages about subtitles and transcripts):').grid(row=1,column=0)
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