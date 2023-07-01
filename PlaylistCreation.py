import config
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import googleapiclient.discovery
import googleapiclient.errors
import time
from StrParsing import getYTPlaylistID, getSpotifyPlaylistID
from ytmusicapi import YTMusic
#Add option to input premade playlist link and add bool parameters for YT quota wait
def createSpotifyPlaylist(link:str,title:str,descrip:str,appropSongIDs:list[str],username:str):
	"""
	Creates or edits the child-appropriate Spotify playlists and adds the songs with the IDs indcated in appropSongIDs

	@param link : link to premade playlist that user inputted or empty string if no link is inputted
	@param title : title of the new playlist
	@param descrip : description for the new playlist
	@param appropSongIDs : list of string Spotify ids of the appropriate songs
	@param username : username of the Spotify user using this program
	@return : If the playlist contains at least one song, then a message telling the user to check their playlist is returned, otherwise a message indicating error or that there are no appropriate songs is returned.
	@return : None on success, otherwise the portion of appropSongIDs that still needs to be added
	@return : link to playlist if new one was created and error occurred, otherwise None
	"""

	#if the user inputted appropSongIDs from a previous failed run, then it will be converted into a list
	if type(appropSongIDs)==str:
		appropSongIDs = appropSongIDs.split(', ')
	#if there are any ids in appropSongIDs, then playlist creation will happen
	if(appropSongIDs):
			#need clientID and clientSecret from a Spotify account to get an access token required to access the API
			clientID, clientSecret = config.spotifyClientID,config.spotifyClientSecret
			token = SpotifyOAuth(client_id=clientID,client_secret=clientSecret,scope="playlist-modify-private",redirect_uri="https://localhost:8080/callback")
			spotifyObj = spotipy.Spotify(auth_manager=token)
			playlistData = dict()
			if not link:
				try:
					#public must be set to False for Spotify to allow editing of the playlist
					playlistData = spotifyObj.user_playlist_create(user=username,name=title,public=False,description=descrip)
				except Exception as e:
					return "Error: " + str(e), str(appropSongIDs)[1:len(str(appropSongIDs))-1], None
			if(len(appropSongIDs)<100):
					try:
						playlistID = None
						if not link:
							playlistID = getSpotifyPlaylistID(link)
							if playlistID==None:
								return "Error: Invalid link", str(appropSongIDs)[1:len(str(appropSongIDs))-1], None
						else:
							playlistID = playlistData['id']
						spotifyObj.user_playlist_add_tracks(user=username,playlist_id=playlistID,tracks=appropSongIDs)
					except Exception as e:
						if not link:
							return "Error: " + str(e), str(appropSongIDs)[1:len(str(appropSongIDs))-1], 'https://open.spotify.com/playlist/'+playlistData['id']
						else:
							return "Error: " + str(e), str(appropSongIDs)[1:len(str(appropSongIDs))-1], None
			else:
					for i in range(int(len(appropSongIDs)/100)):
						#refreshes access token if it has expired
						token_info = token.cache_handler.get_cached_token()
						#checks if token expired or is going to expire in a minute and refreshes if so
						if token.is_token_expired(token_info):
							token = SpotifyOAuth(client_id=config.spotifyClientID,client_secret=config.spotifyClientSecret,scope="playlist-read-private",redirect_uri="https://localhost:8080/callback",username=config.spotifyUserID)
							spotifyObj = spotipy.Spotify(auth_manager=token)
						try:
							spotifyObj.user_playlist_add_tracks(user=username,playlist_id=playlistData['id'],tracks=appropSongIDs[i*100:i*100+100])
						except Exception as e:
							if not link:
								return "Error: " + str(e), str(appropSongIDs[i*100:])[1:len(str(appropSongIDs[i*100:]))-1], 'https://open.spotify.com/playlist/'+playlistData['id']
							else:
								return "Error: " + str(e), str(appropSongIDs[i*100:])[1:len(str(appropSongIDs[i*100:]))-1], None
					if len(appropSongIDs)%100!=0:
						try:
							spotifyObj.user_playlist_add_tracks(user=username,playlist_id=playlistData['id'],tracks=appropSongIDs[int(len(appropSongIDs)/100)*100:])
						except Exception as e:
							if not link:
								return "Error: " + str(e), str(appropSongIDs[int(len(appropSongIDs)/100)*100:])[1:len(str(appropSongIDs[int(len(appropSongIDs)/100)*100:]))-1], 'https://open.spotify.com/playlist/'+playlistData['id']
							else:
								return "Error: " + str(e), str(appropSongIDs[int(len(appropSongIDs)/100)*100:])[1:len(str(appropSongIDs[int(len(appropSongIDs)/100)*100:]))-1], None
			return "Check your playlists", None, None
	else:
			return "There are no appropriate songs in the given playlist.", None, None

