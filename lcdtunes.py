import os
import sys
import base64
import xml.etree.ElementTree
from time import *
import thread

# Import modified driver - gives us control over the backlight
import RPi_I2C_driver

# Set up the logging, based on the command line arguments

import logging
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-d', '--debug', help='Log debug information to screen', action="store_true")
parser.add_argument('-f', '--file', help='Log debug information to file', action="store_true")
args = parser.parse_args()
if args.debug:
        loglevel = logging.DEBUG
else:
        loglevel = logging.INFO

# logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s',filename='example.log',level=loglevel)

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
# create console handler to show messages on screen
ch = logging.StreamHandler()
ch.setLevel(loglevel)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(levelname)s: %(message)s')
file_formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
ch.setFormatter(formatter)
# add the handlers to logger
logger.addHandler(ch)


# create file handler which logs messages to file if user specifed it on the command line
if args.file:
        fh = logging.FileHandler('logger.log', 'w')
        fh.setLevel(loglevel)
        fh.setFormatter(file_formatter)
        logger.addHandler(fh)


# declare global variables
titleflag = False
device = RPi_I2C_driver.lcd()

def ascii_integers_to_string(string, base=16, digits_per_char=2):
	return "".join([chr(int(string[i:i+digits_per_char], base=base)) for i in range(0, len(string), digits_per_char)])

# function to scroll text

def scroll_ltr_infinite(string, line):
	logger.debug("new thread started...")
	logger.debug(string)
	global titleflag
	global device
	titleflag = False
	logger.debug(titleflag)
	str_pad = " " * 20
	string = str_pad + string
	while not titleflag:
    		for i in range (0, len(string)):
			logger.debug("in the for loop...")
			logger.debug(i)
        		lcd_text = string[i:(i+20)]
        		device.lcd_display_string(lcd_text, line)
        		sleep(0.25)
        		device.lcd_display_string(str_pad, line)
		logger.debug("while loop...")
		logger.debug(titleflag)
	logger.debug("Thread exiting...")



def main():
	path = "/tmp/shairport-sync-metadata"
	fifo = open(path, "r")
	wholeelement = ""
	title = ""
	album = ""
	artist = ""
	line4 = ""
	updateflag = False
	global titleflag
	global device
	# initialize the screen

	device.lcd_clear()
	device.lcd_display_string("     Music Box      ",2)
	sleep(3)
	device.lcd_clear()
	device.backlight(0)

	with fifo as f:
		while True:
			line = f.readline()
			line = line.strip()
			logger.debug("Got " + line)
			wholeelement += line
			if line.endswith("</item>"):
				logger.debug("end of item")
				logger.debug("element = " + wholeelement)
				
				# Now that we've got a whole xml element, we can process it
				doc = xml.etree.ElementTree.fromstring(wholeelement)
				
				# get the type and convert to ascii
				type = doc.findtext('type')
				type = ascii_integers_to_string(type)
				# get the code and convert to ascii
				code = doc.findtext('code')
				code = ascii_integers_to_string(code)

				# get the data out, if there is any
				data = doc.findtext('data')
				if data != None:
					data = base64.b64decode(data)
				else:
					data = ""
				if type == "ssnc":
					#if code == "pfls":
						#title = ""
						#album = ""
						#artist = ""
						#updateflag = True
						
					if code == "pend":
						logger.info("Playback finished...")
						titleflag = True # stop running title thread if there is one
						device.lcd_clear()
						device.backlight(0)

					if code == "pbeg":
						device.backlight(1)
						logger.info("Playback started...")
						device.lcd_clear()
					if code == "snua":
						logger.info("User agent received")
						line4 = data
						updateflag = True				
				if type == "core":
					#process the codes that we're interested in
					if code == "assn":
						if title != data:
							title = data
							updateflag = True
					if code == "asar":
						if artist != data:
							artist = data
							updateflag = True
					if code == "asal":
						if album != data:
							album = data
							updateflag = True
					if code == "asbr":
						logger.info("Bitrate:")
						logger.info(int("0x" + ''.join([hex(ord(x))[2:] for x in data]), base=16))


				if data != "":
					logger.info("Type: " + type + ", Code: " + code + ", Data: " + data)
				else:
					logger.info("Type: " + type + ", Code: " + code)
					
				wholeelement = ""
			if updateflag:
				logger.info("\nTitle: " + title + "\nArtist: " + artist + "\nAlbum: " + album)

				# device.lcd_clear()
				# for now, truncate to 20 chars to prevent wrapping onto other lines
				# Check to see if title is > 20 chars. If yes start a thread to scroll text. If no, just display as is
				if (len(title) > 20):
					titleflag = True # stop running title thread if there is one
					thread.start_new_thread(scroll_ltr_infinite, (title,))
				else:
					device.lcd_display_string(title[:20],1)
				# device.lcd_display_string(artist[:20],2)
				# device.lcd_display_string(album[:20],3)
				# device.lcd_display_string(line4[:20],4)
				updateflag = False
	fifo.close()

def test():
	global titleflag
	device.lcd_display_string("This is line 2",2)
	sleep(1)
	logger.debug("test function")
	thread.start_new_thread(scroll_ltr_infinite, ("This is a long string that should scroll in a new thread", 1))
	sleep(1)
	device.lcd_display_string("This is line 3",3)
	# thread.start_new_thread(scroll_ltr_infinite, ("This is a different string that should scroll in a new thread", 2))
	# thread.start_new_thread(scroll_ltr_infinite, ())
	#scroll_ltr_infinite("This is a long string that should scroll")
	sleep(60)
	titleflag = True
	logger.debug("titleflag set to true")
	sleep(60)
	logger.debug("exiting...")

if __name__ == "__main__":
	# main()
	test()
