#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import socket
import re

SOCKET_PATH = os.environ.get('socketpath', '/run/rrdcached.sock')

if len(sys.argv) > 1 and sys.argv[1] == 'config':
	print """graph_title rrdcached stats
graph_category rrdcached
QueueLength.label Queue length
QueueLength.info Number of nodes currently enqueued in the update queue.
UpdatesReceived.label Update commands received
UpdatesReceived.type DERIVE
UpdatesReceived.info Number of UPDATE commands received.
FlushesReceived.label Flush command received
FlushesReceived.type DERIVE
FlushesReceived.info Number of FLUSH commands received.
UpdatesWritten.label Updates written
UpdatesWritten.type DERIVE
UpdatesWritten.info Total number of updates, i. e. calls to rrd_update_r, since the daemon was started.
DataSetsWritten.label DataSets written
DataSetsWritten.type DERIVE
DataSetsWritten.info Total number of "data sets" written to disk since the daemon was started.
TreeNodesNumber.label Number of tree nodes
TreeNodesNumber.info Number of nodes in the cache.
TreeDepth.label Tree depth
TreeDepth.info Depth of the tree used for fast key lookup.
JournalBytes.label Total journal bytes written
JournalBytes.type DERIVE
JournalBytes.info Total number of bytes written to the journal since startup.
JournalRotate.label Journal rotated
JournalRotate.type DERIVE
JournalRotate.info Number of times the journal has been rotated since startup."""
else:
	sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
	sock.connect(SOCKET_PATH)
	sock.send("STATS\n")

	data = sock.recv(4096)
	for line in [x.strip() for x in data.splitlines() if ':' in x]:
		m = re.match("(.*): (\d+)", line, re.IGNORECASE)
		print("%s.value %s" % m.groups())

	sock.close()