def createYTPlaylist(ytResource,appropSongIDs:list[str],link:str,title:str,descrip:str,status:str,timeOfFirstReq:float):
	"""
	Creates or edits a YouTube playlist and adds videos with the ids listed in appropSongIDs
	@param ytResource : YouTube object with the necessary credentials to read, create, and update a playlist
	@param appropSongIDs : list of ids of YouTube videos that have been determined to be appropriate
	@param link : link for premade playlist or empty string if not given a link
	@param title : title that the user wants the playlist to have
	@param descrip : description for the playlist that the user desires
	@param status : string indicating whether the playlist will be public or private
	@param timeOfFirstReq : float that indicates how much time has passed since the first request to YouTube Data API
	@return : str error message on error that is not because of the quota becoming empty or the rest of the ids to be added if the user does not want to wait an hour
	@return : the rest of the ids to be added or None if the user does not want to wait for the quota to refill or on success
	@return : link to playlist if new one was created and error occurred, otherwise None
	"""

	#if the user inputted appropSongIDs from a previous failed run, then it will be converted into a list
	if type(appropSongIDs)==str:
		appropSongIDs = appropSongIDs.split(', ')
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
							return "Error: " + str(e), str(appropSongIDs)[1:len(str(appropSongIDs))-1], None
					else:
						return str(appropSongIDs)[1:len(str(appropSongIDs))-1], None, None
				else:
					return "Error: " + str(error), str(appropSongIDs)[1:len(str(appropSongIDs))-1], None
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
							return "Error: " + str(e), str(appropSongIDs[numSongsAdded-1:])[1:len(str(appropSongIDs[numSongsAdded-1:]))-1],'https://www.youtube.com/playlist?list='+playlistID
					else:
						print("You can add an id to the end of 'https://youtube.com/watch?v=' to find the corresponding video.")
						#returns ids for videos left to add to the playlist starting at numSongsAdded-1 to avoid repeats
						return str(appropSongIDs[numSongsAdded-1:])[1:len(str(appropSongIDs[numSongsAdded-1:]))-1], None, 'https://www.youtube.com/playlist?list='+playlistID
				else:
					return "Error: " + str(e), str(appropSongIDs[numSongsAdded-1:])[1:len(str(appropSongIDs[numSongsAdded-1:]))-1], 'https://www.youtube.com/playlist?list='+playlistID
			except Exception as e:
				return "Error: " + str(e), str(appropSongIDs[numSongsAdded-1:])[1:len(str(appropSongIDs[numSongsAdded-1:]))-1], 'https://www.youtube.com/playlist?list='+playlistID
		return "Check your playlists.", None, None
	else:
		return "There are no appropriate songs in the given playlist.", None, None

def createYTMusicPlaylist(ytMusicResource:YTMusic,appropSongIDs:list[str],link:str,title:str,descrip:str,status:str):
	"""
	Creates or edits a YouTube music playlist and adds the songs with the ids listed in appropSongIDs to the playlist
	@param ytMusicResource : resource object that can request the creation and editing of playlists
	@param link : link to existing playlist that the user wants the songs added to
	@param descrip : description for the new playlist that the user wants add
	@param status : string with values "PUBLIC" or "PRIVATE" to indicate whether they want the new playlist to be public
	@return : str error message on error
	@return : the appropriate song ids that still need to be added
	"""
	if not link:
		try:
			ytMusicResource.create_playlist(title,descrip,status,appropSongIDs)
		except Exception as e:
			return "Error: " + str(e), str(appropSongIDs)[1:len(str(appropSongIDs))-1]
	else:
		try:
			#duplicates will be allowed as to not cause error and to speed up the program, but as long as the playlist does not have any songs added by the user (if a premade playlist is inputted), then there should not be any duplicates
			ytMusicResource.add_playlist_items(getYTPlaylistID(link),appropSongIDs,duplicates=True)
		except Exception as e:
			return "Error: " + str(e),str(appropSongIDs)[1:len(str(appropSongIDs))-1]