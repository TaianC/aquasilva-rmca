"""
# AquaSilva Remote Monitoring and Control Application (AquaSilva RMCA), v1.1
# Made by Taian Chen
"""

try:
	print("[INFO]: Starting imports...")
	from subprocess import call
	from subprocess import Popen
	from time import sleep
	from time import strftime
	from time import gmtime
	# AES + RSA-based encryption was not finished, and sections using it were commented out.
	# from Cryptodome.PublicKey import RSA
	# from Cryptodome import Random
	# from Cryptodome.Cipher import AES
	from Cryptodome.Cipher import Salsa20
	from Cryptodome.Hash import HMAC
	from Cryptodome.Hash import SHA256
	from Cryptodome.Hash import MD5
	import socket
	import configparser
	from sys import exit as app_end
	import multiprocessing
	import tkinter
	from tkinter import messagebox
	from ast import literal_eval
	import ping3
	from platform import system
	import pickle
	# import hashlib
	from random import randint
except ImportError as e:
	sleep = None
	Popen = None
	strftime = None
	gmtime = None
	tkinter = None
	messagebox = None
	call = None
	Salsa20 = None
	HMAC = None
	SHA256 = None
	socket = None
	configparser = None
	MD5 = None
	app_end = None
	multiprocessing = None
	literal_eval = None
	ping3 = None
	system = None
	# RSA = None
	# AES = None
	# Random = None
	# hashlib = None
	pickle = None
	randint = None
	print("[FAIL]: Imports failed! See below.")
	print(e)
except ImportWarning as e:
	print("[FAIL]: Import warnings were raised! Please proceed with caution, see below for more details.")
	print(e)
pass

