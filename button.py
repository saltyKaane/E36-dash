import sys
import pygame
import os
import pygameui as ui
import logging
import signal

#log_format = '%(asctime)-6s: %(name)s - %(levelname)s - %(message)s'
#console_handler = logging.StreamHandler()
#console_handler.setFormatter(logging.Formatter(log_format))
#logger = logging.getLogger()
#logger.setLevel(logging.DEBUG)
#logger.addHandler(console_handler)

#os.putenv('SDL_FBDEV', '/dev/fb1')
#os.putenv('SDL_MOUSEDRV', 'TSLIB')
#os.putenv('SDL_MOUSEDEV', '/dev/input/touchscreen')

MARGIN = 20

img = pygame.image.load("images/m3_logo.png")

class PiTft(ui.Scene):
	def __init__(self):
		ui.Scene.__init__(self)
		
		self.on17_button = ui.ImageButton(None, img)
		#self.on17_button = ui.Button(ui.Rect(MARGIN, MARGIN, 130, 60), '17 on')
		self.on17_button.on_clicked.connect(self.gpi_button)
		self.add_child(self.on17_button)

	def gpi_button(self, frame, image):
		print "M3 Power!"

	def update(self, dt):
		ui.Scene.update(self, dt)

def signal_handler(signal, frame):
	sys.exit()
		
ui.init('Raspberry Pi UI', (480, 320))
#pygame.mouse.set_visible(False)

pitft = PiTft()

signal.signal(signal.SIGINT, signal_handler)

ui.scene.push(pitft)
ui.run()