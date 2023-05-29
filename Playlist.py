import requests, config, MusicSources
import json
import spotipy
from spotipy.oauth2 import SpotifyOAuth
def createSpotifyPlaylist(title,descrip):
    #need clientID and clientSecret from a Spotify account to get an access token required to access the API
    clientID, clientSecret = config.spotifyClientID,config.spotifyClientSecret
    token = SpotifyOAuth(client_id=clientID,client_secret=clientSecret,scope="playlist-modify-private",redirect_uri="https://localhost:8080/callback")
    spotifyObj = spotipy.Spotify(auth_manager=token)
    spotifyObj.user_playlist_create(user=config.userID,name=title,public=False,description=descrip)
