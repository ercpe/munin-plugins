#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#%# family=auto
#%# capabilities=autoconf

import base64
import json
import os

from munin import MuninPlugin
import urllib2

class IcincaHealth(MuninPlugin):
	title = "Icinga health"
	args = '-l 0'

	@property
	def fields(self):
		return [
			("service_health", {
				'label': 'Service health',
				'max': 100.0,
				'min': 0,
				'type': 'GAUGE'
			}),
			("host_health", {
				'label': 'Host health',
				'max': 100.0,
				'min': 0,
				'type': 'GAUGE'
			})
		]

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

		data = json.loads(response)

		print("service_health.value %s" % data['tac']['tac_overview']['percent_service_health'])
		print("host_health.value %s" % data['tac']['tac_overview']['percent_host_health'])



if __name__ == "__main__":
	IcincaHealth().run()
