#!/usr/bin/env python
# -*- coding: utf-8 -*-
#%# family=auto
#%# capabilities=autoconf

from munin import MuninPlugin
from lxml import etree
from graphs import Multigraph, Graph
import os

class Bind9Statchannel(MuninPlugin):
	mg_prefix = "bind9_statchannel_"

	def config(self):
		for g in self._create_graphs():
			print g.get_config()

	def execute(self):
		for g in self._create_graphs():
			print g.get_values()

	def _create_graphs(self):
		self._read()

		# combined graph for the host overview - contains the aggregated values for all views
		query_types_graph = Multigraph("%sqtypes" % self.mg_prefix, 'Query types', category="bind9")
		qtypes = {}

		# sum up all query types and counts over all views
		for view_name, view_stats in self.views.iteritems():
			# create a subgraph definition for this view
			vg = Graph("Query types for view '%s'" % view_name, category='bind9')

			for qtype, count in view_stats['query_types']:
				# sum up the totals for the overview graph
				qtypes[qtype] = qtypes.get(type, 0) + count

				# add a row + data to the graph for the current view
				vg.add_row('qtype_%s' % qtype, qtype, type='COUNTER', draw='AREASTACK')
				vg.add_data('qtype_%s' % qtype, count)

			query_types_graph.add_subgraph("%sqtypes.%s" % (self.mg_prefix, view_name), vg)


		# finish the graph definition for the overview graph
		for qtype, total_count in qtypes.iteritems():
			query_types_graph.add_row('qtype_%s' % qtype, qtype, type='COUNTER', draw='AREASTACK')
			query_types_graph.add_data('qtype_%s' % qtype, total_count)

		yield query_types_graph


		# opcode graph
		opcode_graph = Multigraph("%sopcodes" % self.mg_prefix, 'OPCodes', category='bind9')
		i = 0
		for opcode, count in self.stats['opcodes']:
			opcode_graph.add_row('opcode_%s' % opcode, opcode, type='COUNTER')
			opcode_graph.add_data('opcode_%s' % opcode, count)
			i += 1

		yield opcode_graph


	@property
	def tree(self):
		if not getattr(self, '_tree', None):
			self._tree = etree.parse('/home/johann/Desktop/bind-auto.xml')
		return self._tree

	def _read(self):
		def _grab_values(xpath, parent=None):
			return sorted([
						(counter.get('name'), long(counter.text))
							for counter in (parent if parent is not None else self.tree).xpath(xpath)
					])

		self.views = {}
		for view in self.tree.xpath('/statistics/views/view'):
			view_name = view.get('name').strip()
			if view_name == "_bind":
				continue # no usable infos here?

			self.views[view_name] = {
				'query_types': _grab_values("counters[@type='resqtype']/counter", view),
				'result_stats': _grab_values("counters[@type='resstats']/counter", view)
			}

		self.stats = {
			'opcodes': _grab_values("/statistics/server/counters[@type='opcode']/counter"),
			'query_types': _grab_values("/statistics/server/counters[@type='qtype']/counter"),
			'nsstat': _grab_values("/statistics/server/counters[@type='nsstat']/counter"),
			'zonestat': _grab_values("/statistics/server/counters[@type='zonestat']/counter"),
			'sockstat': _grab_values("/statistics/server/counters[@type='sockstat']/counter"),
		}



if __name__ == "__main__":
	if os.environ.get('FOOBAR', None):
		x = Bind9Statchannel()
		x._read()
		import pprint
		pprint.pprint(x.views)
	Bind9Statchannel().run()

