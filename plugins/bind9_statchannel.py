#!/usr/bin/env python
# -*- coding: utf-8 -*-

from munin import MuninPlugin
from lxml import etree

class Bind9Statchannel(MuninPlugin):

	def config(self):
		mgraph_prefix = "bind9_statchannel_"

#multigraph diskstats_latency
#graph_title Disk latency per device
#graph_args --base 1000
#graph_vlabel Average IO Wait (seconds)
#graph_category disk
#graph_width 400
#
#xvda1_avgwait.label xvda1
#xvda1_avgwait.type GAUGE
#xvda1_avgwait.info Average wait time for an I/O request
#xvda1_avgwait.min 0
#xvda1_avgwait.draw LINE1
#xvda2_avgwait.label xvda2
#xvda2_avgwait.type GAUGE
#xvda2_avgwait.info Average wait time for an I/O request
#xvda2_avgwait.min 0
#xvda2_avgwait.draw LINE1

	def execute123(self):
		tree = self.tree

		for view in tree.xpath('/statistics/views/view'):
			view_name = view.get('name')

			print view_name

			qtypes = []
			for counter in view.xpath("counters[@type='resqtype']/counter"):
				qtypes.append((counter.get('name'), counter.text))
			print sorted(qtypes)


			qstats = []
			for counter in view.xpath("counters[@type='resstats']/counter"):
				qstats.append((counter.get('name'), counter.text))
			print sorted(qstats)


		print "--- EoV ---"		

		if False:
			for socket in tree.xpath('/statistics/socketmgr/sockets/socket'):
				attribs = [socket.xpath('id'), socket.xpath('name'),
							socket.xpath('references'), socket.xpath('type'),
							socket.xpath('local-address') ]

				x = []
				for foo in attribs:
					if foo and len(foo):
						x.append(foo[0].text.strip())
					else:
						x.append("\t")
				print "%s\t%s\t%s\t%s\t%s\t" % tuple(x)

		print "opcode counter:"
		for counter in tree.xpath("server/counters[@type='opcode']/counter"):
			print counter, counter.get('name').strip(), counter.text.strip()

		print "nsstat counter:"
		for counter in tree.xpath("server/counters[@type='nsstat']/counter"):
			print counter, counter.get('name').strip(), counter.text.strip()

		print "sockstat counter:"
		for counter in tree.xpath("server/counters[@type='sockstat']/counter"):
			print counter, counter.get('name').strip(), counter.text.strip()

	def execute(self):
		self._read()
		print self.views
		import pprint
		pprint.pprint(self.stats)

	@property
	def tree(self):
		if not getattr(self, '_tree', None):
			self._tree = etree.parse('/home/johann/bind2.txt.xml')
		return self._tree

	def _read(self):

		def _grab_values(xpath, parent=None):
			return sorted([(counter.get('name'), long(counter.text)) for counter in (parent or self.tree).xpath(xpath)]),

		self.views = {}
		for view in self.tree.xpath('/statistics/views/view'):
			self.views[view.get('name').strip()] = {
				'query_types': _grab_values("counters[@type='resqtype']/counter", view), #sorted([(counter.get('name'), long(counter.text)) for counter in view.xpath("counters[@type='resqtype']/counter")]),
				'result_stats': _grab_values("counters[@type='resstats']/counter", view) #sorted([(counter.get('name'), long(counter.text)) for counter in view.xpath("counters[@type='resstats']/counter")])
			}

		self.stats = {
			'opcodes': _grab_values("/statistics/server/counters[@type='opcode']/counter"),
			'query_types': _grab_values("/statistics/server/counters[@type='qtype']/counter"),
			'nsstat': _grab_values("/statistics/server/counters[@type='nsstat']/counter"),
			'zonestat': _grab_values("/statistics/server/counters[@type='zonestat']/counter"),
			'sockstat': _grab_values("/statistics/server/counters[@type='sockstat']/counter"),
		}



if __name__ == "__main__":
	Bind9Statchannel().run()
