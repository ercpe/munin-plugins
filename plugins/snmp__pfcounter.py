#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (C) 2014 Johann Schmitz <johann@j-schmitz.net>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU Library General Public License as published by
# the Free Software Foundation; version 2 only
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library General Public License for more details.
#
# You should have received a copy of the GNU Library General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#

"""
=head1 NAME

snmp__generic_ - Generic SNMP plugin

=head1 CONFIGURATION


=head1 MAGIC MARKERS

	#%# family=snmpauto
	#%# capabilities=snmpconf

=head1 VERSION

0.0.1

=head1 BUGS

Open a ticket at https://github.com/ercpe/contrib if you find one.

=head1 AUTHOR

Johann Schmitz <johann@j-schmitz.net>

=head1 LICENSE

GPLv2

=cut
"""

import sys
import os
import logging

import re
from pysnmp.entity.rfc3413.oneliner import cmdgen


class SNMPClient(object):
	def __init__(self, host, port, community):
		self.hostname = host
		self.transport = cmdgen.UdpTransportTarget((host, int(port)))
		self.auth = cmdgen.CommunityData('test-agent', community)
		self.gen = cmdgen.CommandGenerator()

	def print_config(self):
		print("""host_name {hostname}
graph_title pfCounter
graph_vlabel #
graph_args --base 1000
graph_category network
graph_info pfCounter
pfCounterMatch.info Number of packets that matched a filter rule.
pfCounterMatch.label pfCounterMatch
pfCounterMatch.type GAUGE
pfCounterMatch.min 0
pfCounterBadOffset.info Number of packets with bad offset.
pfCounterBadOffset.label pfCounterBadOffset
pfCounterBadOffset.type GAUGE
pfCounterBadOffset.min 0
pfCounterFragment.info Number of fragmented packets.
pfCounterFragment.label pfCounterFragment
pfCounterFragment.type GAUGE
pfCounterFragment.min 0
pfCounterShort.info Number of short packets.
pfCounterShort.label pfCounterShort
pfCounterShort.type GAUGE
pfCounterShort.min 0
pfCounterNormalize.info Number of normalized packets.
pfCounterNormalize.label pfCounterNormalize
pfCounterNormalize.type GAUGE
pfCounterNormalize.min 0
pfCounterMemDrop.info Number of packets dropped due to memory limitations.
pfCounterMemDrop.label pfCounterMemDrop
pfCounterMemDrop.type GAUGE
pfCounterMemDrop.min 0
""".format(hostname=self.hostname))

	def execute(self):

		for datarow, oid in [
			('pfCounterMatch', '1.3.6.1.4.1.12325.1.200.1.2.1.0'),
			('pfCounterBadOffset', '1.3.6.1.4.1.12325.1.200.1.2.2.0'),
			('pfCounterFragment', '1.3.6.1.4.1.12325.1.200.1.2.3.0'),
			('pfCounterShort', '1.3.6.1.4.1.12325.1.200.1.2.4.0'),
			('pfCounterNormalize', '1.3.6.1.4.1.12325.1.200.1.2.5.0'),
			('pfCounterMemDrop', '1.3.6.1.4.1.12325.1.200.1.2.6.0'),
		]:
			errorIndication, errorStatus, errorIndex, varBindTable = self.gen.getCmd(self.auth, self.transport, oid)

			if errorIndication:
				logging.error("SNMP getCmd for %s failed: %s, %s, %s" % (oid, errorIndication, errorStatus, errorIndex))
				continue
			else:
				try:
					print("%s.value %s" % (datarow, int(varBindTable[0][1])))
				except ValueError:
					continue

host = os.getenv('host', 'localhost')
port = os.getenv('port', 161)
community = os.getenv('community', 'public')
debug = bool(os.getenv('MUNIN_DEBUG', os.getenv('DEBUG', 0)))

if debug:
	logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)-7s %(message)s')

try:
	match = re.search("^snmp_([^_]+)_pfcounter$", sys.argv[0], re.IGNORECASE)
	host = match.group(1)
	match = re.search("^([^:]+):(\d+)$", host)
	if match is not None:
		host = match.group(1)
		port = match.group(2)
except Exception as ex:
	logging.exception("Caught exception: %s" % ex)

if "snmpconf" in sys.argv[1:]:
	print("require 1.3.6.1.4.1.12325.1.200.1.2.1.0")
	sys.exit(0)
else:
	if not (host and port and community):
		print("# Bad configuration. Cannot run with Host=%s, port=%s and community=%s" % (host, port, community))
		sys.exit(1)

	c = SNMPClient(host, port, community)

	if "config" in sys.argv[1:]:
		c.print_config()
	else:
		c.execute()
