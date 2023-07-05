import config
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from StrParsing import getYTPlaylistID, getSpotifyPlaylistID, getStrAppropSongIDs
from ytmusicapi import YTMusic
#trim off quote marks for each id
def createSpotifyPlaylist(link:str,title:str,descrip:str,appropSongIDs,username:str):
	"""
	Creates or edits the child-appropriate Spotify playlists and adds the songs with the IDs indcated in appropSongIDs

	@param link : link to premade playlist that user inputted or empty string if no link is inputted
	@param title : title of the new playlist
	@param descrip : description for the new playlist
	@param appropSongIDs : list or string of Spotify ids of the songs deemed appropriate by the program
	@param username : username of the Spotify user using this program
	@return : If the playlist contains at least one song, then a message telling the user to check their playlist is returned, otherwise a message indicating error or that there are no appropriate songs is returned.
	@return : None on success, otherwise the portion of appropSongIDs that still needs to be added
	@return : link to playlist if new one was created and error occurred, otherwise None
	"""

	#if the user inputted appropSongIDs from a previous failed run, then it will be converted into a list
	if type(appropSongIDs)==str:
		appropSongIDs = appropSongIDs.split(' ')
	#if there are any ids in appropSongIDs, then playlist creation will happen
	if(appropSongIDs):
			token = SpotifyOAuth(client_id=config.spotifyClientID,client_secret=config.spotifyClientSecret,scope="playlist-modify-private",redirect_uri="https://localhost:8080/callback")
			spotifyObj = spotipy.Spotify(auth_manager=token)
			playlistData = dict()
			playlistID = None
			if not link:
				try:
					#public must be set to False for Spotify to allow editing of the playlist
					playlistData = spotifyObj.user_playlist_create(user=username,name=title,public=False,description=descrip)
				except Exception as e:
					return "Error: " + str(e), getStrAppropSongIDs(appropSongIDs), None
				playlistID = playlistData['id']
			else:
				playlistID = getSpotifyPlaylistID(link)
				if playlistID==None:
					return "Error: Invalid premade playlist link", getStrAppropSongIDs(appropSongIDs), None	
			#only 100 songs can be added at a time
			if(len(appropSongIDs)<100):
				try:
					spotifyObj.user_playlist_add_tracks(user=username,playlist_id=playlistID,tracks=appropSongIDs)
				except Exception as e:
					if not link:
						return "Error: " + str(e), getStrAppropSongIDs(appropSongIDs), 'https://open.spotify.com/playlist/'+playlistData['id']
					else:
						return "Error: " + str(e), getStrAppropSongIDs(appropSongIDs), None
			else:
				for i in range(int(len(appropSongIDs)/100)):
					#refreshes access token if it has expired
					token_info = token.cache_handler.get_cached_token()
					#checks if token expired or is going to expire in a minute and refreshes if so
					if token.is_token_expired(token_info):
						token = SpotifyOAuth(client_id=config.spotifyClientID,client_secret=config.spotifyClientSecret,scope="playlist-read-private",redirect_uri="https://localhost:8080/callback",username=config.spotifyUserID)
						spotifyObj = spotipy.Spotify(auth_manager=token)
					try:
						spotifyObj.user_playlist_add_tracks(user=username,playlist_id=playlistID,tracks=appropSongIDs[i*100:i*100+100])
					except Exception as e:
						if not link:
							return "Error: " + str(e), getStrAppropSongIDs(appropSongIDs,i*100), 'https://open.spotify.com/playlist/'+playlistData['id']
						else:
							return "Error: " + str(e), getStrAppropSongIDs(appropSongIDs,i*100), None
				if len(appropSongIDs)%100!=0:
					try:
						spotifyObj.user_playlist_add_tracks(user=username,playlist_id=playlistID,tracks=appropSongIDs[int(len(appropSongIDs)/100)*100:])
					except Exception as e:
						if not link:
							return "Error: " + str(e), getStrAppropSongIDs(appropSongIDs,int(len(appropSongIDs)/100)*100), 'https://open.spotify.com/playlist/'+playlistData['id']
						else:
							return "Error: " + str(e), getStrAppropSongIDs(appropSongIDs,int(len(appropSongIDs)/100)*100), None
			return "Check your playlists", None, None
	else:
			return "There are no appropriate songs in the given playlist.", None, None

