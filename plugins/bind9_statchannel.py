#!/usr/bin/env python
# -*- coding: utf-8 -*-
#%# family=auto
#%# capabilities=autoconf

from munin import MuninPlugin
from lxml import etree
from graphs import Multigraph, Graph

class Bind9Statchannel(MuninPlugin):
	mg_prefix = "bind9_statchannel_"

	def config(self):
		for g in self._create_graphs():
			print g.get_config()

	def execute(self):
		for g in self._create_graphs():
			print g.get_values()

	def _create_graphs(self):
		#self._read()

#		# combined graph for the host overview - contains the aggregated values for all views
#		query_types_graph = Multigraph("%sqtypes" % self.mg_prefix, 'Query types', category="bind9")
#		qtypes = {}
#
#		# sum up all query types and counts over all views
#		for view_name, view_stats in self.views.iteritems():
#			# create a subgraph definition for this view
#			vg = Graph("Query types for view '%s'" % view_name, category='bind9')
#
#			for qtype, count in view_stats['query_types']:
#				# sum up the totals for the overview graph
#				qtypes[qtype] = qtypes.get(type, 0) + count
#
#				# add a row + data to the graph for the current view
#				vg.add_row('qtype_%s' % qtype, qtype, type='COUNTER', draw='AREASTACK')
#				vg.add_data('qtype_%s' % qtype, count)
#
#			query_types_graph.add_subgraph("%sqtypes.%s" % (self.mg_prefix, view_name), vg)
#
#
#		# finish the graph definition for the overview graph
#		for qtype, total_count in qtypes.iteritems():
#			query_types_graph.add_row('qtype_%s' % qtype, qtype, type='COUNTER', draw='AREASTACK')
#			query_types_graph.add_data('qtype_%s' % qtype, total_count)
#
#		yield query_types_graph
#
#
#		result_graph = Multigraph("%srstats" % self.mg_prefix, 'Result stats', category="bind9")
#		rstats = {}
#		# sum up all result types and counts over all views
#		for view_name, view_stats in self.views.iteritems():
#			# create a subgraph definition for this view
#			vg = Graph("Result stats for view '%s'" % view_name, category='bind9')
#
#			for atype, count in view_stats['result_stats']:
#				# sum up the totals for the overview graph
#				rstats[atype] = rstats.get(type, 0) + count
#
#				# add a row + data to the graph for the current view
#				vg.add_row('rstat_%s' % atype, atype, type='COUNTER', draw='AREASTACK')
#				vg.add_data('rstat_%s' % atype, count)
#
#			result_graph.add_subgraph("%srstats.%s" % (self.mg_prefix, view_name), vg)
#
#
#		# finish the graph definition for the overview graph
#		for atype, total_count in rstats.iteritems():
#			result_graph.add_row('rstat_%s' % atype, atype, type='COUNTER', draw='AREASTACK')
#			result_graph.add_data('rstat_%s' % atype, total_count)
#
#		yield result_graph
#
#
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

		resq_totals = {}
		resstat_totals = {}

		# sum the totals over all views for the overview graph
		for view_name, stats in self.views:
			for k, v in stats['resqtype'].iteritems():
				resq_totals[k] = resq_totals.get(k, 0) + v
			for k, v in stats['resstats'].iteritems():
				resstat_totals[k] = resstat_totals.get(k, 0) + v

		# finish overview graphs
		for k, v in sorted(resq_totals.iteritems()):
			resq_graph.add_row(k, k, type='DERIVE', draw='AREASTACK', min=0)
			resq_graph.add_data(k, v)

		for k, v in sorted(resstat_totals.iteritems()):
			resstat_graph.add_row(k, k, type='DERIVE', draw='AREASTACK', min=0)
			resstat_graph.add_data(k, v)

		for view_name, stats in self.views:
			q_graph = Graph("Queries for view '%s'" % view_name, category='bind9', args='-l 0')
			for k, v in sorted(stats['resqtype'].iteritems()):
				q_graph.add_row(k, k, type='DERIVE', draw='AREASTACK')
				q_graph.add_data(k, v)

			r_graph = Graph("Resolver statistics for view '%s'" % view_name, category='bind9', args='-l 0')
			for k, v in sorted(stats['resstats'].iteritems()):
				r_graph.add_row(k, k, type='DERIVE', draw='AREASTACK')
				r_graph.add_data(k, v)

			resq_graph.add_subgraph("%sresqtypes.%s" % (self.mg_prefix, view_name), q_graph)
			resq_graph.add_subgraph("%sresstat.%s" % (self.mg_prefix, view_name), r_graph)

		yield resq_graph
		yield resstat_graph


	@property
	def tree(self):
		if not getattr(self, '_tree', None):
			self._tree = etree.parse('/home/johann/Desktop/bind-auto.xml')
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
							#'cache': self._get_counters("counters[@type='resstats']/counter", None, view),
						}))
		return self._views


	def _get_counters(self, xpath, items=None, parent=None):
		parent = parent if parent is not None else self.tree

		counters = [(n.get('name'), long(n.text)) for n in parent.xpath(xpath)]
		l = filter(lambda item: not items or item[0] in items, counters)

		return dict(l)

	def _read(self):
		pass
#		def _grab_values(xpath, parent=None):
#			return sorted([
#						(counter.get('name'), long(counter.text))
#							for counter in (parent if parent is not None else self.tree).xpath(xpath)
#					])

#		self.views = {}
#		for view in self.tree.xpath('/statistics/views/view'):
#			view_name = view.get('name').strip()
#			#if view_name == "_bind":
#			#	continue # no usable infos here?
#
#			self.views[view_name] = {
#				'query_types': _grab_values("counters[@type='resqtype']/counter", view),
#				'result_stats': _grab_values("counters[@type='resstats']/counter", view)
#			}
#
#		self.stats = {
#			'opcodes': _grab_values("/statistics/server/counters[@type='opcode']/counter"),
#			'query_types': _grab_values("/statistics/server/counters[@type='qtype']/counter"),
#			'nsstat': _grab_values("/statistics/server/counters[@type='nsstat']/counter"),
#			'zonestat': _grab_values("/statistics/server/counters[@type='zonestat']/counter"),
#			'sockstat': _grab_values("/statistics/server/counters[@type='sockstat']/counter"),
#		}



if __name__ == "__main__":
	Bind9Statchannel().run()

