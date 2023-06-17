import LyricParsing, config
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
#Test invalid links given

def getAppropSpotifySongs(link:str)->list[str]:
	"""
	This function is meant to parse the Spotfiy playlist data to retrieve the Spotify ids for the appropriate songs and update and return an array with those ids.
	@param link : link to playlist
	@return appropSongIds : list with string Spotify ids of the appropriate songs in the playlist
	"""
	
	if 'spotify' not in link:
		return 'Not a valid Spotify link'
	playlistID, appropSongIds= '', []
	token = SpotifyOAuth(client_id=config.spotifyClientID,client_secret=config.spotifyClientSecret,scope="playlist-read-private",redirect_uri="https://localhost:8080/callback")
	spotifyObj = spotipy.Spotify(auth_manager=token)
	#extracts playlist id from the two types of spotify links
	if('?' in link):
		playlistID = link[link.index('playlist/')+9:link.index('?')]
	else:
		playlistID = link[link.index('playlist/')+9:]
	data = spotifyObj.playlist_tracks(playlistID,fields=any)
	#while there are more songs in the playlist to get data from
	while(data['next']):
		#refreshes access token if it has expired
		if 'error' in data and data['error']['status']==401:
			token = SpotifyOAuth(client_id=config.spotifyClientID,client_secret=config.spotifyClientSecret,scope="playlist-read-private",redirect_uri="https://localhost:8080/callback")
			spotifyObj = spotipy.Spotify(auth_manager=token)
		#for other errors, retries three times
		elif 'items' not in data:
			attempts = 0
			while attempts<3 and 'items' not in data:
				data = spotifyObj.playlist_tracks(playlistID,fields=any)
				attempts+=1
				print(data)
		try:
			for item in data['items']:
				if not item['track']['explicit']:
					artists, songTitle = [], item['track']['name']
					for artist in item['track']['artists']:
						#prevents featured artists mentioned in song title from being repeated
						if(artist['name'] not in songTitle):
							artists.append(artist['name'])
					#passing artists into an array enforces the perception of artists as being an array
					LyricParsing.findAndParseLyrics(artists,songTitle,appropSongIds,item['track']['id'],'')
			data = spotifyObj.next(data)
		except Exception as e:
			print(e)
			break
	return appropSongIds

#try to find lyrics first and then YT transcript as last resort
def getAppropYTSongs(link:str)->list[str]:
	"""
	This function parses the songs in a YouTube playlist and returns the ids of those songs that are appropriate for children.
	@param link : link to YouTube playlist
	@return youtube : resource object with necessary credentials stored to read, create and update playlists
	@return appropSongIDs : list of YouTube ids for videos deemed appropriate for children by the program
	"""

	if 'youtube' not in link:
		return 'Not a valid YouTube link'
	#given a playlist link from either a specific video on the list (which means the video id is in the playlist link) or just the playlist itself, lastAmpInd will be the needed end index for playlistID
	lastAmpInd = link.rfind('&')
	listEqInd = link.find('list=')
	if(lastAmpInd<listEqInd):
		lastAmpInd = len(link)
	playlistID = link[link.index('list=')+5:lastAmpInd]
	#Must copy file name into first parameter
	flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
	config.googleClientSecretFileName, scopes=['https://www.googleapis.com/auth/youtube.readonly','https://www.googleapis.com/auth/youtube.force-ssl'])
	credentials = flow.run_local_server()
	youtube = googleapiclient.discovery.build('youtube', 'v3', credentials=credentials)
	appropSongIDs = []
	#initialized to 50 to allow the loop to run, reassigned later
	numResults = 50
	nextPageToken = ''
	#While the results returned by the current request is greater than or equal to 50 (the max number of results that can be returned), the program will keep requesting transcripts
	while numResults>=50:
		request = youtube.playlistItems().list(
			part="snippet",
			maxResults=50,
			playlistId=playlistID,
			pageToken = nextPageToken
		)
		response = request.execute()
		numResults = response['pageInfo']['totalResults']
		for item in response['items']:
			vidTitle = item['snippet']['title']
			artists = ''
			songTitle = ''
			if ' - ' in vidTitle:
				artists = vidTitle[:vidTitle.find(' - ')]
				#determines where to cut off the title of song based on the video title 
				specStrFirstOccurArr = [vidTitle.find('feat.'),vidTitle.find('ft.'),vidTitle.find('('),vidTitle.find('[')]
				endIndForSongTitleStr = len(vidTitle)+1
				for potentialInd in specStrFirstOccurArr:
					if potentialInd > 0 and potentialInd < endIndForSongTitleStr:
						endIndForSongTitleStr=potentialInd
				songTitle = vidTitle[vidTitle.find(' - ')+3:endIndForSongTitleStr-1]
				print(artists + ' - ' + songTitle)
			else:
				#if video title is not in standard format of "Artist Name - Song Title", then default to info below which should be more favorable for api searches
				songTitle = vidTitle
			LyricParsing.findAndParseLyrics([artists],songTitle,appropSongIDs,item['snippet']['resourceId']['videoId'],youtube)
		if 'nextPageToken' in response:
			nextPageToken=response['nextPageToken']
	return youtube,appropSongIDs
		
def getAppropYTMusicSongs(link):
	pass
def getAppropSouncloudSongs(link):
	pass

def getAppropPandoraSongs(link):
	pass

def getAppropFolderSongs(link):
	pass

def getAppropM3USongs(link):
	pass

#getAppropYTSongs('https://www.youtube.com/watch?v=lKz-2zIhL6I&list=PL3p01WtxiCCr_4fQ70ZbTqKS_6KyBLo7i')