class client:
	"""Main class."""
	def __init__(self):
		"""Initiation function of AquaSilva RMCA."""
		print("[INFO]: Starting client AquaSilva RCM Application...")
		print("[INFO]: Declaring variables...")
		# AES + RSA-based encryption was not finished, and sections using it were commented out.
		# self.key = None
		# self.private = None
		# self.public = None
		self.socket = None
		self.host = ""
		self.port = 64220
		self.connect_retries = 0
		self.auth = ""
		self.ping_text = None
		self.ping_button = None
		self.ping_results = ""
		self.report_content = ""
		self.sensor_content = ""
		self.operation_status = 0
		self.state_valve_outlet = False
		self.state_valve_inlet = False
		self.state_light = False
		self.state_light_level = 0
		print("[INFO]: Loading configurations...")
		config_parse_load = configparser.ConfigParser()
		try:
			config_parse_load.read("main.cfg")
			self.host = config_parse_load["NET"]["ip"]
			self.port = config_parse_load["NET"]["port"]
			self.port = int(self.port)
			raw_key = config_parse_load["ENCRYPT"]["key"]
			raw_key_hash = MD5.new(raw_key.encode(encoding = "ascii", errors = "replace"))
			self.key = raw_key_hash.hexdigest()
			self.key = self.key.encode(encoding = "ascii", errors = "replace")
			self.hmac_key = config_parse_load["ENCRYPT"]["hmac_key"]
			self.auth = config_parse_load["ENCRYPT"]["auth"]
			self.auth = self.auth.encode(encoding = "ascii", errors = "replace")
			self.random_refresh = config_parse_load["OPT"]["random_refresh"]
		except configparser.Error as ce:
			print("[FAIL]: Failed to load configurations! See below for details.")
			print(ce)
		except FileNotFoundError:
			print("[FAIL]: Failed to load configurations! Configuration file is missing.")
		pass
		print("[INFO]: Starting background tasks...")
		# self.task_vitals_refresh = client.create_process(client.vitals_refresh, self)
		print("[INFO]: Starting GUI...")
		self.root = tkinter.Tk()
		self.root.title("AquaSilva RCMA: Client")
		self.root.configure(bg = "#344561")
		self.root.geometry('{}x{}'.format(765, 530))
		self.root.resizable(width = False, height = False)
		menu = tkinter.Menu(self.root)
		self.root.config(menu = menu)
		app_menu = tkinter.Menu(menu)
		app_menu.add_command(label = "Edit Configs", command = lambda: client.set_configuration_gui())
		app_menu.add_command(label = "Exit", command = lambda: client.exit(0))
		menu.add_cascade(label = "App", menu = app_menu)
		net_menu = tkinter.Menu(menu)
		net_tools_menu = tkinter.Menu(net_menu)
		net_tools_menu.add_command(label = "Ping", command = lambda: client.ping_gui(self))
		net_menu.add_cascade(label = "Tools", menu = net_tools_menu)
		menu.add_cascade(label = "Net", menu = net_menu)
		addon_menu = tkinter.Menu(menu)
		menu.add_cascade(label = "Add-Ons", menu = addon_menu)
		vitals_frame = tkinter.Frame(self.root, bg = "#506a96", highlightthickness = 2, bd = 0, height = 50, width = 60)
		vitals_frame.grid(row = 0, column = 0, padx = (10, 0), pady = (15, 0))
		vitals_label = tkinter.Label(vitals_frame, bg = "#506a96", fg = "white", text = "Status", font = ("Calibri", 12))
		vitals_label.grid(row = 0, column = 0, padx = (5, 0))
		self.vitals_text = tkinter.Text(vitals_frame, bg = "white", fg = "black", state = tkinter.DISABLED, height = 10, width = 50, font = ("Calibri", 10))
		self.vitals_text.grid(row = 1, column = 0, padx = (5, 5), pady = (10, 0))
		vitals_refresh_button = tkinter.Button(vitals_frame, text = "Refresh", bg = "white", fg = "black", command = lambda: client.vitals_refresh(self))
		vitals_refresh_button.grid(row = 2, column = 0, padx = (5, 5), pady = (10, 5))
		sensor_frame = tkinter.Frame(self.root, bg = "#506a96", highlightthickness = 2, bd = 0, height = 50, width = 60)
		sensor_frame.grid(row = 0, column = 1, padx = (10, 0), pady = (15, 0))
		sensor_label = tkinter.Label(sensor_frame, bg = "#506a96", fg = "white", text = "Sensors", font = ("Calibri", 12))
		sensor_label.grid(row = 0, column = 0, padx = (5, 0))
		self.sensor_text = tkinter.Text(sensor_frame, bg = "white", fg = "black", state = tkinter.DISABLED, height = 10, width = 50, font = ("Calibri", 10))
		self.sensor_text.grid(row = 1, column = 0, padx = (5, 5), pady = (10, 0))
		sensor_refresh_button = tkinter.Button(sensor_frame, text = "Refresh", bg = "white", fg = "black", command = lambda: client.sensor_refresh(self))
		sensor_refresh_button.grid(row = 2, column = 0, padx = (5, 5), pady = (10, 5))
		multi_frame = tkinter.Frame(self.root, bg = "#344561")
		multi_frame.grid(row = 1, column = 0, padx = (10, 0), pady = (10, 0))
		net_frame = tkinter.Frame(multi_frame, bg = "#506a96", highlightthickness = 2, bd = 0)
		net_frame.grid(row = 0, column = 0, padx = (0, 5))
		net_label = tkinter.Label(net_frame, bg = "#506a96", fg = "white", text = "Network", font = ("Calibri", 12))
		net_label.grid(row = 0, column = 0, padx = (5, 0))
		self.net_status_data = tkinter.StringVar()
		self.net_status_data.set("Status: " + "Disconnected")
		net_status_label = tkinter.Label(net_frame, bg = "#506a96", fg = "white", textvariable = self.net_status_data, font = ("Calibri", 12))
		net_status_label.grid(row = 1, column = 0, padx = (5, 0), pady = (10, 0))
		net_disconnect_button = tkinter.Button(net_frame, bg = "white", fg = "black", text = "Disconnect", font = ("Calibri", 12), width = 10, height = 1, command = lambda: client.disconnect(self))
		net_disconnect_button.grid(row = 2, column = 0, padx = (5, 0), pady = (10, 0))
		net_connect_button = tkinter.Button(net_frame, bg = "white", fg = "black", text = "Connect", font = ("Calibri", 12), width = 10, height = 1, command = lambda: client.connect(self))
		net_connect_button.grid(row = 3, column = 0, padx = (5, 0))
		net_help_button = tkinter.Button(net_frame, bg = "#506a96", fg = "white", text = "?", width = 1, height = 1, font = ("Calibri", 10), command = lambda: messagebox.showinfo("AquaSilva RMCA: Net Help", "This panel controls your network connection with the bot. See the NET options in menu bar for additional tools and actions."))
		net_help_button.grid(row = 4, column = 0, padx = (5, 150), pady = (71, 5))
		report_frame = tkinter.Frame(multi_frame, bg = "#506a96", highlightthickness = 2, bd = 0)
		report_frame.grid(row = 0, column = 1, padx = (5, 0))
		report_label = tkinter.Label(report_frame, bg = "#506a96", fg = "white", text = "Reports", font = ("Calibri", 12))
		report_label.grid(row = 0, column = 0, padx = (5, 0))
		report_type_list = [
			"None",
			"CH Check",
			"Sensors"
		]
		report_type_data = tkinter.StringVar(report_frame)
		report_type_data.set(report_type_list[0])
		report_dropdown = tkinter.OptionMenu(report_frame, report_type_data, report_type_list[0], report_type_list[1], report_type_list[2])
		report_dropdown.configure(width = 7)
		report_dropdown.grid(row = 1, column = 0, padx = (5, 0), pady = (10, 0))
		report_collect_button = tkinter.Button(report_frame, bg = "white", fg = "black", text = "Collect", font = ("Calibri", 12), width = 10, command = lambda: client.report_collect(self, report_type_data.get()))
		report_collect_button.grid(row = 2, column = 0, padx = (5, 0), pady = (5, 0))
		report_view_button = tkinter.Button(report_frame, bg = "white", fg = "black", text = "View", font = ("Calibri", 12), width = 10, command = lambda: client.report_gui(self, report_type_data.get(), self.report_content))
		report_view_button.grid(row = 3, column = 0, padx = (5, 0), pady = (5, 0))
		report_save_button = tkinter.Button(report_frame, bg = "white", fg = "black", text = "Save", font = ("Calibri", 12), width = 10, command = lambda: client.report_save(self, report_type_data.get(), self.report_content))
		report_save_button.grid(row = 4, column = 0, padx = (5, 0), pady = (5, 0))
		report_help_button = tkinter.Button(report_frame, bg = "#506a96", fg = "white", text = "?", width = 1, height = 1, font = ("Calibri", 10), command = lambda: messagebox.showinfo("AquaSilva RMCA: Report Help", "This panel allows you to request, view, and save reports."))
		report_help_button.grid(row = 5, column = 0, padx = (5, 150), pady = (22, 7))
		control_frame = tkinter.Frame(self.root, bg = "#344561")
		control_frame.grid(row = 1 , column = 1, padx = (5, 0))
		os_control_frame = tkinter.Frame(control_frame, bg = "#506a96", highlightthickness = 2, bd = 0)
		os_control_frame.grid(row = 0, column = 0, pady = (10, 0))
		os_control_update_button = tkinter.Button(os_control_frame, bg = "white", fg = "black", text = "Update OS", height = 1, width = 10, font = ("Calibri", 12), command = lambda: self.socket.sendall(client.send(self, b"command_update")))
		os_control_update_button.grid(row = 0, column = 0, padx = (5, 5), pady = (40, 5))
		os_control_shutdown_button = tkinter.Button(os_control_frame, bg = "white", fg = "black", text = "Shutdown", height = 1, width = 10, font = ("Calibri", 12), command = lambda: client.os_control_shutdown_wrapper(self))
		os_control_shutdown_button.grid(row = 1, column = 0, padx = (5, 5), pady = (0, 5))
		os_control_reboot_button = tkinter.Button(os_control_frame, bg = "white", fg = "black", text = "Reboot", height = 1, width = 10, font = ("Calibri", 12), command = lambda: self.socket.sendall(client.send(self, b"command_reboot")))
		os_control_reboot_button.grid(row = 2, column = 0, padx = (5, 5), pady = (0, 10))
		os_control_notice_button = tkinter.Button(os_control_frame, bg = "#506a96", fg = "white", text = "!", height = 1, width = 1, command = lambda: messagebox.showinfo("AquaSilva RMCA: OS Command Notice", "When using this panel's functions, please note that:" + "\n" + "1. OS Update assumes that your host OS is Debian or Debian-based, and updates through APT." + "\n" + "2. Shutdown and reboot uses Linux's built-in functions to do so through shell." + "\n" + "3. After shutting down, there is no way to turn the bot back on besides cutting and restoring power. Please use cautiously."))
		os_control_notice_button.grid(row = 3, column = 0, padx = (1, 80), pady = (50, 2))
		farm_control_frame = tkinter.Frame(control_frame, bg = "#506a96", highlightthickness = 2, bd = 0)
		farm_control_frame.grid(row = 0, column = 1, pady = (10, 0), padx = (10, 0))
		farm_control_label = tkinter.Label(farm_control_frame, bg = "#506a96", fg = "white", text = "Controls", font = ("Calibri", 12))
		farm_control_label.grid(row = 0, column = 0)
		farm_control_auto_button = tkinter.Button(farm_control_frame, bg = "white", fg = "black", text = "Auto", height = 1, width = 10, font = ("Calibri", 12), command = lambda: client.auto_wrapper(self))
		farm_control_auto_button.grid(row = 1, column = 0, pady = (5, 0), padx = (25, 5))
		farm_control_lights_button = tkinter.Button(farm_control_frame, bg = "white", fg = "black", text = "Lights", height = 1, width = 10, font = ("Calibri", 12), command = lambda: client.toggle_wrapper(self, "L"))
		farm_control_lights_button.grid(row = 2, column = 0, pady = (5, 0), padx = (25, 5))
		farm_control_valve_outlet_button = tkinter.Button(farm_control_frame, bg = "white", fg = "black", text = "Outlet Valve", height = 1, width = 10, font = ("Calibri", 12), command = lambda: client.toggle_wrapper(self, "<"))
		farm_control_valve_outlet_button.grid(row = 3, column = 0, pady = (5, 0), padx = (25, 5))
		farm_control_valve_inlet_button = tkinter.Button(farm_control_frame, bg = "white", fg = "black", text = "Inlet Valve", height = 1, width = 10, font = ("Calibri", 12), command = lambda: client.toggle_wrapper(self, ">"))
		farm_control_valve_inlet_button.grid(row = 4, column = 0, pady = (5, 0), padx = (25, 5))
		farm_control_help_button = tkinter.Button(farm_control_frame, bg = "#506a96", fg = "white", text = "?", height = 1, width = 1, command = lambda: messagebox.showinfo("AquaSilva RMCA: Controls", "This panel controls operation state, valves, and lights. Please note when the operation state is set to automatic, everything in this panel is locked and only the AUTO button is toggleable." + "\n" + "To use dimming, enter a percentage value to be adjusted to. Press reset to revert back to 100."))
		farm_control_help_button.grid(row = 5, column = 0, padx = (0, 100), pady = (32, 0))
		farm_control_lights_dimming_label = tkinter.Label(farm_control_frame, bg = "#506a96", fg = "white", text = "Light Dimmer", font = ("Calibri", 12))
		farm_control_lights_dimming_label.grid(row = 0, column = 1, padx = (5, 27))
		farm_control_lights_dimming_level_var = tkinter.StringVar(farm_control_frame)
		farm_control_lights_dimming_entry = tkinter.Entry(farm_control_frame, bg = "white", fg = "black", textvariable = farm_control_lights_dimming_level_var, width = 10)
		farm_control_lights_dimming_entry.grid(row = 1, column = 1, padx = (5, 27), pady = (5, 0))
		farm_control_lights_dimming_submit_button = tkinter.Button(farm_control_frame, bg = "white", fg = "black", text = "Adjust", height = 1, width = 10, font = ("Calibri", 12), command = lambda: client.lights_dimming_set(self, farm_control_lights_dimming_level_var.get()))
		farm_control_lights_dimming_submit_button.grid(row = 2, column = 1, padx = (5, 27), pady = (5, 0))
		farm_control_lights_dimming_reset_button = tkinter.Button(farm_control_frame, bg = "white", fg = "black", text = "Reset", height = 1, width = 10, font = ("Calibri", 12), command = lambda: client.lights_dimming_set(self, "RESET"))
		farm_control_lights_dimming_reset_button.grid(row = 3, column = 1, padx = (5, 27), pady = (5, 0))
		self.root.mainloop()
	pass
	@staticmethod
	def create_process(target, args):
		"""
		Creates a new process from multiprocessing.
		:param target: the function being processed.
		:param args: the arguments for said function being processed.
		:return: if failed, returns nothing. otherwise returns dummy variable.
		"""
		if __name__ == '__main__':
			try:
				dummy = multiprocessing.Process(target = target, args = args)
				dummy.start()
				dummy.join()
			except multiprocessing.ProcessError as me:
				print("[FAIL]: Process creation failed! Details below.")
				print(me)
				return None
			pass
			return dummy
		else:
			return None
		pass
	pass
	@staticmethod
	def stop_process(target, error_ignore):
		"""
		Stops target process from multiprocessing.
		:param target: process to be stopped.
		:param error_ignore: boolean to tell the function to throw a failure message or not when failed.
		:return: none.
		"""
		if __name__ == '__main__':
			try:
				target.terminate()
			except Exception as spe:
				if error_ignore is True:
					print("[INFO]: Stop process failed, however this is indicated to be normal.")
				else:
					print("[FAIL]: Stop process failed! See details below.")
					print(spe)
				pass
			pass
		pass
	pass
	def vitals_refresh(self):
		"""
		Requests status. Intended for multiprocessing.
		:return: none.
		"""
		while True:
			self.socket.sendall(client.send(self, b"rmca-1.0:state_get"))
			if client.receive_acknowledgement(self) is False:
				return None
			pass
			self.state_light_level = int(client.receive(self, self.socket.recv(4096)).decode(encoding = "utf-8", errors = "replace"))
			self.state_light = literal_eval(client.receive(self, self.socket.recv(4096)).decode(encoding="utf-8", errors="replace"))
			self.state_valve_inlet = literal_eval(client.receive(self, self.socket.recv(4096)).decode(encoding="utf-8", errors="replace"))
			self.state_valve_outlet = literal_eval(client.receive(self, self.socket.recv(4096)).decode(encoding="utf-8", errors="replace"))
			self.operation_status = int(client.receive(self, self.socket.recv(4096)).decode(encoding="utf-8", errors="replace"))
			if self.operation_status == 0:
				operation_status = "Manual"
			else:
				operation_status = "Auto"
			pass
			self.vitals_text.configure(state = tkinter.NORMAL)
			self.vitals_text.delete("1.0", tkinter.END)
			self.vitals_text.insert("1.0", "[STATUS] \n" + "Operation State: " + operation_status + "\n Valve Outlet Open: " + str(self.state_valve_outlet) + "\n Valve Inlet Open: " + str(self.state_valve_inlet) + "\n Lights Powered: " + str(self.state_light) + "\n Light Dimming Percentage: " + str(self.state_light_level) + "%")
			self.vitals_text.update_idletasks()
			self.vitals_text.configure(state = tkinter.DISABLED)
			if self.random_refresh is True:
				sleep(randint(1, 3))
			else:
				sleep(1)
			pass
		pass
	pass
	def sensor_refresh(self):
		"""
		Requests sensor data. Intended for multiprocessing.
		:return: none.
		"""
		while True:
			self.socket.sendall(client.send(self, b"rmca-1.0:sensor_collect"))
			if client.receive_acknowledgement(self) is False:
				return None
			pass
			data = client.receive(self, self.socket.recv(4096)).decode(encoding = "utf-8", errors = "replace").split()
			self.sensor_content = "Timestamp: " + data[0] + "\n" + "Epoch Timestamp: " + data[1] + "\n" + "Ambient Temperature: " + data[2] + " C\n" + "Water Temperature: " + data[3] + "C\n" + "Humidity: " + data[4] + "%\n" + "Water Level: " + data[5] + "\n"
			self.vitals_text.configure(state = tkinter.NORMAL)
			self.vitals_text.delete("1.0", tkinter.END)
			self.vitals_text.insert("1.0", "[SENSORS] \n" + self.sensor_content)
			self.vitals_text.update_idletasks()
			if self.random_refresh is True:
				sleep(randint(1, 3))
			else:
				sleep(1)
			pass
		pass
	pass
	@staticmethod
	def set_configuration(var, value, section, key, multi):
		"""
		Edits entry in configuration file and applies new edit to variables.
		:param var: variable being updated.
		:param value: value to be assigned to variable and entered into configuration file.
		:param section: section in the configuration file to be edited.
		:param key: key to variable in section in the configuration file to be edited.
		:param multi: boolean for whether to run a for range when reading params, useful when making multiple configuration settings.
		:return: None
		"""
		print("[INFO]: Editing configurations...")
		str(var)
		str(value)
		str(section)
		str(key)
		if multi is True:
			cycles = len(var)
			while cycles != 0:
				parameter_key = cycles - 1
				var[parameter_key] = value[parameter_key]
				config_parse_edit = configparser.ConfigParser()
				config_parse_edit[section[parameter_key]][key[parameter_key]] = var[parameter_key]
				with open("main.cfg", "w") as config_write:
					config_parse_edit.write(config_write)
				pass
				cycles -= 1
			pass
			config_write.close()
		else:
			var = value
			config_parse_edit = configparser.ConfigParser()
			print(section)
			print(key)
			config_parse_edit[section][key] = var
			with open("main.cfg", "w") as config_write:
				config_parse_edit.write(config_write)
			pass
			config_write.close()
		pass
	pass
	@staticmethod
	def set_configuration_gui():
		"""
		Planned:
		Does exactly what client.set_configuration does, but with a GUI window.
		Current:
		Either opens nano text editor for Linux systems or will open OS' built-in text editor if not Linux.
		"""
		platform = system()
		if platform in ["Linux", "Ubuntu", "Debian", "Raspbian", "Kubuntu", "Arch", "Arch Linux", "Fedora", "Linux Mint"]:
			call("sudo nano main.cfg", shell = True)
		elif platform == "Windows":
			Popen(["notepad.exe", "main.cfg"])
		else:
			messagebox.showerror("AquaSilva RMCA: OS Unsupported", "Client OS is unsupported, please manually edit configuration! The accepted operating systems are Linux and Linux distributions, and Windows. If you believe this is a mistake please open an issue on the repository page.")
		pass
	pass
	def ping(self):
		"""
		Pings host address and records latency and losses.
		:return: average latency, nested list with individual latency values, total losses, nested list with individual losses, if host resolution failed
		"""
		print("[INFO]: Starting PING test...")
		scans = [ping3.ping(self.host, timeout = 10, size = 64, unit = "ms"), ping3.ping(self.host, timeout = 10, size = 64, unit = "ms"), ping3.ping(self.host, timeout = 10, size = 64, unit = "ms"), ping3.ping(self.host, timeout = 10, size = 64, unit = "ms")]
		if False in scans:
			return [None, [None, None, None, None], 4, [True, True, True, True], True]
		else:
			result = [0, [scans[0], scans[1], scans[2], scans[3]], 0, [False, False, False, False], None]
			if scans[0] is None:
				result[1][0] = 0
				result[2] += 1
				result[3][0] = True
			elif scans[1] is None:
				result[1][1] = 0
				result[2] += 1
				result[3][1] = True
			elif scans[2] is None:
				result[1][2] = 0
				result[2] += 1
				result[3][2] = True
			elif scans[3] is None:
				result[1][3] = 0
				result[2] += 1
				result[3][3] = True
			pass
			result[0] = (result[1][0] + result[1][1] + result[1][2] + result[1][3])/4
			print("[INFO]: PING test complete.")
			return result
		pass
	pass
	def ping_wrapper(self):
		"""
		Wrapper for client.ping() for ping_gui.
		:return: none
		"""
		ping_results_raw = client.ping(self)
		if ping_results_raw[4] is True:
			self.ping_results = "Unable to resolve hostname," + "\n" + "is the NET configuration correct?" + "\n" + "Host IP was:" + "\n" + self.host
		else:
			ping_results_raw[0] = round(ping_results_raw[0], 2)
			ping_results_raw[1][0] = round(ping_results_raw[1][0], 2)
			ping_results_raw[1][1] = round(ping_results_raw[1][1], 2)
			ping_results_raw[1][2] = round(ping_results_raw[1][2], 2)
			ping_results_raw[1][3] = round(ping_results_raw[1][3], 2)
			if ping_results_raw[3][0] is True:
				ping_results_raw[1][0] = "Timed out!"
			elif ping_results_raw[3][1] is True:
				ping_results_raw[1][1] = "Timed out!"
			elif ping_results_raw[3][2] is True:
				ping_results_raw[1][2] = "Timed out!"
			elif ping_results_raw[3][3] is True:
				ping_results_raw[1][3] = "Timed out!"
			pass
			self.ping_results = "Average Latency (ms): " + str(ping_results_raw[0]) + "\n" + "Test 1 Latency: " + str(ping_results_raw[1][0]) + "\n" + "Test 2 Latency: " + str(ping_results_raw[1][1]) + "\n" + "Test 3 Latency: " + str(ping_results_raw[1][2]) + "\n" + "Test 4 Latency: " + str(ping_results_raw[1][3]) + "\n" + str(ping_results_raw[2]) + "/4" + " Loss"
		pass
		self.ping_text.configure(state = tkinter.NORMAL)
		self.ping_text.insert("1.0", self.ping_results)
		self.ping_text.update_idletasks()
		self.ping_text.configure(state = tkinter.DISABLED)
	pass
	def ping_gui(self):
		"""
		Does exactly what client.set_configuration does, but with a GUI window.
		:return: none.
		"""
		root = tkinter.Toplevel()
		root.title("AquaSilva RMCA: Ping Tool")
		root.configure(bg = "#344561")
		root.geometry('{}x{}'.format(255, 290))
		root.resizable(width = False, height = False)
		self.ping_text = tkinter.Text(root, height = 8, width = 30, bg = "white", fg = "black", font = ("Calibri", 12))
		self.ping_text.grid(row = 0, column = 0, pady = (8, 14), padx = (5, 5))
		self.ping_text.configure(state = tkinter.DISABLED)
		self.ping_button = tkinter.Button(root, bg = "white", fg = "black", text = "Ping", width = 20, font = ("Calibri", 12), command = lambda: client.ping_wrapper(self))
		self.ping_button.grid(row = 1, column = 0, pady = (0, 2))
		save_button = tkinter.Button(root, bg = "white", fg = "black", text = "Save", width = 20, font = ("Calibri", 12), command = lambda: client.report_save(self, "PING", self.ping_results))
		save_button.grid(row = 2, column = 0, pady = (0, 2))
		close_button = tkinter.Button(root, bg = "white", fg = "black", text = "Close", width = 20, font = ("Calibri", 12), command = lambda: root.destroy())
		close_button.grid(row = 3, column = 0, pady = (0, 10))
		root.mainloop()
	pass
	def report_collect(self, report_type):
		"""
		Sends a report request to host with given type and sets self.report_content with results.
		:param report_type: type of report.
		:return: none.
		"""
		if report_type == "":
			pass
		elif report_type == "CH Check":
			self.socket.sendall(client.send(self, b"rmca-1.0:command_ch_check"))
			if client.receive_acknowledgement(self) is False:
				return None
			pass
			data = client.receive(self, self.socket.recv(4096))
			data = data.decode(encoding="utf-8", errors="replace")
			self.report_content = data
		elif report_type == "Sensors":
			self.socket.sendall(client.send(self, b"rmca-1.0:sensor_data_clear"))
			if client.receive_acknowledgement(self) is False:
				return None
			pass
			data = pickle.loads(client.receive(self, self.socket.recv(262144)))
			file = open("sensor_data-" + str((strftime("%b%d%Y%H%M%S"), gmtime())[0]) + ".p", "wb")
			pickle.dump(data, file, pickle.HIGHEST_PROTOCOL)
			file.close()
			data_index = int(client.receive(self, self.socket.recv(4096)).decode(encoding = "utf-8", errors = "replace"))
			file_index = open("sensor_data_index-" + str((strftime("%b%d%Y%H%M%S"), gmtime())[0]) + ".txt", "wb")
			file_index.write(str(data_index).encode(encoding = "ascii", errors = "replace"))
			file_index.close()
			data_read_index = 0
			while data_index != data_index:
				self.report_content = data[data_read_index][0] + " " + data[data_read_index][1] + " " + data[data_read_index][2] + " " + data[data_read_index][3] + " " + data[data_read_index][4] + " " + data[data_read_index][5] + "\n"
				data_read_index += 1
			pass
		else:
			return None
		pass
	pass
	def report_gui(self, report_type, content):
		"""
		Views a report with given type and contents.
		:param report_type: type of report.
		:param content: report contents to be displayed.
		:return: none.
		"""
		if self.report_content == "":
			return None
		pass
		root = tkinter.Toplevel()
		root.title("AquaSilva RMCA: Report Viewer, " + report_type)
		root.configure(bg = "#344561")
		root.geometry('{}x{}'.format(400, 370))
		root.resizable(width = False, height = False)
		graphics_report = tkinter.Text(root, height = 15, bg = "white", fg = "black", font = ("Calibri", 12))
		graphics_report.configure(state = tkinter.NORMAL)
		graphics_report.insert("1.0", content)
		graphics_report.update_idletasks()
		graphics_report.configure(state = tkinter.DISABLED)
		graphics_report.grid(row = 0, column = 0, pady = (5, 14))
		graphics_report_close_button = tkinter.Button(root, bg = "white", fg = "black", text = "Close", width = 40, font = ("Calibri", 12), command = lambda: root.destroy())
		graphics_report_close_button.grid(row = 1, column = 0, pady = (0, 10))
		root.mainloop()
	pass
	def report_save(self, report_type, content):
		"""
		Saves a report with given type and contents.
		:param report_type: type of report.
		:param content: report contents to be saved.
		:return: none.
		"""
		if self.report_content == "" and report_type != "PING":
			return None
		pass
		print("[INFO]: Generating timestamps for report...")
		timestamp = strftime("%b%d%Y%H%M%S"), gmtime()
		timestamp_output = timestamp[0]
		timestamp_str = str(timestamp_output)
		file_report_name = report_type + "_report-" + timestamp_str + ".txt"
		print("[INFO]: Generating text file report...")
		file_report = open(file_report_name, "w+")
		file_report.write(content)
		file_report.close()
		print("[INFO]: Report saved.")
	pass
	def os_control_shutdown_wrapper(self):
		"""
		Creates dialogue asking for user to confirm to shutdown bot.
		:return: none.
		"""
		confirm_dialogue = messagebox.askyesno("AquaSilva RMCA: Confirm Shutdown?", "Are you sure you want to shutdown the bot? There is no way to boot it besides physically restarting its power source, and if the Arduino fails, you may overdischarge your battery.")
		if confirm_dialogue is True:
			self.socket.sendall(client.send(self, b"command_shutdown"))
			client.disconnect(self)
		else:
			return None
		pass
	pass
	@staticmethod
	def exit(status):
		"""
		Stops application.
		:return: none.
		"""
		print("[INFO]: Stopping application...")
		app_end(status)
	pass
	def connect(self):
		"""
		Connects to an IP with port number, and starts an encrypted connection.
		:return: none.
		"""
		print("[INFO]: Creating socket connection...")
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.socket.setblocking(False)
		self.socket.settimeout(10)
		try:
			self.socket.connect((self.host, self.port))
		except socket.error as se:
			print("[FAIL]: Failed to connect! See below for details.")
			print(se)
		pass
		if client.receive_acknowledgement(self) is False:
			return None
		pass
		self.socket.sendall(client.send(self, self.auth))
		if client.receive_acknowledgement(self) is False:
			print("[INFO]: Closing connection due to invalid authentication...")
			client.disconnect(self)
			return None
		pass
		print("[INFO]: Successfully connected to host!")
		# AES + RSA-based encryption was not finished, and sections using it were commented out.
		# print("[INFO]: Generating encryption keys...")
		# random = Random.new().read
		# self.key = RSA.generate(1024, random)
		# self.private = self.key.exportKey()
		# self.public = self.key.publickey().exportKey()
		# hash_public_object = hashlib.sha1(self.public)
		# hash_public = hash_public_object.hexdigest()
		# print("[INFO]: Forwarding keys to host...")
		# self.socket.sendall(self.public)
		# confirm = client.receive_acknowledgement(self)
		# if confirm is False:
		#     return None
		# pass
		# self.socket.sendall(hash_public)
		# confirm = client.receive_acknowledgement(self)
		# if confirm is False:
		#     return None
		# pass
		# msg = self.socket.recv(1024)
		# self.socket.sendall(b"rmca-1.0:connection_acknowledge")
		# en = eval(msg)
		# decrypt = self.key.decrypt(en)
		# hashing sha1
		# en_object = hashlib.sha1(decrypt)
		# en_digest = en_object.hexdigest()
	pass
	def disconnect(self):
		"""
		Sends a message to host notifying that client has disconnected and then closes socket.
		:return: none.
		"""
		self.socket.sendall(client.send(self, b"rmca-1.0:disconnected"))
		self.net_status_data.set("Status: " + "Disconnected")
		self.socket.close()
		print("[INFO]: Disconnected from bot.")
	pass
	def send(self, message):
		"""
		Wrapper for host.encrypt, formats output to be readable for sending.
		Use as socket.sendall(host.send(self, b"message")).
		:param message: message to be encrypted.
		:return: formatted byte string with encrypted message, HMAC validation, and nonce.
		"""
		encrypted = client.encrypt(self, message)
		return encrypted[1] + b" " + encrypted[2] + b" " + encrypted[0]
	pass
	def receive(self, socket_input):
		"""
		Wrapper for host.decrypt, formats received input and returns decrypted message.
		Use as host.receive(self, socket.receive(integer)).
		:param socket_input: byte string being decrypted.
		:return: decrypted message.
		"""
		socket_input_spliced = socket_input.split()
		nonce = socket_input_spliced[0]
		hmac = socket_input_spliced[1]
		encrypted_message = socket_input_spliced[2]
		return client.decrypt(self, encrypted_message, hmac, nonce)
	pass
	def encrypt(self, byte_input):
		"""
		Takes byte input and returns encrypted input using a key and encryption nonce.
		:param byte_input: byte string to be encrypted.
		:return: encrypted string, nonce, and HMAC validation.
		"""
		ciphering = Salsa20.new(self.key)
		validation = HMAC.new(self.hmac_key, msg = ciphering.encrypt(byte_input), digestmod = SHA256)
		return [ciphering.encrypt(byte_input), ciphering.nonce, validation.hexdigest()]
	pass
	def decrypt(self, encrypted_input, validate, nonce):
		"""
		Decrypts given encrypted message and validates message with HMAC and nonce from encryption.
		:param encrypted_input: encrypted string to be decrypted.
		:param validate: HMAC validation byte string.
		:param nonce: nonce, additional security feature to prevent replay attacks.
		"""
		validation = HMAC.new(self.hmac_key, msg = encrypted_input, digestmod = SHA256)
		try:
			validation.hexverify(validate)
		except ValueError:
			client.disconnect(self)
			raise Exception("[FAIL]: Message is not authentic, failed HMAC validation!")
		pass
		ciphering = Salsa20.new(self.key, nonce = nonce)
		return ciphering.decrypt(encrypted_input)
	pass
	def receive_acknowledgement(self):
		"""Listens for an acknowledgement byte string, returns booleans whether string was received or failed."""
		try:
			acknowledgement = client.receive(self, self.socket.recv(4096))
		except socket.error as sae:
			print("[FAIL]: Failed to receive acknowledgement string. See below for details.")
			print(sae)
			return False
		pass
		if acknowledgement == b"rmca-1.0:connection_acknowledge":
			print("[INFO]: Received acknowledgement.")
			return True
		elif acknowledgement == b"rmca-1.0:authentication_invalid":
			print("[FAIL]: Did not receive an acknowledgement. Authentication was invalid.")
			return False
		elif acknowledgement == b"rmca-1.0:operation_status_incompatible":
			print("[FAIL]: Current operation status is automatic, manual input is not allowed. Please change from automatic operation.")
			messagebox.showerror("AquaSilva RMCA: Operation Status Incompatible", "Host is currently running in automatic operation. Please disable this to allow for manual input.")
			return False
		elif acknowledgement == b"rmca-1.0:unknown_command":
			print("[FAIL]: Command unrecognized by host.")
			return False
		else:
			print("[FAIL]: Did not receive an acknowledgement. Instead received: ")
			print(acknowledgement.decode(encoding = "uft-8", errors = "replace"))
		pass
	pass
	def state_reset(self):
		"""
		Resets state values.
		:return: none.
		"""
		self.state_valve_outlet = False
		self.state_valve_inlet = False
		self.state_light = False
		self.state_light_level = 100
	pass
	def lights_dimming_set(self, setting):
		"""
		Sets light dimming percentage, and sends to host.
		:param setting: light percentage setting or reset signal.
		:return: none.
		"""
		if self.operation_status == 1:
			messagebox.showerror("AquaSilva RMCA: Light Dimming Error", "Host is currently running in automatic operation. Please disable this to allow for manual input.")
			return None
		else:
			if setting == "RESET":
				self.socket.sendall(client.send(self, b"rmca-1.0:light_reset"))
				self.state_light_level = 100
				if client.receive_acknowledgement(self) is False:
					return None
				pass
			else:
				try:
					int(setting)
				except ValueError:
					messagebox.showerror("AquaSilva RMCA: Light Dimming Error", "Dimming value was not a number.")
					return None
				pass
				if setting not in range(0, 101):
					messagebox.showerror("AquaSilva RMCA: Light Dimming Error", "Dimming value was a number, but was not a value between 0-100.")
					return None
				pass
				self.socket.sendall(client.send(self, b"rmca-1.0:light_adjust"))
				if client.receive_acknowledgement(self) is False:
					return None
				pass
				self.state_light_level = setting
				self.socket.sendall(client.send(self, str(setting).encode(encoding = "ascii", errors = "replace")))
			pass
		pass
	pass
	def auto_wrapper(self):
		"""
		Toggles automatic mode in host.
		:return: none.
		"""
		if self.operation_status == 1:
			self.operation_status = 0
			self.socket.sendall(client.send(self, b"rmca-1.0:command_auto_stop"))
			if client.receive_acknowledgement(self) is False:
				return None
			pass
			client.state_reset(self)
		else:
			self.operation_status = 1
			self.socket.sendall(client.send(self, b"rmca-1.0:command_auto_start"))
			if client.receive_acknowledgement(self) is False:
				return None
			pass
			client.state_reset(self)
		pass
	pass
	def toggle_wrapper(self, toggle_flag):
		"""
		Wrapper for hardware toggle commands to host.
		:param toggle_flag: Arduino command to be translated back into socket communications command and sent.
		:return: none.
		"""
		if self.operation_status == 0:
			if toggle_flag == "<":
				self.socket.sendall(client.send(self, b"rmca-1.0:command_valve_outlet"))
				self.state_valve_outlet = not self.state_valve_outlet
				if client.receive_acknowledgement(self) is False:
					return None
				pass
			elif toggle_flag == ">":
				self.socket.sendall(client.send(self, b"rmca-1.0:command_valve_inlet"))
				self.state_valve_inlet = not self.state_valve_inlet
				if client.receive_acknowledgement(self) is False:
					return None
				pass
			elif toggle_flag == "L":
				self.socket.sendall(client.send(self, b"rmca-1.0:light_toggle"))
				self.state_light = not self.state_light
				if client.receive_acknowledgement(self) is False:
					return None
				pass
			pass
		else:
			messagebox.showerror("AquaSilva RMCA: Operation Status Incompatible", "Host is currently running in automatic operation. Please disable this to allow for manual input.")
			return None
		pass
	pass
pass

c = client()
