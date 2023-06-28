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
        
        uiFrame=ttk.Frame(self.__root)
        uiFrame.pack(padx=5,pady=5)
        self.link = StringVar()
        self.playlistTitle = StringVar()
        self.descrip = StringVar()
        #need to clarify if all lower case or upper case based on selection of YT or YT Music
        self.status = StringVar()
        #options for whether the user wants to wait an hour for the YT API quota to refill if it runs out at the steps in the names of the following three variables
        self.getYTPlaylistReqQuotaWait = BooleanVar()
        self.postYTLyricAnalysisQuotaWait = BooleanVar()
        self.addingYTVidsQuotaWait = BooleanVar()
        self.buildGUI(uiFrame,self.link)

    def buildGUI(self,master,link):
        ttk.Label(master,text='Enter or paste in the playlist link:').grid(row=0,column=0)
        self.linkEntry = ttk.Entry(master,width=50,textvariable=link,)
        self.linkEntry.grid(row=1,column=0)
        #for spacing
        ttk.Frame(master).grid(row=2,column=0,pady=5)
        ttk.Label(master,text='Select the streaming service of the playlist:').grid(row=3,column=0)
        streamingServiceDropDown = ttk.Combobox(master,values=['Spotify','YouTube Music','YouTube'])
        streamingServiceDropDown.grid(row=4,column=0)

#Add link validation here!
def testSpotifyPart():
    link = input("Paste in your Spotify playlist link (CTRL + SHIFT + V) and press Enter: ")
    title = input("Enter a title for the new playlist and press Enter: ")
    descrip = input("Enter a description for the new playlist or press Enter without typing anything if you do not want one: ")
    print(PlaylistCreation.createSpotifyPlaylist(title,descrip,PlaylistParsing.getAppropSpotifySongs(link),config.spotifyUserID))
    #Make sure to uncomment functions you test in PlaylistParsing.py
    """
    https://open.spotify.com/playlist/3duJ5cNbfcCYEBQLEmRtIo
    https://open.spotify.com/playlist/3GJE68uV72wcsk7m6q99bL
    https://open.spotify.com/playlist/01L7OAAENPDVgttzcq5NN5
    https://open.spotify.com/playlist/1prjcMYoNiV4HLmO6PwlKo
    https://open.spotify.com/playlist/7M0hlHcvmKT4OtyfkriQHr
    https://open.spotify.com/playlist/1I5CX9jpaUFZxZ8kLMbBKo
    https://open.spotify.com/playlist/04UuVmB3pxFQgNziUgyj4j
    https://open.spotify.com/playlist/0BHAO3n0fsWjC6Z1mLJYsP
    https://open.spotify.com/playlist/0OaqORX9wCVcmBXvGO7JU3
    https://open.spotify.com/playlist/3Zc0vSZnaQK9eJvhnvnWpi
    """

#add option to provide playlist link and appropriate song ids (latter should come from a previous run) which would allow the program to skip certain steps
#advise users to create playlist on their own so that the program can request 2500 more songs from the original playlist or add one more song to the new playlist than if it had to make the playlist itself
def testYTPart():
    sourceLink = input('Paste in the YouTube playlist link that you want the program to look through (CTRL + SHIFT + V) and press Enter: ')
    #add link verification for destLink
    destLink = input('Paste a link to the playlist you want the songs added to if you created one or do not type anything and press Enter if you did not: ')
    title = ''
    descrip = ''
    publOrPriv = ''
    if not destLink:
        title = input('Enter a title for the new playlist and press Enter: ')
        descrip = input('Enter a description for the new playlist or press Enter without typing anything if you do not want one: ')
        publOrPriv = ''
        while publOrPriv!='public' and publOrPriv!='private':
            publOrPriv=input("Do you want your playlist to be public or private(Enter either \"public\" or \"private\")? Enter answer here: ")
    ytResource,appropSongIds,timeOfFirstReq = PlaylistParsing.getAppropYTSongs(sourceLink)
    print(PlaylistCreation.createYTPlaylist(ytResource,appropSongIds,destLink,title,descrip,publOrPriv,timeOfFirstReq))
    """
    https://www.youtube.com/watch?v=CevxZvSJLk8&list=PLWLlkFICHOB5Amt6T7IPawzxX4WNNyH4N
    https://www.youtube.com/watch?v=OPf0YbXqDm0&list=PLMC9KNkIncKtPzgY-5rmhvj7fax8fdxoj
    """

def testYTMusicPart():
    sourceLink = input('Paste in the YouTube Music playlist link that you want the program to look through (CTRL + SHIFT + V) and press Enter: ')
    #add link verification for destLink
    destLink = input('Paste a link to the playlist you want the songs added to if you created one or do not type anything and press Enter if you did not: ')
    title = ''
    descrip = ''
    publOrPriv = ''
    if not destLink:
        title = input('Enter a title for the new playlist and press Enter: ')
        descrip = input('Enter a description for the new playlist or press Enter without typing anything if you do not want one: ')
        publOrPriv = ''
        while publOrPriv!='PUBLIC' and publOrPriv!='PRIVATE':
            publOrPriv=input("Do you want your playlist to be public or private(Enter either \"PUBLIC\" or \"PRIVATE\")? Enter answer here: ")
    appropSongIDs, ytMusicResource = PlaylistParsing.getAppropYTMusicSongs(sourceLink)
    PlaylistCreation.createYTMusicPlaylist(ytMusicResource,appropSongIDs,destLink,title,descrip,publOrPriv)

if __name__=='__main__':
    root = Tk()
    app = GUI(root)
    root.mainloop()
    exit(0)