#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

from pymax.cube import Cube

def _get_cube():
	cube_address = os.environ.get('cube_address', None)
	cube_port = os.environ.get('cube_port', 62910) or 62910
	return Cube(address=cube_address, port=cube_port)
from munin import MuninPlugin

class MaxCubePlugin(MuninPlugin):
	category = 'home automation'
	vlabel = u'Temperature in °C'

	def __init__(self):
		super(MaxCubePlugin, self).__init__()
		self._info = None
		self._rooms = None
		self._messages = None
		self.get_data()
		self.title = "Cube %s" % self.info.serial

	def get_data(self):
		with _get_cube() as cube:
			self._info = cube.info
			self._rooms = cube.rooms
			self._messages = cube.connection.received_messages

	@property
	def info(self):
		return self._info

	@property
	def rooms(self):
		return self._rooms

	@property
	def fields(self):
		l = []
		for room in sorted(self.rooms, key=lambda r: r.name):
			for device in sorted(room.devices, key=lambda d: d.name):
				l.append(("dev_%s_%s" % (str(room.rf_address), str(device.rf_address)), {
					'label': '%s / %s' % (room.name, device.name),
					'info': 'Current temperature on %s in %s' % (device.name, room.name),
					'min': 0,
					'type': 'GAUGE',
					'draw': 'LINE1',
				}))
		return l

	def autoconf(self):
		return True

	def execute(self):
		for room in sorted(self.rooms, key=lambda r: r.name):
			for device in sorted(room.devices, key=lambda d: d.name):
				last_message = [m for m in [self._messages['L']] if m.rf_addr.lower() == device.rf_address.lower()]
				if last_message:
					print("dev_%s_%s.value %s" % (room.rf_address, device.rf_address, last_message[0].temperature))

if __name__ == "__main__":
	MaxCubePlugin().run()