import requests

def spotify(link):
    playlistID = ''
    if('?' in link):
        playlistID = link[link.index('playlist/')+9:link.index('?')]
    else:
        playlistID = link[link.index('playlist/')+9:]
    

print(spotify('https://open.spotify.com/playlist/31hXsTQWKdum0YD6eHzLGf?si=yCdM_Gg_S6yI10rHweJl3Q'))

def appleMusic(link):
    pass

def youtube(link):
    pass

def soundcloud(link):
    pass

def folder(link):
    pass

def m3u(link):
    pass