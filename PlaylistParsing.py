import LyricParsing, config, StrParsing
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from ytmusicapi import YTMusic

def getAppropSpotifySongs(link:str)->list[str]|str:
	"""
	Parses the Spotfiy playlist data for the artists and song titles to help find lyrics and then returns the Spotify ids for the appropriate songs
	@param link : link to playlist
	@return appropSongIds : list with string Spotify ids of the appropriate songs in the playlist
	@return : str error message on error
	"""
	
	playlistID, appropSongIds= '', []
	token = SpotifyOAuth(client_id=config.spotifyClientID,client_secret=config.spotifyClientSecret,scope="playlist-read-private",redirect_uri="https://localhost:8080/callback",username=config.spotifyUserID)
	spotifyObj = spotipy.Spotify(auth_manager=token)
	playlistID = StrParsing.getSpotifyPlaylistID(link)
	if playlistID==None:
		return "Error: Invalid Spotify link"
	data = dict()
	try:
		data = spotifyObj.playlist_tracks(playlistID,fields=any)
	except Exception as e:
		return "Error: " + str(e)
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
					return "Error " + str(e)
				attempts+=1
				print(data)
		#indicates whether the variable "metadata" was assigned a message saying that there is suspicious activity coming from the user's IP address as the only element in the array
		azUnusActErrOccurred = False
		#keeps track the amount of requests since the
		reqsSinceLastAZReq = 0
		for item in data['items']:
			if not item['track']['explicit']:
				songTitle = item['track']['name']
				#conditional in list comprehension prevents featured artists mentioned in the song title from being repeated
				artists = [artist['name'] for artist in item['track']['artists'] if artist['name'] not in songTitle]
				azUnusActErrOccurred,reqsSinceLastAZReq = LyricParsing.findAndParseLyrics(artists,songTitle,appropSongIds,item['track']['id'],azUnusActErrOccurred,reqsSinceLastAZReq,'')
				if type(azUnusActErrOccurred)==None:
					return "File retrieval error"
		data = spotifyObj.next(data)
		
	return appropSongIds

def getAppropYTSongs(link:str):
	"""
	Parses the songs in a YouTube playlist for the artists and song title and returns the ids of those songs that are appropriate for children
	@param link : link to YouTube playlist
	@return : resource object with necessary credentials stored to read, create and update playlists on success, str error message on failure
	@return appropSongIDs : list of YouTube ids for videos deemed appropriate for children by the program on success, None on failure
	"""

	#Must copy file name into first parameter
	flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
	config.googleClientSecretFileName, scopes=['https://www.googleapis.com/auth/youtube.readonly','https://www.googleapis.com/auth/youtube.force-ssl'])
	credentials = flow.run_local_server()
	youtube = googleapiclient.discovery.build('youtube', 'v3', credentials=credentials)
	appropSongIDs = []
	nextPageToken = ''
	response = 'nextPageToken'
	while 'nextPageToken' in response:
		request = youtube.playlistItems().list(
			part="snippet",
			maxResults=50,
			playlistId=StrParsing.getYTPlaylistID(link),
			pageToken = nextPageToken
		)
		try:
			response = request.execute()
		except Exception as e:
			return "Error: " + str(e), None, None
		#indicates whether the variable "metadata" was assigned a message saying that there is suspicious activity coming from the user's IP address as the only element in the array
		azUnusActErrOccurred = False
		#keeps track the amount of requests since the
		reqsSinceLastAZReq = 0
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
			azUnusActErrOccurred,reqsSinceLastAZReq = LyricParsing.findAndParseLyrics([artists],songTitle,appropSongIDs,item['snippet']['resourceId']['videoId'],azUnusActErrOccurred,reqsSinceLastAZReq,youtube)
			if type(azUnusActErrOccurred)==None:
				return "File retrieval error", None, None
		if 'nextPageToken' in response:
			nextPageToken=response['nextPageToken']
	return youtube,appropSongIDs

def getAppropYTMusicSongs(link:str):
	"""
	Uses the YT Music api to collect artist and song title info from each song in a playlist and returns ids corresponding to songs deemed appropriate
	@param link : link to YouTube Music playlist
	@return appropSongIDs : list of YouTube Music ids for songs deemed appropriate for children by the program
	@returned ytmusic : resource object that can read, create, and edit playlists
	"""
	
	appropSongIDs = []
	data = dict()
	ytmusic = YTMusic('oauth.json')
	try:
		data = ytmusic.get_playlist(StrParsing.getYTPlaylistID(link),limit=None)
	except Exception as e:
		return "Error: " + str(e), None
	#indicates whether the variable "metadata" was assigned a message saying that there is suspicious activity coming from the user's IP address as the only element in the array
	azUnusActErrOccurred = False
    #keeps track the amount of requests since the
	reqsSinceLastAZReq = 0
	for track in data['tracks']:
		artists = [artist['name'] for artist in track['artists']]
		songTitle = track['title']
		specStrFirstOccurArr = [songTitle.find('feat.'),songTitle.find('ft.'),songTitle.find('('),songTitle.find('[')]
		endIndForSongTitleStr = len(songTitle)+1
		for potentialInd in specStrFirstOccurArr:
					if potentialInd > -1 and potentialInd < endIndForSongTitleStr:
						endIndForSongTitleStr=potentialInd
		songTitle = songTitle[:endIndForSongTitleStr]
		azUnusActErrOccurred,reqsSinceLastAZReq = LyricParsing.findAndParseLyrics(artists,songTitle,appropSongIDs,track['videoId'],azUnusActErrOccurred,reqsSinceLastAZReq,ytmusic)
		if type(azUnusActErrOccurred)==None:
			return "File retrieval error", None
	return appropSongIDs,ytmusic

#Soundcloud is still working on access to its API (in 2021 they announced that they will figure out another way to start authorizing developer apps instead of a Google form, but they still haven't) and I cannot find any wrappers that can create playlists
def getAppropSouncloudSongs(link:str):
	pass
#developer page is not working
def getAppropPandoraSongs(link):
	pass
#Still in beta, so I submitted a request and am waiting to hear back
def getAppropAmazonMusic(link):
	pass