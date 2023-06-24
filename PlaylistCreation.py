import config
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import googleapiclient.discovery
import googleapiclient.errors
import time
from StrParsing import getYTPlaylistID
def createSpotifyPlaylist(title: str,descrip: str,appropSongIDs: list[str],username: str):
	"""
	This function creates the child-appropriate Spotify playlists and adds the songs with the IDs indcated in appropSongIDs.

	@param title : title of the new playlist
	@param descrip : description for the new playlist
	@param appropSongIDs : list of string Spotify ids of the appropriate songs
	@param username : username of the Spotify user using this program
	@return : If the playlist contains at least one song, then a message telling the user to check their playlist is returned, otherwise a message indicating that there are no appropriate songs is returned.
	"""

	if type(appropSongIDs)==str:
		return "Not a valid Spotify link"
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
#implement option to add to exisiting playlist
def createYTPlaylist(ytResource,appropSongIDs:list[str],link:str,title:str,descrip:str,status:str,timeOfFirstReq:float):
	"""
	This function creates a YouTube playlist and adds videos with the ids listed in appropSongIDs.
	@param ytResource : YouTube object with the necessary credentials to read, create, and update a playlist
	@param appropSongIDs : list of ids of YouTube videos that have been determined to be appropriate
	@param link : link for premade playlist or empty string if not given a link
	@param title : title that the user wants the playlist to have
	@param descrip : description for the playlist that the user desires
	@param status : string indicating whether the playlist will be public or private
	@param timeOfFirstReq : float that indicates how much time has passed since the first request to YouTube Data API
	"""
	if type(appropSongIDs)!=list:
		return 'Invalid link or input for appropSongIDs'
	if(appropSongIDs):
		#shown to user to help determine if they would like to wait for the quota to refill and the program
		numSongsAdded = 0
		playlistID = ''
		if(not link):
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
			#error handle for quota overload
			try:
				playlistCreateResponse = requestPlaylistCreate.execute()
				playlistID = playlistCreateResponse['id']
			except googleapiclient.errors.HttpError as error:
				if 'quota' in error._get_reason():
					print("Lyric analysis completed. Quota limit reached. Answer the following question:")
					waitAnswer = ''
					while waitAnswer!='yes' and waitAnswer!='no' and waitAnswer!='Yes' and waitAnswer!='No':
						waitAnswer=input("Are you okay with the program sleeping for an hour until it requests more data? Answer 'yes' or 'no' (*Note: If you answer no, you will be given the list of video ids for the songs that were deemed appropriate which you can copy and paste when asked to in the next run which must be in at least an hour from now.)")
					if waitAnswer=='yes' or waitAnswer=='Yes':
						print("Waiting for an hour.")
						time.sleep(3600.1-(time.time()-timeOfFirstReq))
						print("Done waiting.")
						try:
							playlistCreateResponse = requestPlaylistCreate.execute()
							playlistID = playlistCreateResponse['id']
						except Exception as e:
							print(e)
							exit(1)
					else:
						return appropSongIDs
				else:
					print(error)
					exit(1)
		else:
			playlistID=getYTPlaylistID(link)
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
			except googleapiclient.errors.HttpError as error:
				if 'quota' in error._get_reason():
					print("Quota limit reached while adding songs to the playlist. Answer the following question:")
					waitAnswer = ''
					while waitAnswer!='yes' and waitAnswer!='no' and waitAnswer!='Yes' and waitAnswer!='No':
						waitAnswer=input("Are you okay with the program sleeping for an hour until it can make more requests to add songs to the playlist? If you answer no, you will receive a list of links to songs that still needed to be added. You can decide to add them yourself or run the program an hour from now and copy and paste it when asked to.")
					if waitAnswer=='yes' or waitAnswer=='Yes':
						time.sleep(3600.1-(time.time()-timeOfFirstReq))
						try:
							requestPlaylistInsert.execute()
						except Exception as e:
							print(e)
							exit(1)
					else:
						#returns links to the videos left to add to the playlist starting at numSongsAdded-1 to avoid repeats
						return ['https://youtube.com/watch?v='+id for id in appropSongIDs[numSongsAdded-1:]]
				else:
					print(error)
					exit(1)
			except Exception as e:
				print(e)
				pass
	else:
		return "There are no appropriate songs in the given playlist."
		