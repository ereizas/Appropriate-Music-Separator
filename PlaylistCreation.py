import config
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import PlaylistParsing
def createSpotifyPlaylist(title: str,descrip: str,appropSongIDs: list[str],username: str):
    """
    This function creates the child-appropriate Spotify playlists and adds the songs with the IDs indcated in appropSongIDs.

    @param title : title of the new playlist
    @param descrip : description for the new playlist
    @param appropSongIDs : list of string Spotify ids of the appropriate songs
    @param username : username of the Spotify user using this program
    @return : If the playlist contains at least one song, then a message telling the user to check their playlist is returned, otherwise a message indicating that there are no appropriate songs is returned.
    """
    if(appropSongIDs):
        #need clientID and clientSecret from a Spotify account to get an access token required to access the API
        clientID, clientSecret = config.spotifyClientID,config.spotifyClientSecret
        token = SpotifyOAuth(client_id=clientID,client_secret=clientSecret,scope="playlist-modify-private",redirect_uri="https://localhost:8080/callback")
        spotifyObj = spotipy.Spotify(auth_manager=token)
        playlistData = spotifyObj.user_playlist_create(user=username,name=title,public=False,description=descrip)
        #if there are songs that are deemed appropriate, then the playlist will be created
        if(len(appropSongIDs)<100):
            spotifyObj.user_playlist_add_tracks(user=username,playlist_id=playlistData['id'],tracks=appropSongIDs)
        else:
            for i in range(int(len(appropSongIDs)/100)):
                spotifyObj.user_playlist_add_tracks(user=username,playlist_id=playlistData['id'],tracks=appropSongIDs[i*100:i*100+100-1])
        return "Check your playlists"
    else:
        return "There are no appropriate songs in the given playlist"