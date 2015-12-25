#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import re
import subprocess
import shlex
import tempfile

from collections import OrderedDict

from munin import MuninPlugin

tests_re = re.compile(r"tests=\[(.*?)\]", flags=re.IGNORECASE)

class SpamassassinRuleHitsPlugin(MuninPlugin):
	title = "Spamassassin rule hits"
	category = 'mail'
	vlabel = 'Hits'

	@property
	def fields(self):
		def _inner():
			t = tempfile.mktemp()
			for k in self.get_data(t).keys():
				yield (k, {
					'label': k,
					'min': 0,
					'type': 'GAUGE',
					'info': 'Number of hits of rule %s' % k,
				})
			os.remove(t)
		return list(_inner())

	def get_data(self, state_file):
		logfile = os.environ.get('logfile', '/var/log/mail.log')
		logtail = os.environ.get('logtail', '/usr/bin/logtail')

		logtail_cmd = "%s %s %s" % (logtail, logfile, state_file)

		logtail_proc = subprocess.Popen(shlex.split(logtail_cmd), stdout=subprocess.PIPE)
		grep_proc = subprocess.Popen(shlex.split("grep 'spam_scan: score='"), stdin=logtail_proc.stdout, stdout=subprocess.PIPE)
		logtail_proc.stdout.close()

		stdout, _ = grep_proc.communicate()

		d = {}

		for line in stdout.splitlines():
			tests_m = tests_re.search(line)
			if not tests_m:
				continue

			chunks = [x.strip() for x in tests_m.group(1).split(',')]
			for c in chunks:
				if '=' not in c:
					continue
				name, _ = c.split('=')
				d[name] = d.get(name, 0) + 1

		return OrderedDict(sorted(d.items(), key=lambda t: t[0]))

	def execute(self):
		state_file = os.environ.get('state_file', '/var/lib/munin/plugin-state/%s.offset' % os.path.basename(__file__))
		for k, v in self.get_data(state_file).items():
			print("%s.value %s" % (k, v))


if __name__ == '__main__':
	SpamassassinRuleHitsPlugin().run()