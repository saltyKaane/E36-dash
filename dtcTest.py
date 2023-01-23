#!/usr/bin/python
import obd

# DEBUG: Set debug logging so we can see everything that is happening.
obd.logger.setLevel(obd.logging.DEBUG)

connection = obd.Async("/dev/tty.usbserial-113010839615", 115200, "3", fast=False)

connection.watch(obd.commands.GET_DTC)
connection.watch(obd.commands.CLEAR_DTC)

connection.start()

# Returns a list of tuples containing the error code and the description (if available).
response = connection.query(obd.commands.GET_DTC)

# Loop through the list.
for code,desc in response.value:
	print code
	
response = connection.query(obd.commands.CLEAR_DTC)

print "DTCs cleared"
