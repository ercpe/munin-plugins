# -*- coding: utf-8 -*-
import json

from munin import MuninPlugin

import os
import sys

class MemorableMuninPlugin(MuninPlugin):

	@property
	def plugin_state_file(self):
		basedir = os.environ.get('state_dir', '/var/lib/munin/plugin-state/')
		return os.path.join(basedir, os.path.basename(sys.argv[0]))

	def load_state(self, default=None):
		try:
			with open(self.plugin_state_file, 'r') as f:
				return json.load(f)
		except (IOError, ValueError):
			pass
		return default

	def save_state(self, data):
		with open(self.plugin_state_file, 'w') as f:
			return json.dump(data, f)
