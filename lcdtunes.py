import os
import sys
import base64
import xml.etree.ElementTree
from time import *

# Import modified driver - gives us control over the backlight
import RPi_I2C_driver

def ascii_integers_to_string(string, base=16, digits_per_char=2):
	return "".join([chr(int(string[i:i+digits_per_char], base=base)) for i in range(0, len(string), digits_per_char)])

# function to scroll text

def scroll_ltr_infinite(string):
	str_pad = " " * 20
	string = str_pad + string

	while updateflag:
    		for i in range (0, len(string)):
        		lcd_text = string[i:(i+20)]
        		device.lcd_display_string(lcd_text,1)
        		sleep(0.3)
        		device.lcd_display_string(str_pad,1)



path = "/tmp/shairport-sync-metadata"
fifo = open(path, "r")

def main():
	wholeelement = ""
	title = ""
	album = ""
	artist = ""
	line4 = ""
	updateflag = False
	# initialize the screen
	device = RPi_I2C_driver.lcd()

	device.lcd_clear()
	device.lcd_display_string("     Music Box      ",2)
	sleep(3)
	device.lcd_clear()
	device.backlight(0)

	with fifo as f:
		while True:
			line = f.readline()
			line = line.strip()
			#print "Got " + line
			wholeelement += line
			if line.endswith("</item>"):
				# print "end of item"
				# print "element = " + wholeelement
				
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
						print "Playback finished..."
						device.lcd_clear()
						device.backlight(0)

					if code == "pbeg":
						device.backlight(1)
						print "Playback started..."
						device.lcd_clear()
					if code == "snua":
						print "User agent received"
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


				if data != "":
					print "Type: " + type + ", Code: " + code + ", Data: " + data
				wholeelement = ""
			if updateflag:
				print "\nTitle: " + title + "\nArtist: " + artist + "\nAlbum: " + album

				device.lcd_clear()
				# for now, truncate to 20 chars to prevent wrapping onto other lines
				device.lcd_display_string(title[:20],1)
				device.lcd_display_string(artist[:20],2)
				device.lcd_display_string(album[:20],3)
				device.lcd_display_string(line4[:20],4)
				updateflag = False
	fifo.close()

if __name__ == "__main__":
	main()
