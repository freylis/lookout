#!/usr/bin/env python

import flask, os, sys, time, psutil, json, socket
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop

if getattr(sys, 'frozen', None):
	static = os.path.join(sys._MEIPASS, 'static')
else:
	static = 'static'

app = flask.Flask(__name__, static_folder=static)
PORT = 9890

@app.route('/')
def frontend():
	total_cpu = psutil.cpu_percent
	mem = psutil.virtual_memory()
	print mem.available
	return flask.send_from_directory(app.static_folder, 'index.html')

@app.route('/raw')
def raw():
	diskused = 0
	disktotal = 0
	for i in psutil.disk_partitions():
		try:
			x = psutil.disk_usage(i.mountpoint)
			diskused += x.used
			disktotal += x.total
		except OSError:
			pass
	o = json.dumps({
		'uptime':	time.time() - psutil.BOOT_TIME,
		'fqdn':		socket.getfqdn(),
		'cpuusage':	psutil.cpu_percent(0),
		'ramusage':	psutil.virtual_memory(),
		'diskio':	psutil.disk_io_counters(),
		'diskusage':	[diskused, disktotal],
		'netio':	psutil.network_io_counters(),
		'swapusage':	psutil.swap_memory()
	})
	return flask.Response(o, mimetype='application/json')

if __name__ == '__main__':
	if len(sys.argv) > 1:
		PORT = sys.argv[1]
	server = HTTPServer(WSGIContainer(app))
	print 'Now listening on port ' + str(PORT)
	server.listen(PORT)
	IOLoop.instance().start()
