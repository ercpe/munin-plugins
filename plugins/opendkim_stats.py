#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from utils import MemorableMuninPlugin


class OpenDKIMStats(MemorableMuninPlugin):
	title = "DKIM signatures"
	category = 'mail'
	vlabel = 'Messages'

	@property
	def fields(self):
		return [
			('messages', {
				'label': 'Messages',
				'min': 0,
				'type': 'GAUGE',
				'draw': 'LINE'
			}),
			('signatures_passed', {
				'label': 'Signatures passed',
				'min': 0,
				'type': 'GAUGE',
				'draw': 'LINE'
			}),
			('signatures_failed', {
				'label': 'Signatures failed',
				'min': 0,
				'type': 'GAUGE',
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
		old_messages, old_sig_passed, old_sig_failed = tuple(self.load_state((0, 0, 0)))

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

		if old_messages == old_sig_passed == old_sig_failed == 0:
			# avoid big spike when state file is missing
			new_messages = 0
			new_sig_passed = 0
			new_sig_failed = 0
		else:
			new_messages = messages - old_messages
			new_sig_passed = sig_passed - old_sig_passed
			new_sig_failed = sig_failed - old_sig_failed

		print("messages.value %s" % new_messages)
		print("signatures_passed.value %s" % new_sig_passed)
		print("signatures_failed.value %s" % new_sig_failed)
		self.save_state((messages, sig_passed, sig_failed))

if __name__ == "__main__":
	OpenDKIMStats().run()
