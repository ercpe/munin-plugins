# -*- coding: utf-8 -*-

import sys
import os

from munin import MuninPlugin

class OpenDKIMStats(MuninPlugin):
	title = "DKIM signatures"
	category = 'mail'
	vlabel = 'Connections in tracking table'

	@property
	def fields(self):
		return [
			('messages', {
				'label': 'Messages',
				'min': 0,
				'type': 'COUNTER',
				'draw': 'LINE'
			}),
			('signatures_passed', {
				'label': 'Signatures passed',
				'min': 0,
				'type': 'COUNTER',
				'draw': 'LINE'
			}),
			('signatures_failed', {
				'label': 'Signatures failed',
				'min': 0,
				'type': 'COUNTER',
				'draw': 'LINE'
			}),
		]

	def autoconf(self):
		return True

	def execute(self):
		# file format: http://fossies.org/linux/opendkim/stats/README
		stats_file = os.environ.get('stats_file', '/var/lib/opendkim/stats.dat')

		messages = 0
		sig_passed = 0
		sig_failed = 0

		with open(stats_file, 'r') as f:
			for line in (x.strip() for x in f.readlines()):
				if not line:
					continue

				try:
					if line[0] == 'M':
						# message
						messages += 1
					elif line[0] == 'S':
						# signature
						passed = line.split('\t')[1]
						if int(passed) == 1:
							sig_passed += 1
						else:
							sig_failed += 1
				except Exception as ex:
					print(ex)

		print("messages.value %s" % messages)
		print("signatures_passed.value %s" % sig_passed)
		print("signatures_failed.value %s" % sig_failed)


if __name__ == "__main__":
	OpenDKIMStats().run()