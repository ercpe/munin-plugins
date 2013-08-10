# -*- coding: utf-8 -*-

class Graph(object):
	'''
	Represents a munin graph definition
	'''

	def __init__(self, title, **kwargs):
		kwargs['title'] = title
		self.graph_args = kwargs
		self.rows = {}
		self.data = {}

	def add_row(self, name, label, type="GAUGE", draw="LINE1", **kwargs):
		d = kwargs
		d['label'] = label
		d['type'] = type
		d['draw'] = draw
		self.rows[name] = d

	def add_data(self, name, value):
		if not name in self.rows:
			raise Exception("Got value for an undefined data row!")

		self.data[name] = value

	def get_config(self):
		l = []
		for t in self.graph_args.iteritems():
			l.append("graph_%s %s" % t)

		for row_name, options in sorted(self.rows.iteritems()):
			for k, v in options.iteritems():
				l.append("%s.%s %s" % (row_name, k, v))

		return '\n'.join(l)

	def get_values(self):
		return '\n'.join(["%s.value %s" % t for t in sorted(self.data.iteritems())])


class Multigraph(Graph):
	"""
	Represents a munin multigraph definition
	"""

	def __init__(self, name, *args, **kwargs):
		super(Multigraph, self).__init__(*args, **kwargs)
		self.name = name
		self.subgraphs = {}

	def add_subgraph(self, name, graph):
		self.subgraphs[name] = graph

	def get_config(self):
		s = "multigraph %s\n%s\n\n" % (self.name, Graph.get_config(self))

		for name, graph in self.subgraphs.iteritems():
			s += "multigraph %s\n%s\n\n" % (name, graph.get_config())

		return s.strip()

	def get_values(self):
		s = "multigraph %s\n" % self.name
		s += super(Multigraph, self).get_values() + "\n"
		for name, sg in self.subgraphs.iteritems():
			s += "multigraph %s\n" % name
			s += sg.get_values() + "\n"
		return s.strip()


if __name__ == "__main__":

	g = Graph('My funky graph', graph_category='Misc')
	g.add_row('test1', label='Sample value for test1')
	g.add_row('test2', label='Sample value for test2')

	g.add_data('test1', 2)
	g.add_data('test2', 6)

	#print g.get_config()
	#print g.get_values()

	mg = Multigraph('web_mg', 'Funky multigraph', graph_category='Webserver')
	mg.add_row('avg_static_hits', 'Avg. hits to static files')
	mg.add_row('avg_dynamic_hits', 'Avg. hits to dynamic content')
	mg.add_data('avg_static_hits', 10)
	mg.add_data('avg_dynamic_hits', 20)

	g1 = Graph('Accesses to Webserver Web1')
	g1.add_row('static_hits', 'Hits on static files')
	g1.add_data('static_hits', 100)
	g1.add_row('dynamic_hits', 'Hits on dynamic files')
	g1.add_data('dynamic_hits', 10)
	mg.add_subgraph('web_mg.web1', g1)

	g2 = Graph('Accesses to Webserver Web2')
	g2.add_row('static_hits', 'Hits on static files')
	g2.add_data('static_hits', 1000)
	g2.add_row('dynamic_hits', 'Hits on dynamic files')
	g2.add_data('dynamic_hits', 100)
	mg.add_subgraph('web_mg.web2', g2)

	print mg.get_config()
	print "-----"
	print mg.get_values()


#		print """multigraph bind9_mg_test
#graph_title Multigraph test
#graph_args --base 1000
#graph_vlabel Average Test
#graph_category bind9
#
#suba_avg.label SubA
#suba_avg.type GAUGE
#suba_avg.min 0
#suba_avg.draw LINE1

#subb_avg.label SubB
#subb_avg.type GAUGE
#subb_avg.min 0
#subb_avg.draw LINE1
#"""


#		print """multigraph bind9_mg_test.subb
#graph_title Values for SubB
#graph_args --base 1000
#graph_vlabel numbers
#graph_category bind9
#
#slot1.label Data Row 1
#slot1.type GAUGE
#slot1.min 0
#slot1.draw LINE1
#slot2.label Data Row 2
#slot2.type GAUGE
#slot2.min 0
#slot2.draw LINE1
#"""
