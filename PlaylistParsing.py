import LyricParsing, config, StrParsing
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import time
from ytmusicapi import YTMusic
#Test invalid links given
#add feature to check if all songs are appropriate, then don't create new playlist

def getAppropSpotifySongs(link:str)->list[str]:
	"""
	This function is meant to parse the Spotfiy playlist data to retrieve the Spotify ids for the appropriate songs and update and return an array with those ids.
	@param link : link to playlist
	@return appropSongIds : list with string Spotify ids of the appropriate songs in the playlist
	"""
	
	if 'spotify' not in link:
		return 'Not a valid Spotify link'
	playlistID, appropSongIds= '', []
	token = SpotifyOAuth(client_id=config.spotifyClientID,client_secret=config.spotifyClientSecret,scope="playlist-read-private",redirect_uri="https://localhost:8080/callback",username=config.spotifyUserID)
	spotifyObj = spotipy.Spotify(auth_manager=token)
	#extracts playlist id from the two types of spotify links
	if('?' in link):
		playlistID = link[link.index('playlist/')+9:link.index('?')]
	else:
		playlistID = link[link.index('playlist/')+9:]
	try: #start commit
		data = spotifyObj.playlist_tracks(playlistID,fields=any)
	except Exception as e:
		print(e)
		exit(1)
	#while there are more songs in the playlist to get data from
	while(data['next']):
		#refreshes access token if it has expired
		token_info = token.cache_handler.get_cached_token()
		#checks if token expired or is going to expire in a minute and refreshes if so
		if token.is_token_expired(token_info):
			token = SpotifyOAuth(client_id=config.spotifyClientID,client_secret=config.spotifyClientSecret,scope="playlist-read-private",redirect_uri="https://localhost:8080/callback",username=config.spotifyUserID)
			spotifyObj = spotipy.Spotify(auth_manager=token)
		#for other errors, retries three times
		if 'items' not in data:
			attempts = 0
			while 'items' not in data and attempts<3:
				try:
					data = spotifyObj.playlist_tracks(playlistID,fields=any)
				except Exception as e:
					print(e)
					exit(1)
				attempts+=1
				print(data)
		for item in data['items']:
			if not item['track']['explicit']:
				songTitle = item['track']['name']
				#conditional in list comprehension prevents featured artists mentioned in the song title from being repeated
				artists = [artist['name'] for artist in item['track']['artists'] if artist['name'] not in songTitle]
				#passing artists into an array enforces the perception of artists as being an array
				LyricParsing.findAndParseLyrics(artists,songTitle,appropSongIds,item['track']['id'],'')
		data = spotifyObj.next(data)
		
	return appropSongIds

#try to find lyrics first and then YT transcript as last resort
def getAppropYTSongs(link:str,waitForQuotaRefill:bool):
	"""
	This function parses the songs in a YouTube playlist and returns the ids of those songs that are appropriate for children.
	@param link : link to YouTube playlist
	@param waitForQuotaRefill : boolean indicating whether the user wants to wait for the quota to get refilled
	@return youtube : resource object with necessary credentials stored to read, create and update playlists
	@return appropSongIDs : list of YouTube ids for videos deemed appropriate for children by the program
	@return timeOfFirstReq : time in UTC for when the first request was made
	"""

	if 'youtube' not in link:
		return 'Not a valid YouTube link','',''
	#Must copy file name into first parameter
	flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
	config.googleClientSecretFileName, scopes=['https://www.googleapis.com/auth/youtube.readonly','https://www.googleapis.com/auth/youtube.force-ssl'])
	credentials = flow.run_local_server()
	youtube = googleapiclient.discovery.build('youtube', 'v3', credentials=credentials)
	appropSongIDs = []
	nextPageToken = ''
	timeOfFirstReq = 0
	response = 'nextPageToken'
	while 'nextPageToken' in response:
		request = youtube.playlistItems().list(
			part="snippet",
			maxResults=50,
			playlistId=StrParsing.getYTPlaylistID(link),
			pageToken = nextPageToken
		)
		if not timeOfFirstReq:
			timeOfFirstReq=time.time()
		try:
			response = request.execute()
		except googleapiclient.errors.HttpError as error:
			if 'quota' in error._get_reason():
				if waitForQuotaRefill:
					time.sleep(3600.1-(time.time()-timeOfFirstReq))
					try:
						response = request.execute()
					except Exception as e:
						print(e)
						exit(1)
			else:
				print(error)
				exit(1)
		for item in response['items']:
			artists = ''
			songTitle = item['snippet']['title']
			if ' - ' in songTitle:
				artists = songTitle[:songTitle.find(' - ')]
				#determines where to cut off the title of song based on the video title 
				specStrFirstOccurArr = [songTitle.find('feat.'),songTitle.find('ft.'),songTitle.find('('),songTitle.find('[')]
				hyphenInd = songTitle.find('-')
				endIndForSongTitleStr = len(songTitle)+1
				for potentialInd in specStrFirstOccurArr:
					if potentialInd > hyphenInd and potentialInd < endIndForSongTitleStr:
						endIndForSongTitleStr=potentialInd
				songTitle = songTitle[songTitle.find(' - ')+3:endIndForSongTitleStr-1]
			print(artists + ' - ' + songTitle)
			LyricParsing.findAndParseLyrics([artists],songTitle,appropSongIDs,item['snippet']['resourceId']['videoId'],youtube)
		if 'nextPageToken' in response:
			nextPageToken=response['nextPageToken']
	return youtube,appropSongIDs,timeOfFirstReq

#check if quota applies
def getAppropYTMusicSongs(link:str):
	if 'music.youtube' not in link:
		return 'Not a valid YouTube Music link'
	appropSongIDs = []
	ytmusic = YTMusic('oauth.json')
	try:
		data = ytmusic.get_playlist(StrParsing.getYTPlaylistID(link),limit=None)
	except Exception as e:
		print(e)
		exit(1)
	for track in data['tracks']:
		artists = [artist for artist in track['artists']]
		songTitle = track['title']
		specStrFirstOccurArr = [songTitle.find('feat.'),songTitle.find('ft.'),songTitle.find('('),songTitle.find('[')]
		endIndForSongTitleStr = len(songTitle)+1
		for potentialInd in specStrFirstOccurArr:
					if potentialInd > -1 and potentialInd < endIndForSongTitleStr:
						endIndForSongTitleStr=potentialInd
		songTitle = songTitle[:endIndForSongTitleStr]
		LyricParsing.findAndParseLyrics(artists,songTitle,appropSongIDs,track['videoId'],ytmusic)
	return appropSongIDs
#end commit (error handling)
getAppropYTMusicSongs('https://music.youtube.com/playlist?list=RDCLAK5uy_mfdqvCAl8wodlx2P2_Ai2gNkiRDAufkkI')

def getAppropSouncloudSongs(link):
	pass

def getAppropPandoraSongs(link):
	pass

def getAppropFolderSongs(link):
	pass

def getAppropM3USongs(link):
	pass

#getAppropYTSongs('https://www.youtube.com/watch?v=lKz-2zIhL6I&list=PL3p01WtxiCCr_4fQ70ZbTqKS_6KyBLo7i')