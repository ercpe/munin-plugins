#!/usr/bin/env python
# -*- coding: utf-8 -*-
#%# family=auto
#%# capabilities=autoconf

from munin import MuninPlugin
from lxml import etree
from graphs import Multigraph, Graph
import os
import urllib2

class Bind9Statchannel(MuninPlugin):
	mg_prefix = "bind9_statchannel_"

	def config(self):
		for g in self._create_graphs():
			print g.get_config()

	def execute(self):
		for g in self._create_graphs():
			print g.get_values()

	def _sum_dicts(self, dicts):
		d = {}

		for x in dicts:
			for k, v in x.iteritems():
				d[k] = d.get(k, 0) + v

		return d

	def _create_graphs(self):
		# opcode graph
		opcode_graph = Multigraph("%sopcodes" % self.mg_prefix, 'OPCodes', category='bind9')
		for opcode, count in self.opcodes.iteritems():
			opcode_graph.add_row('opcode_%s' % opcode, opcode, type='COUNTER')
			opcode_graph.add_data('opcode_%s' % opcode, count)

		yield opcode_graph


		# server statistics graph
		nsstat_graph = Multigraph("%snsstat" % self.mg_prefix, 'Server Statistics', category='bind9',
								args="-l 0", vlabel='Usage (Queries / Second)')
		for k, v in sorted(self.nsstat.iteritems()):
			nsstat_graph.add_row(k, k, 'DERIVE', 'AREASTACK')
			nsstat_graph.add_data(k, v)

		yield nsstat_graph


		# socket statistics graph
		sockstat_graph = Multigraph("%ssockstat" % self.mg_prefix, 'Socket I/O Statistics', category='bind9',
								args="-l 0", vlabel='Derived Count')
		for k, v in sorted(self.sockstat.iteritems()):
			sockstat_graph.add_row(k, k, type='DERIVE', draw='AREASTACK', min=0)
			sockstat_graph.add_data(k, v)
		yield sockstat_graph


		# view graphs
		resq_graph = Multigraph("%sresqtypes" % self.mg_prefix, 'Queries', category='bind9',
							args='-l 0', vlabel="Queries / second")
		resstat_graph = Multigraph("%sresstat" % self.mg_prefix, 'Resolver statistics', category='bind9',
							args='-l 0', vlabel="Queries / second")
		cachedb_graph = Multigraph("%scachedb" % self.mg_prefix, 'CacheDB', category='bind9',
							args='-l 0', vlabel="Count")

		# sum the totals over all views for the overview graph
		resq_totals = self._sum_dicts([x[1]['resqtype'] for x in self.views])
		resstat_totals = self._sum_dicts([x[1]['resstats'] for x in self.views])
		cachedb_totals = self._sum_dicts([x[1]['cachedb'] for x in self.views])

		# finish overview graphs
		for k, v in sorted(resq_totals.iteritems()):
			resq_graph.add_row(k, k, type='DERIVE', draw='AREASTACK', min=0)
			resq_graph.add_data(k, v)

		for k, v in sorted(resstat_totals.iteritems()):
			resstat_graph.add_row(k, k, type='DERIVE', draw='AREASTACK', min=0)
			resstat_graph.add_data(k, v)

		for k, v in sorted(cachedb_totals.iteritems()):
			cachedb_graph.add_row(k, k, type='DERIVE', draw='AREASTACK', min=0)
			cachedb_graph.add_data(k, v)

		for view_name, stats in self.views:
			q_graph = Graph("Queries for view '%s'" % view_name, category='bind9', args='-l 0')
			for k, v in sorted(stats['resqtype'].iteritems()):
				q_graph.add_row(k, k, type='DERIVE', draw='AREASTACK')
				q_graph.add_data(k, v)
			resq_graph.add_subgraph("%sresqtypes.%s" % (self.mg_prefix, view_name), q_graph)

			r_graph = Graph("Resolver statistics for view '%s'" % view_name, category='bind9', args='-l 0')
			for k, v in sorted(stats['resstats'].iteritems()):
				r_graph.add_row(k, k, type='DERIVE', draw='AREASTACK')
				r_graph.add_data(k, v)
			resq_graph.add_subgraph("%sresstat.%s" % (self.mg_prefix, view_name), r_graph)

			cdb_graph = Graph("Cache DB for view '%s'" % view_name, category='bind9', args='-l 0')
			for k, v in sorted(stats['cachedb'].iteritems()):
				cdb_graph.add_row(k, k, type='DERIVE', draw='AREASTACK')
				cdb_graph.add_data(k, v)
			cachedb_graph.add_subgraph("%scachedb.%s" % (self.mg_prefix, view_name), cdb_graph)

		yield resq_graph
		yield resstat_graph
		yield cachedb_graph

		# memory graph with total and inuse values
		mem_graph = Multigraph("%smemory" % self.mg_prefix, 'Memory usage', category='bind9',
							args="-l 0 --base 1024", vlabel="Memory in use")
		for k, v in self.memory:
			if k == "TotalUse":
				mem_graph.add_row(k, k, draw='LINE1', type='DERIVE', min=0)
			else:
				mem_graph.add_row(k, k, draw='AREASTACK')
			mem_graph.add_data(k, v)
		yield mem_graph


	@property
	def tree(self):
		if not getattr(self, '_tree', None):
			if os.environ.get('debug_file'):
				self._tree = etree.parse(os.environ.get('debug_file'))
			else:
				r = urllib2.urlopen(os.environ.get('url', 'http://localhost:8053'))
				self._tree = etree.parse(r)
		return self._tree

	@property
	def nsstat(self):
		return self._get_counters("/statistics/server/counters[@type='nsstat']/counter",
					['QryRecursion', 'QryNxrrset', 'Requestv4', 'Requestv6', 'Response',
					'QrySuccess', 'QryAuthAns', 'QryNoauthAns', 'QryNXDOMAIN', 'RespEDNS0'])

	@property
	def sockstat(self):
		return self._get_counters("/statistics/server/counters[@type='sockstat']/counter",
					['UDP4Open', 'UDP6Open', 'TCP4Open', 'TCP6Open', 'UDP4Close', 'UDP6Close',
					'TCP4Close', 'TCP6Close', 'UDP4Conn', 'UDP6Conn', 'TCP4Conn', 'TCP6Conn',
					'TCP4Accept', 'TCP6Accept', 'TCP6SendErr', 'UDP4RecvErr', 'UDP6RecvErr', 'TCP4RecvErr', 'TCP6RecvErr']
				)

	@property
	def memory(self):
		return [(x.tag, long(x.text)) for x in self.tree.xpath('/statistics/memory/summary/*')]

	@property
	def opcodes(self):
		return self._get_counters("/statistics/server/counters[@type='opcode']/counter")

	@property
	def views(self):
		if not getattr(self, '_views', None):
			self._views = []
			for view in self.tree.xpath('/statistics/views/view'):
				view_name = view.get('name').strip()
				if view_name == "_bind":
					continue

				self._views.append((view_name, {
							'resqtype': self._get_counters("counters[@type='resqtype']/counter", None, view),
							'resstats': self._get_counters("counters[@type='resstats']/counter", None, view),
							'cachedb': dict([(x.xpath('name')[0].text, long(x.xpath('counter')[0].text))
											for x in view.xpath("cache/rrset")]),
						}))
		return self._views


	def _get_counters(self, xpath, items=None, parent=None):
		parent = parent if parent is not None else self.tree

		counters = [(n.get('name'), long(n.text)) for n in parent.xpath(xpath)]
		l = filter(lambda item: not items or item[0] in items, counters)

		return dict(l)

if __name__ == "__main__":
	Bind9Statchannel().run()

