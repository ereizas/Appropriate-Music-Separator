#This will temporarily receive input through the commandline instead of a GUI for testing
import PlaylistParsing, PlaylistCreation, config
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

testYTMusicPart()