def createYTPlaylist(appropSongIDs,link:str,title:str,descrip:str,private:bool):
	"""
	Creates or edits a YouTube playlist and adds videos with the ids listed in appropSongIDs
	@param appropSongIDs : list or string of ids of YouTube videos that have been determined to be appropriate
	@param link : link for premade playlist or empty string if not given a link
	@param title : title that the user wants the playlist to have
	@param descrip : description for the playlist that the user desires
	@param private : boolean indicating whether the user wants the playlist to be private
	@return : str message that indicates that there are no appropriate songs or to check playlists on success, None if the user immediately wants the remaining appopriate song IDs or str error message on failure
	@return : the rest of the ids to be added or None on success
	@return : link to playlist if new one was created and error occurred, otherwise empty str
	"""

	flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
	config.googleClientSecretFileName, scopes=['https://www.googleapis.com/auth/youtube.readonly','https://www.googleapis.com/auth/youtube.force-ssl'])
	credentials = flow.run_local_server()
	ytResource = googleapiclient.discovery.build('youtube', 'v3', credentials=credentials)
	#if the user inputted appropSongIDs from a previous failed run, then it will be converted into a list
	if type(appropSongIDs)==str:
		appropSongIDs = appropSongIDs.split(' ')
	if(appropSongIDs):
		numSongsAdded = 0
		playlistID = ''
		if(not link):
			requestPlaylistCreate = ytResource.playlists().insert(
				part="snippet,status",
				body={
					"snippet": {
						"title": title,
						"description": descrip,
						"defaultLanguage": "en"
					},
					"status": {
						"privacyStatus": 'private' if private else 'public'
					}
				}
			)
			#error handle for quota overload
			try:
				playlistCreateResponse = requestPlaylistCreate.execute()
				playlistID = playlistCreateResponse['id']
			except Exception as e:
				return "Error: " + str(e), getStrAppropSongIDs(appropSongIDs), ''
		else:
			playlistID=getYTPlaylistID(link)
			if playlistID==None:
				return 'Error: Invalid premade playlist link', getStrAppropSongIDs(appropSongIDs), ''
		for id in appropSongIDs:
			requestPlaylistInsert = ytResource.playlistItems().insert(
			part="snippet",
			body={
				"snippet": {
					"playlistId": playlistID,
					"position": 0,
					"resourceId": {
						"kind": "youtube#video",
						"videoId": id
									}
							} 
					}
			)
			try:
				requestPlaylistInsert.execute()
				numSongsAdded+=1
			except Exception as e:
				return "Error: " + str(e), getStrAppropSongIDs(appropSongIDs,numSongsAdded-1), 'https://www.youtube.com/playlist?list='+playlistID
		return "Check your playlists.", None, ''
	else:
		return "There are no appropriate songs in the given playlist.", None, ''

def createYTMusicPlaylist(appropSongIDs,link:str,title:str,descrip:str,private:bool):
	"""
	Creates or edits a YouTube music playlist and adds the songs with the ids listed in appropSongIDs to the playlist
	@param appropSongIDs : list or string of ids of YouTube Music songs that were deemed appropriate
	@param link : link to existing playlist that the user wants the songs added to
	@param descrip : description for the new playlist that the user wants add
	@param status : bool indicating whether the user wants the new playlist to be private
	@return : 'Check your playlists' on success, str error message on error
	@return : None on success, the appropriate song ids that still need to be added on failure
	"""

	ytMusicResource = YTMusic('oauth.json')
	if type(appropSongIDs)==str:
		appropSongIDs = appropSongIDs.split(' ')
	if not link:
		try:
			ytMusicResource.create_playlist(title,descrip,'PRIVATE' if private else 'PUBLIC',appropSongIDs)
			return 'Check your playlists', None
		except Exception as e:
			return "Error: " + str(e), getStrAppropSongIDs(appropSongIDs)
	else:
		try:
			playlistID = getYTPlaylistID(link)
			if playlistID==None:
				return 'Error: Invalid premade playlist link', getStrAppropSongIDs(appropSongIDs)
			#duplicates will be allowed as to not cause error and to speed up the program, but as long as the playlist does not have any songs added by the user (if a premade playlist is inputted), then there should not be any duplicates
			ytMusicResource.add_playlist_items(getYTPlaylistID(link),appropSongIDs,duplicates=True)
			return 'Check your playlist', None
		except Exception as e:
			return "Error: " + str(e), getStrAppropSongIDs(appropSongIDs)