#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#%# family=auto
#%# capabilities=autoconf

import base64
import json
import os

from munin import MuninPlugin
import urllib2
from graphs import Multigraph


class IcincaMulti(MuninPlugin):

	@property
	def graph_defs(self):
		return {
			'health': Multigraph('icinga_health', 'Icinga health', category='Icinga', args='-l 0') \
						.add_row('service_health', 'Service health', 'GAUGE', min=0.0, max=100.0) \
						.add_row('host_health', 'Host health', 'GAUGE', min=0.0, max=100.0),
			'host_exec_time': Multigraph('icinga_host_execution_time', 'Icinga host check execution time', category='Icinga') \
						.add_row('min_host_exec_time', 'Minimum host check execution time', 'GAUGE', min=0) \
						.add_row('avg_host_exec_time', 'Average host check execution time', 'GAUGE', min=0) \
						.add_row('max_host_exec_time', 'Maximum host check execution time', 'GAUGE', min=0),
			'service_exec_time': Multigraph('icinga_service_execution_time', 'Icinga service check execution time', category='Icinga') \
						.add_row('min_service_exec_time', 'Minimum service check execution time', 'GAUGE', min=0) \
						.add_row('avg_service_exec_time', 'Average service check execution time', 'GAUGE', min=0) \
						.add_row('max_service_exec_time', 'Maximum service check execution time', 'GAUGE', min=0),
			'host_check_latency': Multigraph('icinga_host_check_latency', 'Icinga host check latency', category='Icinga') \
						.add_row('min_host_check_latency', 'Minimum host check latency', 'GAUGE', min=0) \
						.add_row('avg_host_check_latency', 'Average host check latency', 'GAUGE', min=0) \
						.add_row('max_host_check_latency', 'Maximum host check latency', 'GAUGE', min=0),
			'service_check_latency': Multigraph('icinga_service_check_latency', 'Icinga service check latency', category='Icinga') \
						.add_row('min_service_check_latency', 'Minimum service check latency', 'GAUGE', min=0) \
						.add_row('avg_service_check_latency', 'Average service check latency', 'GAUGE', min=0) \
						.add_row('max_service_check_latency', 'Maximum service check latency', 'GAUGE', min=0),
		}

	def config(self):
		for _, x in self.graph_defs.items():
			print(x.get_config())

	def execute(self):
		tac_url = os.environ['tac_url']
		user = os.environ.get('user', None)
		password = os.environ.get('password', None)

		r = urllib2.Request("%s?jsonoutput" % tac_url)
		r.add_header('Accept', 'text/json,application/json;q=0.9,*/*;q=0.1')
		r.add_header('User-Agent', 'munin-plugin icinga health/0.1')

		if user and password:
			r.add_header('Authorization', 'Basic ' + base64.encodestring("%s:%s" % (user, password)))

		response = urllib2.urlopen(r).read()
		data = json.loads(response)['tac']['tac_overview']

		graphs = self.graph_defs
		graphs['health'].add_data('service_health', data['percent_service_health'])
		graphs['health'].add_data('host_health', data['percent_host_health'])

		graphs['host_exec_time'].add_data('min_host_exec_time', data['min_host_check_execution_time'])
		graphs['host_exec_time'].add_data('avg_host_exec_time', data['average_host_check_execution_time'])
		graphs['host_exec_time'].add_data('max_host_exec_time', data['max_host_check_execution_time'])
		graphs['service_exec_time'].add_data('min_service_exec_time', data['min_service_check_execution_time'])
		graphs['service_exec_time'].add_data('avg_service_exec_time', data['average_service_check_execution_time'])
		graphs['service_exec_time'].add_data('max_service_exec_time', data['max_service_check_execution_time'])
		graphs['host_check_latency'].add_data('min_host_check_latency', data['min_host_check_latency'])
		graphs['host_check_latency'].add_data('avg_host_check_latency', data['average_host_check_latency'])
		graphs['host_check_latency'].add_data('max_host_check_latency', data['max_host_check_latency'])
		graphs['service_check_latency'].add_data('min_service_check_latency', data['min_service_check_latency'])
		graphs['service_check_latency'].add_data('avg_service_check_latency', data['average_service_check_latency'])
		graphs['service_check_latency'].add_data('max_service_check_latency', data['max_service_check_latency'])

		for _, x in graphs.items():
			print(x.get_values())


if __name__ == "__main__":
	IcincaMulti().run()
