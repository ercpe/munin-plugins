#!/usr/bin/env python2
#  -*- coding: utf-8 -*-
#%# capabilities=autoconf
import os

from munin import MuninPlugin

class IPFamilyConntrack(MuninPlugin):
	title = "Connection tracking by IP family"
	category = 'network'
	vlabel = 'Connections in tracking table'

	@property
	def fields(self):
		return [
			('ipv4_tcp', { 'label': 'IPv4 / TCP', 'min': 0, 'type': 'GAUGE', 'draw': 'AREASTACK' }),
			('ipv4_udp', { 'label': 'IPv4 / UDP', 'min': 0, 'type': 'GAUGE', 'draw': 'AREASTACK' }),
			('ipv4_icmp', { 'label': 'IPv4 / ICMP', 'min': 0, 'type': 'GAUGE', 'draw': 'AREASTACK' }),
			('ipv4_other', { 'label': 'IPv4 / Other', 'min': 0, 'type': 'GAUGE', 'draw': 'AREASTACK' }),
			('ipv6_tcp', { 'label': 'IPv6 / TCP', 'min': 0, 'type': 'GAUGE', 'draw': 'AREASTACK' }),
			('ipv6_udp', { 'label': 'IPv6 / UDP', 'min': 0, 'type': 'GAUGE', 'draw': 'AREASTACK' }),
			('ipv6_icmpv6', { 'label': 'IPv6 / ICMP', 'min': 0, 'type': 'GAUGE', 'draw': 'AREASTACK' }),
			('ipv6_other', { 'label': 'IPv6 / Other', 'min': 0, 'type': 'GAUGE', 'draw': 'AREASTACK' }),
		]

	def autoconf(self):
		return True

	def execute(self):
		d = dict(((x[0], 0) for x in self.fields))

		with open(os.environ.get('conntrack_file', '/proc/net/nf_conntrack')) as f:
			for line in f:
				data = line.split()
				family, proto = data[0], data[2]

				if proto in ['tcp', 'udp', 'icmp', 'icmpv6']:
					d['%s_%s' % (family, proto)] += 1
				else:
					d['%s_other' % family] += 1

		for x in d.items():
			print("%s.value %s" % x)


if __name__ == "__main__":
	IPFamilyConntrack().run()