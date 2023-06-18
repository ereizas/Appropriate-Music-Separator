import config
import spotipy
from spotipy.oauth2 import SpotifyOAuth
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
			print("Number of appropriate songs: " + str(len(appropSongIDs)))
			if(len(appropSongIDs)<100):
					spotifyObj.user_playlist_add_tracks(user=username,playlist_id=playlistData['id'],tracks=appropSongIDs)
			else:
					for i in range(int(len(appropSongIDs)/100)):
						#refreshes access token if it has expired
						token_info = token.cache_handler.get_cached_token()
						#checks if token expired or is going to expire in a minute and refreshes if so
						if token.is_token_expired(token_info):
							token = SpotifyOAuth(client_id=config.spotifyClientID,client_secret=config.spotifyClientSecret,scope="playlist-read-private",redirect_uri="https://localhost:8080/callback",username=config.spotifyUserID)
							spotifyObj = spotipy.Spotify(auth_manager=token)
						spotifyObj.user_playlist_add_tracks(user=username,playlist_id=playlistData['id'],tracks=appropSongIDs[i*100:i*100+100])
					if len(appropSongIDs)%100!=0:
						spotifyObj.user_playlist_add_tracks(user=username,playlist_id=playlistData['id'],tracks=appropSongIDs[int(len(appropSongIDs)/100)*100:])
			return "Check your playlists"
	else:
			return "There are no appropriate songs in the given playlist."
#implement option to wait for hour or print list of video ids
def createYTPlaylist(ytResource,appropSongIDs:list[str],title:str,descrip:str,status:str,waitForQuotaRefill:bool,timeOfFirstReq:float):
	"""
	This function creates a YouTube playlist and adds videos with the ids listed in appropSongIDs.
	@param ytResource : YouTube object with the necessary credentials to read, create, and update a playlist
	@param appropSongIDs : list of ids of YouTube videos that have been determined to be appropriate
	@param title : title that the user wants the playlist to have
	@param descrip : description for the playlist that the user desires
	@param status : string indicating whether the playlist will be public or private
	@param waitForQuotaRefill : boolean indicating whether the user would like to wait for a quota refill for the program to add more songs to the playlist
	@param timeOfFirstReq : float that indicates how much time has passed since the first request to YouTube Data API
	"""
	if(appropSongIDs):
		#error handle for quota overload, use timeOfFirstReq to determine how long to wait
		requestPlaylistCreate = ytResource.playlists().insert(
			part="snippet,status",
			body={
				"snippet": {
					"title": title,
					"description": descrip,
					"defaultLanguage": "en"
				},
				"status": {
					"privacyStatus": status
				}
			}
		)
		#shown to user to help determine if they would like to wait for the quota to refill and the program
		numSongsAdded = 0
		#error handle for quota overload
		playlistCreateResponse = requestPlaylistCreate.execute()
		for id in appropSongIDs:
			requestPlaylistInsert =  request = ytResource.playlistItems().insert(
			part="snippet",
			body={
				"snippet": {
					"playlistId": playlistCreateResponse['id'],
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
				print(e)
				pass
	else:
		return "There are no appropriate songs in the given playlist."
		