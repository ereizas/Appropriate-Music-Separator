import PlaylistParsing, PlaylistCreation, config
from tkinter import *
from tkinter import ttk

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
        #options for whether the user wants to wait an hour for the YT API quota to refill if it runs out at the steps in the names of the following three variables
        self.getYTPlaylistReqQuotaWait = BooleanVar()
        self.postYTLyricAnalysisQuotaWait = BooleanVar()
        self.addingYTVidsQuotaWait = BooleanVar()
        self.buildYTOptions(ytOptionsFrame,self.private,self.getYTPlaylistReqQuotaWait,self.postYTLyricAnalysisQuotaWait,self.addingYTVidsQuotaWait)
        
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
        #add "Separate Appropriate Music" button after YT options if possible
    
    def buildYTOptions(self,master,private,getYTPlaylistReqQuotaWait,postYTLyricAnalysisQuotaWait,addingYTVidsQuotaWait):
        """
        Builds YT specific checkbox options
        """

        self.privateCheckbutton = ttk.Checkbutton(master,text='Check this if you want the playlist to be private (YouTube and YouTube Music only)',variable=private)
        self.privateCheckbutton.grid(row=0,column=0)
        ttk.Label(master,text='The following options are for YouTube (not YouTube Music) playlists only (read the paragraph before the steps in the YouTube setup section of the README.md file for a review of the quota limit and cost):').grid(row=1,column=0)
        self.playlistReqQuotaWaitCheckbutton = ttk.Checkbutton(master,text='Check this if you are okay with waiting an hour for the request quota to refill after it has ran out while requesting information from the original playlist (recommended for large playlists of about a few hundred songs)',variable=getYTPlaylistReqQuotaWait)
        self.playlistReqQuotaWaitCheckbutton.grid(row=2,column=0,pady=3)
        self.lyricAnalysisQuotaWaitCheckbutton = ttk.Checkbutton(master,text='Check this if you are okay with waiting an hour for quota to refill if it ran out after analyzing the lyrics of all the songs. *If unchecked, the program will return a list of ids that you can input to speed up the next run (which will still have to be in an hour).',variable=postYTLyricAnalysisQuotaWait)
        self.lyricAnalysisQuotaWaitCheckbutton.grid(row=3,column=0,pady=3)
        self.ytVidsQuotaWaitCheckbutton = ttk.Checkbutton(master,text='Check this if you are okay with waiting an hour for quota refill after it ran out from adding videos to the new playlist. *If unchecked, the program will return a list of the rest of the ids that need to be added.',variable=addingYTVidsQuotaWait)
        self.ytVidsQuotaWaitCheckbutton.grid(row=4,column=0,pady=3)
    
    def separatePlaylist(self):
        #clears the output text box
        if self.outputTextBox.get('1.0',END):
            self.outputTextBox.delete('1.0',END)
        self.outputTextBox.insert(END,"Processing playlist, make sure to check the command line/terminal (For Windows: PowerShell) that you ran this on for any updates.\n")
        streamingService = self.streamingServiceDropDown.get()
        if streamingService=='Spotify':
            spotifyGetRet = PlaylistParsing.getAppropSpotifySongs(self.linkEntry.get())
            if type(spotifyGetRet)==str:
                self.outputTextBox.insert(END,str(spotifyGetRet)+'\n')
            else:
                message, strAppropSongIDs, newLink = PlaylistCreation.createSpotifyPlaylist(self.premadePlaylistLinkEntry.get(),self.titleEntry.get(),self.descripEntry.get(),spotifyGetRet,config.spotifyUserID)
                if 'Error:' in message:
                    outputTBMessage = message + " Appropriate Song IDs: " + strAppropSongIDs
                    if newLink:
                        outputTBMessage+=newLink
                    self.outputTextBox.insert(END,outputTBMessage)
                else:
                    self.outputTextBox.insert(END,message)
        elif streamingService=='YouTube Music':
            pass
        elif streamingService=='YouTube':
            pass
        else:
            self.outputTextBox.insert(END,'The streaming service entered is either not available or not valid.')
    
    def buildEndFrame(self,master):
        self.separateButton = ttk.Button(master,text='Separate Appropriate Music',command=self.separatePlaylist)
        self.separateButton.grid(row=0,column=0)   
        ttk.Label(master,text='Output:').grid(row=1,column=0)
        self.outputTextBox = Text(master,width=150,height=15)
        self.outputTextBox.grid(row=2,column=0)

if __name__=='__main__':
    root = Tk()
    app = GUI(root)
    root.mainloop()
    exit(0)