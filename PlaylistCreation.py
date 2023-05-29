import config
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import PlaylistParsing
def createSpotifyPlaylist(title,descrip,appropSongIDs):
    #need clientID and clientSecret from a Spotify account to get an access token required to access the API
    clientID, clientSecret = config.spotifyClientID,config.spotifyClientSecret
    token = SpotifyOAuth(client_id=clientID,client_secret=clientSecret,scope="playlist-modify-private",redirect_uri="https://localhost:8080/callback")
    spotifyObj = spotipy.Spotify(auth_manager=token)
    playlistData = spotifyObj.user_playlist_create(user=config.spotifyUserID,name=title,public=False,description=descrip)
    spotifyObj.user_playlist_add_tracks(user=config.spotifyUserID,playlist_id=playlistData['id'],tracks=appropSongIDs)

#createSpotifyPlaylist("My Playlist","hello",PlaylistParsing.getAppropSpotifySongs('https://open.spotify.com/playlist/3Zc0vSZnaQK9eJvhnvnWpi'))