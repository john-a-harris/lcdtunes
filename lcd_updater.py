#!/usr/bin/python3
#
# moOde audio player (C) 2014 Tim Curtis
# http://moodeaudio.org
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# Stub script for lcd-updater.sh daemon
#

import base64

# some constants for codes and types
MTYPE = "mood".encode("utf-8").hex()

MTITLE = "mtit".encode("utf-8").hex()

MARTIST = "mart".encode("utf-8").hex()

MALBUM = "malb".encode("utf-8").hex()

MPLAY = "play".encode("utf-8").hex()

MSTOP = "stop".encode("utf-8").hex()

#Load the values from the currentsong file
songattr={}
with open("/var/local/www/currentsong.txt") as file1:
   for line in file1:
      name, var = line.partition("=")[::2]
      songattr[name.strip()] = var.strip()


#print(songattr["artist"])
#print(songattr["title"])

print(songattr)

#Check to see if Airplay is active
if songattr["file"] == "AirPlay Active":
    print("airplay active")
    exit()


#Check to see if state is play
if songattr["state"] == "play":
    print ("Moode playing")
    print ("Artist: " + songattr["artist"])
    artist = base64.b64encode(songattr["artist"].encode()).decode()
    print(artist)
    print ("Title: " + songattr["title"])
    title = base64.b64encode(songattr["title"].encode()).decode()
    print(title)
    print ("Album: " + songattr["album"])
    album = base64.b64encode(songattr["album"].encode()).decode()
    print(album)

    path = "/tmp/shairport-sync-metadata"
    fifo = open(path, "w")
    fifo.write("<item><type>" + MTYPE + "</type><code>" + MPLAY + "</code></item>\n")
    fifo.write("<item><type>" + MTYPE + "</type><code>" + MARTIST + "</code><data>" + artist + "</data></item>\n")
    fifo.write("<item><type>" + MTYPE + "</type><code>" + MTITLE + "</code><data>" + title + "</data></item>\n")
    fifo.write("<item><type>" + MTYPE + "</type><code>" + MALBUM + "</code><data>" + album + "</data></item>\n")

    fifo.close()

# Check to see if state is paused
if songattr["state"] in ("pause", "stop"):
    print ("Moode paused")
    path = "/tmp/shairport-sync-metadata"
    fifo = open(path, "w")
    fifo.write("<item><type>" + MTYPE + "</type><code>" + MSTOP + "</code></item>\n")

    fifo.close()
