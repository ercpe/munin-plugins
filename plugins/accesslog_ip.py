#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#%# family=auto
#%# capabilities=autoconf

import os
import tempfile
from munin import MuninPlugin

class IPDistribution(MuninPlugin):
	title = "IP distribution"

	@property
	def fields(self):
		return [
			("ipv4", {
				'label': 'IPv4',
				'min': 0,
				'type': 'GAUGE'
			}),
			("ipv6", {
				'label': 'IPv6',
				'min': 0,
				'type': 'GAUGE'
			})
		]

	def execute(self):
		raw_file = os.environ['file']

		tempfd, access_log_file = tempfile.mkstemp(text=True)

		try:
			state_file = os.path.join('/var/lib/munin/plugin-state/',  __file__.replace('.py', ''))
			os.system("logtail %s %s > %s" % (raw_file, os.environ.get('state_file', state_file), access_log_file))
		
			with open(access_log_file, 'r') as f:
				ipv4 = 0
				ipv6 = 0

				for line in f:
					try:
						remote_host = line[:line.index(' ')]
						if not ':' in remote_host:
							ipv4 += 1
						else:
							ipv6 += 1
					except:
						pass

				print("ipv4.value %s" % ipv4)
				print("ipv6.value %s" % ipv6)
		finally:
			os.remove(access_log_file)


if __name__ == "__main__":
	IPDistribution().run()
