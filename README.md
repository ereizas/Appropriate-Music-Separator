# Synopsis

This program is meant to take in a music playlist link or file with one or more songs and create a new playlist with only the songs appropriate for children. Even though songs may not be marked explicit, they can still have inappropriate references to things such as drugs, violence, etc. Those who use this program should still verify that each outputted playlist has appropriate songs based on their best judgement and lyric verification if needed, but given a playlist with a mix of inappropriate and appropriate songs, it should reduce the time it takes to check manually.

# Setup

*Test packaging the code into executables.
Certain setups need to be completed before you run the program.

1. If you inputting a Spotify, YouTube, or YouTube Music playlist, go through the Genius Lyric API Setup
2. If you want to separate appropriate music from a YouTube playlist, I strongly recommend that you select the YouTube music option instead because most if not all music should transfer over once you find a playlist there, and the YouTube option has limits that will be bothersome (read below if you would still like to use YouTube instead of YouTube Music). Also, the setup for YouTube Music is much shorter.
3. For each type of playlist you desire to input and create, go to the corresponding setup section (i.e. Spotify Setup for Spotify playlist input and creation)

## Genius Lyric API Setup

This is what allows the program to request lyrics from Genius to analyze and pick out appropriate songs.

1. Go to https://genius.com/api-clients/new
2. Enter what you would like for the "App Name" field
3. Paste https://github.com/ereizas/Appropriate-Song-Separator into the "App Website URL" and click "Save"
4. Copy the Client ID and paste it into the single quote marks next to geniusClientID in the config.py file
5. Copy the Client Secret and paste it into the single quote marks next to geniusClientSecret in the same file

## Spotify Setup

You can skip steps 1-5 if you are **not** on a Windows machine. These steps are necessary in order to get some required info to put into the program. The Spotify playlist creation may take about 1.5 to 7 times the amount of songs not marked explicit in the playlist in seconds. For example, if you have 30 songs not marked explicit in your playlist, this program can take about 45 to 210 seconds to finish. This is due to the search times for the APIs I was able to find. *If your playlist is especially long (a few hundred songs most of which do not have explicit labels), then you should go into the settings and make sure your computer does not fall asleep during the duration of the program (you will most likely need to set "Sleep on battery power" and "Sleep on charge" to Never).

1. Press the Windows button (or click on the search bar in the bottom left corner of your home screen)
2. Search "Control Panel" and click on the app
3. Click on "Programs"
4. Click on "Turn Windows features on or off"
5. Make sure "Internet Information Services" and "Internet Information Services Hostable Web Core" are checked and press "OK" if you had to checkmark either one
6. Go to https://developer.spotify.com/
7. Click "Log in" in the upper right corner and log in to your Spotify account
8. Click on your username in the same spot you clicked to log in and click "Dashboard"
9. Accept the Spotify Developer Terms of Service
10. Click Create App
11. Type whatever you would like in "App name" and "App description" (leave "Website" blank)
12. Type https://localhost:8080/callback into the "Redirect URI" field
13. Check the box next to "I understand and agree with Spotify's Developer Terms of Service and Design Guidelines" and click "Save"
14. Go back to the dashboard if not already there, click on the app you created, and click on "Settings" in the upper right area of the screen
15. Copy the Client ID and paste it into the single quote marks next to spotifyClientID in the config.py file you downloaded
16. Click view Client Secret and do the same as the last step but for the single quote marks next to spotifyClientSecret

## YouTube Music Setup

1. Open the command prompt or terminal on your computer (search either one of these in the home search or applications search feature)
2. Type "cd" then find the location of the folder/directory that you downloaded the project to and copy (CTRL + C) and paste (CTRL + SHIFT + V) that into the terminal.
3. Type "pip install ytmusicapi" and press Enter
4. Type ytmusicapi oauth
5. Check if code at the end of the link that pops up and the code shown in the terminal match up
6. On the site, click on the account that you want the playlist to be created in
7. Press Enter in the terminal
8. Confirm there is a file called oauth.json in the directory/folder for the program.

## Youtube Setup

It is important to note that YouTube's API limits playlist creation and addition a lot since it costs more quota points. To clarify, every hour you get a max quota of 10,000 points. Requesting the information for every 50 songs from a playlist costs 1 point each, creating a playlist costs 50, and adding one song to the playlist costs 50. So for a playlist with 200 songs, 4 points would be used for requesting the playlist information and 50 would be used for creating a playlist which leaves us with 9946 quota points left. This only allows for 198 of the songs to be added. If there are more songs to be added after the quota is reached, you will be given the option to wait an hour for the quota to refill or to receive links of the songs to be added. I highly recommend you create a playlist beforehand, and input it into the appropriate place when you run the program.

1. Go to https://console.cloud.google.com/apis/credentials?authuser=1 and make sure you are logged in to Google
2. Click check box next to "I agree to the Google Cloud Platform Terms of Service , and the terms of service of any applicable services and APIs." and click "Agree and Continue"
3. Click on "Create Project" on the upper right portion of the screen
4. Name the project whatever you like and click "Create Project"
5. Click "Configure Consent Screen" in the upper right 
6. Click the bubble next to "External" and click "Create"
7. Type something for the App name that makes sense to you like "Appropriate Music Separator". When you run the app, you will see a site from Google pop up saying something like "Appropriate Music Separator wants access to your Google Account. Select what Appropriate Music Separator can ccess." You will have to select the first checkbox which should automatically check all the boxes. Then click "Continue" and then "Allow.
8. Select your email for User support email (you can send in any issues you have in the github page, this is just to set up the app on your computer), and scroll down and enter the same email for Developer contact information
9. Click "Save and Continue" twice in a row to arrive at the "Test users" section
10. Click "Add Users", enter your email, click "Add", and click "Save and Continue"
11. Scroll down and click the "Credentials" tab on the left side of the screen
12. Click "Create Credentials" (top left) and then OAuth client ID
13. From the Application type dropdown, select "Desktop app", and enter whatever name you would like. As you can see by the warning the YouTube part of the app may not work until 5 minutes to an hour after this.
14. Click "Create" and then download JSON
15. Move the JSON file to the folder/directory where the main files of the project are
16. Copy the name of the downloaded file and paste it into the single quote marks near googleClientSecretFileName in the config.py file
17. Click the Enabled APIs & Services tab on the left
18. Search for "YouTube Data API v3" or scroll down, and click on it under the YouTube section
19. Click "Enable"

# Ideas for Future Features

Translation Capability