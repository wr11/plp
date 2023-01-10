from pubdefines import SERVER_DIR

import os
import queue
import onlinereload.reloader as reloader
import sys
import threading
import time
import conf

_win32 = (sys.platform == 'win32')


def _normalize_filename(filename):
	if filename is not None:
		if filename.endswith('.pyc') or filename.endswith('.pyo'):
			filename = filename[:-1]
		elif filename.endswith('$py.class'):
			filename = filename[:-9] + '.py'
	return filename


class ModuleMonitor(threading.Thread):
	"""Monitor module source file changes"""

	def __init__(self, interval=1, auto=False):
		threading.Thread.__init__(self)
		self.daemon = True
		self.mtimes = {}
		self.queue = queue.Queue()
		self.interval = interval
		self.auto = auto

	def run(self):
		while True:
			self._scan()
			time.sleep(self.interval)

	def _scan(self):
		from importlib import import_module, reload
		moduledict = {}
		if self.auto:
			moduledict = dict(sys.modules)
		else:
			mod = import_module("onlinereload.reloadbox")
			newmod = reload(mod)
			modulenames = getattr(newmod, "MODULE_LIST", [])
			for modulename in modulenames:
				module = import_module(modulename)
				if not module:
					continue
				moduledict[modulename] = module
		if not moduledict:
			return

		change = False
		for modulename, module in moduledict.items():
			# We're only interested in file-based modules (not C extensions).
			filename = getattr(module, '__file__', None)
			if filename is None:
				continue
			# We're only interested in the files in our project.
			if SERVER_DIR not in filename:
				continue
			# We're only interested in the source .py files.
			filename = _normalize_filename(filename)

			# stat() the file.  This might fail if the module is part of a
			# bundle (.egg).  We simply skip those modules because they're
			# not really reloadable anyway.
			try:
				stat = os.stat(filename)
			except OSError:
				continue

			# Check the modification time.  We need to adjust on Windows.
			mtime = stat.st_mtime
			if _win32:
				mtime -= stat.st_ctime

			# Check if we've seen this file before.  We don't need to do
			# anything for new files.
			if filename in self.mtimes:
				# If this file's mtime has changed, queue it for reload.
				if mtime != self.mtimes[filename]:
					change = True
					self.queue.put(modulename)

			# Record this filename's current mtime.
			self.mtimes[filename] = mtime
		
		if change:
			g_Reloader.poll()


class Reloader(object):

	def __init__(self, interval=1, auto=False):
		self.monitor = ModuleMonitor(interval=interval, auto=auto)
		self.monitor.start()

	def poll(self):
		modulenames = set()
		while not self.monitor.queue.empty():
			try:
				modulenames.add(self.monitor.queue.get_nowait())
			except queue.Empty:
				break
		if modulenames:
			self._reload(modulenames)

	def _reload(self, modulenames):
		for modulename in modulenames:
			mod = sys.modules.get(modulename, None)
			if not mod:
				continue
			reloader.reload(mod)

if "g_Reloader" not in globals():
	g_Reloader = None

def Init():
	global g_Reloader
	if not conf.IsReloadOpen():
		g_Reloader = None
		return
	if conf.IsAutoReloadOpen():
		iInterval = conf.GetAutoReloadInterval()
		g_Reloader = Reloader(iInterval, True)
	elif conf.IsManualReloadOpen():
		iInterval = conf.GetManualReloadInterval()
		g_Reloader = Reloader(iInterval, False)