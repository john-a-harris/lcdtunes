#!/usr/bin/python

import os
import requests
import json

CLIENT_ID = 
CLIENT_SECRET = 

# some constants for codes and types
STYPE = "spot".encode('utf-8')
STYPE = STYPE.encode('hex')

STITLE = "stit"
STITLE = STITLE.encode('hex')

SARTIST = "sart"
SARTIST = SARTIST.encode('hex')

SALBUM = "salb"
SALBUM = SALBUM.encode('hex')

SPLAY = "play".encode('hex')

SSTOP = "stop".encode('hex')

try:
	PLAYER_EVENT = os.environ["PLAYER_EVENT"]
except KeyError:
	print("Player event variable not set")
try:
	TRACK_ID = os.environ['TRACK_ID']
except KeyError:
        print("Track id variable not set")

# base URL of all Spotify API endpoints
BASE_URL = 'https://api.spotify.com/v1/'

AUTH_URL = 'https://accounts.spotify.com/api/token'

#print("Player event: " + PLAYER_EVENT)
#print("Track ID: " + TRACK_ID)

if PLAYER_EVENT in ("started", "session_connected"):
	print("got started event")
	path = "/tmp/shairport-sync-metadata"
        fifo = open(path, "w")
	fifo.write("<item><type>" + STYPE + "</type><code>" + SPLAY + "</code></item>\n")
	fifo.close()
	exit()

if PLAYER_EVENT in ("stopped", "session_disconnected"):
	print("got stopped event")
        path = "/tmp/shairport-sync-metadata"
        fifo = open(path, "w")
	fifo.write("<item><type>" + STYPE + "</type><code>" + SSTOP + "</code></item>\n")
	fifo.close()
	exit()

if PLAYER_EVENT == "playing":

	path = "/tmp/shairport-sync-metadata"
        fifo = open(path, "w")

	# POST
	auth_response = requests.post(AUTH_URL, {
	    'grant_type': 'client_credentials',
	    'client_id': CLIENT_ID,
	    'client_secret': CLIENT_SECRET,
	})

	# convert the response to JSON
	auth_response_data = auth_response.json()

	# save the access token
	access_token = auth_response_data['access_token']

	headers = {
	    'Authorization': 'Bearer {token}'.format(token=access_token)
	}

	# actual GET request with proper header
	r = requests.get(BASE_URL + 'tracks/' + TRACK_ID, headers=headers)

	r = r.json()
	title = r['name']
	# print(title + ' : ' + title.encode('base64'))
	# print("<item><type>" + STYPE + "</type><code>" + STITLE + "</code><data>" + title.encode('base64') + "</data></item>\n")
	fifo.write("<item><type>" + STYPE + "</type><code>" + STITLE + "</code><data>" + title.encode('base64') + "</data></item>\n")

	album = r['album']['name']
	fifo.write("<item><type>" + STYPE + "</type><code>" + SALBUM + "</code><data>" + album.encode('base64') + "</data></item>\n")

	artist = ""
	if len(r['artists']) > 1:
		artist_list = []
		for a in r['artists']:
			# artist = artist + ", " + a['name'] 
			artist_list.append(a['name'])
		artist = ', '.join(artist_list)
	else:
		artist = r['artists'][0]['name']
	fifo.write("<item><type>" + STYPE + "</type><code>" + SARTIST + "</code><data>" + artist.encode('base64') + "</data></item>\n")

	# print('Track name: ' + r['name'])
	# print('Album: ' + r['album']['name'])
	# print('Artist: ' + r['artists'][0]['name'])

	#print(json.dumps(r, indent=1))
	fifo.close()
