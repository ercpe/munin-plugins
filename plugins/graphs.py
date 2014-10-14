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
		return self

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
