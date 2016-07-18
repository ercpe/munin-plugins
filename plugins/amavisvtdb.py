#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sqlite3
import sys
import hashlib

sql = """  select pattern, num_infected, num_clean, num_infected * 100 / (num_infected + num_clean) as infected_percent from (
	select DISTINCT
	  f.pattern,
	  (SELECT COUNT(*) FROM filenames f2 where f2.pattern = f.pattern and f2.infected = 1) as num_infected,
	  (SELECT COUNT(*) FROM filenames f2 where f2.pattern = f.pattern and f2.infected = 0) as num_clean
	from filenames f where f.pattern is not NULL order by num_infected DESC
  ) q where num_infected + num_clean > 10;"""


def config(dbfile):
	print("""graph_title AmavisVT patterns
graph_category antivirus
graph_args -l 0 --upper-limit 100""")

	conn = None

	try:
		conn = sqlite3.connect(dbfile)
		conn.text_factory = str

		cursor = conn.cursor()

		cursor.execute(sql)
		l = cursor.fetchall()

		for pattern, _, _, infected_percent in l:
			h = hashlib.md5()
			h.update(pattern)
			key = "pattern_%s" % h.hexdigest()

			print("%s.label %s" % (key, pattern))
			print("%s.type GAUGE" % (key, ))
			print("%s.info Percent infected of pattern '%s'" % (key, pattern))
	finally:
		if conn:
			try:
				conn.close()
			except:
				pass

def data(dbfile):
	conn = None

	try:
		conn = sqlite3.connect(dbfile)
		conn.text_factory = str

		cursor = conn.cursor()

		cursor.execute(sql)
		l = cursor.fetchall()

		for pattern, _, _, infected_percent in l:
			h = hashlib.md5()
			h.update(pattern)
			key = "pattern_%s" % h.hexdigest()

			print("%s.value %s" % (key, infected_percent))
	finally:
		if conn:
			try:
				conn.close()
			except:
				pass

dbfile = os.environ.get('database', '/var/lib/amavisvt/amavisvt.sqlite3')



if len(sys.argv) > 1 and sys.argv[1] == 'config':
	config(dbfile)
else:
	data(dbfile)
