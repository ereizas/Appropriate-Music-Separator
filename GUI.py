#This will temporarily receive input through the commandline instead of a GUI for testing
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
        self.prevRunAppropYTIDs = StringVar()
        self.originalLink = StringVar()
        self.newLink = StringVar()
        self.playlistTitle = StringVar()
        self.descrip = StringVar()
        self.buildGeneralGUI(generalFrame,self.prevRunAppropYTIDs,self.originalLink,self.newLink,self.playlistTitle,self.descrip)

        ytOptionsFrame = ttk.Frame(self.__root)
        ytOptionsFrame.pack(padx=5,pady=5)
        #need to decide upper or lower case based on whether YT or YT Music is selected
        self.private = BooleanVar()
        #options for whether the user wants to wait an hour for the YT API quota to refill if it runs out at the steps in the names of the following three variables
        self.getYTPlaylistReqQuotaWait = BooleanVar()
        self.postYTLyricAnalysisQuotaWait = BooleanVar()
        self.addingYTVidsQuotaWait = BooleanVar()
        self.buildYTOptions(ytOptionsFrame,self.private,self.getYTPlaylistReqQuotaWait,self.postYTLyricAnalysisQuotaWait,self.addingYTVidsQuotaWait)
        
        self.separateButton = ttk.Button(ytOptionsFrame,text='Separate Appropriate Music')
        self.separateButton.grid(row=19,column=0)

    def buildGeneralGUI(self,master,prevRunAppropYTIDs,originalLink,newLink,playlistTitle,descrip):
        ttk.Label(master,text='If you have it, paste the list of YouTube IDs from a previous run:').grid(row=0,column=0)
        self.prevRunAppropYTIDsEntry = ttk.Label(master,width=100,textvariable=prevRunAppropYTIDs)
        self.prevRunAppropYTIDsEntry.grid(row=1,column=0)
        ttk.Label(master,text='Enter or paste in the link of the playlist you want the program to analyze:').grid(row=2,column=0)
        self.linkEntry = ttk.Entry(master,width=50,textvariable=originalLink)
        self.linkEntry.grid(row=3,column=0)
        #for spacing
        ttk.Frame(master).grid(row=4,column=0,pady=5)
        ttk.Label(master,text='Select the streaming service of the playlist:').grid(row=5,column=0)
        streamingServiceDropDown = ttk.Combobox(master,values=['Spotify','YouTube Music','YouTube'])
        streamingServiceDropDown.grid(row=6,column=0)
        ttk.Label(master,text='Enter the link for the playlist you want the appropriate songs to be added to (recommended for YouTube, not as important for YouTube music) or skip to the next entry to create a new one:').grid(row=7,column=0)
        self.newPlaylistLinkEntry = ttk.Entry(master,width=50,textvariable=newLink)
        self.newPlaylistLinkEntry.grid(row=8,column=0)
        ttk.Label(master,text='Enter a title for the new playlist:').grid(row=9,column=0)
        self.TitleEntry = ttk.Entry(master,width=40,textvariable=playlistTitle)
        self.TitleEntry.grid(row=10,column=0)
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

if __name__=='__main__':
    root = Tk()
    app = GUI(root)
    root.mainloop()
    exit(0)