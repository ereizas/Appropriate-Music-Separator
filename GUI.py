#This will temporarily receive input through the commandline instead of a GUI for testing
import PlaylistParsing, PlaylistCreation, config
def testSpotifyPart():
    username = config.spotifyUserID
    link = input("Paste in your Spotify playlist link (CTRL + SHIFT + V) and press Enter: ")
    newPlaylistTitle = input("Enter a title for the new playlist and press Enter: ")
    newPlaylistDescrip = input("Enter a description for the new playlist or press Enter without typing anything if you do not want one: ")
    print(PlaylistCreation.createSpotifyPlaylist(newPlaylistTitle,newPlaylistDescrip,PlaylistParsing.getAppropSpotifySongs(link),username))
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

def testYTPart():
    link = input('Paste in your YouTube playlist link (CTRL + SHIFT + V) and press Enter: ')
    title = input('Enter a title for the new playlist and press Enter: ')
    ytResource,appropSongIds,timeOfFirstReq = PlaylistParsing.getAppropYTSongs(link,False)
    print(PlaylistCreation.createYTPlaylist(ytResource,appropSongIds,title,"",'private',False,timeOfFirstReq))
    """
    https://www.youtube.com/watch?v=CevxZvSJLk8&list=PLWLlkFICHOB5Amt6T7IPawzxX4WNNyH4N
    https://www.youtube.com/watch?v=OPf0YbXqDm0&list=PLMC9KNkIncKtPzgY-5rmhvj7fax8fdxoj
    """

testYTPart()