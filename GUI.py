#This will temporarily receive input through the commandline instead of a GUI for testing
import PlaylistParsing, PlaylistCreation
link = input("Paste in your playlist link (CTRL + SHIFT + V) and press Enter: ")
newPlaylistTitle = input("Enter a title for the new child-appropriate playlist and press Enter: ")
newPlaylistDescrip = input("Enter a description for the new child-appropriate playlist or press Enter without typing anything if you do not want one: ")
PlaylistCreation.createSpotifyPlaylist(newPlaylistTitle,newPlaylistDescrip,PlaylistParsing.getAppropSpotifySongs(link)) 

