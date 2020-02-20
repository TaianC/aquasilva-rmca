"""
# AquaSilva Remote Monitoring and Control Application (AquaSilva RMCA), v1.1
# Made by Taian Chen
"""

try:
    print("[INFO]: Starting imports...")
    from subprocess import call
    from subprocess import Popen
    from time import sleep
    from time import gmtime
    from time import strftime
    from time import time
    # AES + RSA-based encryption was not finished, and sections using it were commented out.
    # from Cryptodome.PublicKey import RSA
    # from Cryptodome import Random
    # from Cryptodome.Cipher import AES
    from Cryptodome.Cipher import Salsa20
    from Cryptodome.Hash import HMAC
    from Cryptodome.Hash import SHA256
    from Cryptodome.Hash import MD5
    from Cryptodome.Hash import SHA3_512
    import socket
    import configparser
    from sys import exit as app_end
    import multiprocessing
    import serial
    from ast import literal_eval
    from .computer_hardware_check import ch_check
    # import hashlib
except ImportError as e:
    sleep = None
    gmtime = None
    strftime = None
    time = None
    tkinter = None
    call = None
    Popen = None
    Salsa20 = None
    HMAC = None
    SHA256 = None
    socket = None
    configparser = None
    MD5 = None
    app_end = None
    serial = None
    multiprocessing = None
    literal_eval = None
    SHA3_512 = None
    ch_check = None
    # RSA = None
    # AES = None
    # Random = None
    # hashlib = None
    print("[FAIL]: Imports failed! See below.")
    print(e)
except ImportWarning as e:
    print("[FAIL]: Import warnings were raised! Please proceed with caution, see below for more details.")
    print(e)
pass

class host:
    """Main class."""
    def __init__(self):
        """Initiation and command loop instructions of AquaSilva RMCA."""
        print("[INFO]: Starting host AquaSilva RMC Application...")
        print("[INFO]: Declaring variables...")
        self.socket = None
        self.host = ""
        self.port = 64220
        self.connect_retries = 0
        self.sensor_data = []
        self.sensor_data_index = 0
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
        except configparser.Error as ce:
            print("[FAIL]: Failed to load configurations! See below for details.")
            print(ce)
        except FileNotFoundError:
            print("[FAIL]: Failed to load configurations! Configuration file is missing.")
        pass
        print("[INFO]: Starting background processes...")
        self.process_sensor_collect = host.create_process(host.sensor_collect, self)
        self.process_auto = host.create_process(host.auto, self)
        print("[INFO]: Creating open server socket...")
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setblocking(False)
        self.socket.settimeout(5)
        self.socket.bind((socket.gethostname(), self.port))
        self.socket.setblocking(True)
        self.socket.listen(1)
        connection, client_address = self.socket.accept()
        self.socket.setblocking(False)
        with connection:
            print("[INFO]: Received connection from ", client_address, ".")
            connection.sendall(host.send(self, b"rmca-1.0:connection_acknowledge"))
            data = SHA3_512.new(host.receive(self, connection.recv(4096))).hexdigest().encode(encoding = "ascii", errors = "replace")
            if data == self.auth:
                print("[INFO]: Client authenticated!")
                connection.sendall(host.send(self, b"rmca-1.0:connection_acknowledge"))
            else:
                print("[FAIL]: Client authentication invalid! Given code does not match authentication code.")
                connection.sendall(host.send(self, b"rmca-1.0:authentication_invalid"))
                self.socket.close()
                host.restart()
            pass
            while True:
                command = host.receive(self, connection.recv(4096))
                if command == b"rmca-1.0:command_shutdown":
                    connection.sendall(host.send(self, b"rmca-1.0:connection_acknowledge"))
                    host.shutdown()
                elif command == b"rmca-1.0:command_reboot":
                    connection.sendall(host.send(self, b"rmca-1.0:connection_acknowledge"))
                    host.reboot()
                elif command == b"rmca-1.0:command_update":
                    connection.sendall(host.send(self, b"rmca-1.0:connection_acknowledge"))
                    host.os_update()
                elif command == b"rmca-1.0:disconnected":
                    self.socket.close()
                    print("[INFO]: Client has disconnected.")
                    host.restart()
                elif command == b"rmca-1.0:sensor_collect":
                    connection.sendall(host.send(self, b"rmca-1.0:connection_acknowledge"))
                    sensor_data_now = self.sensor_data[self.sensor_data_index]
                    for x in sensor_data_now:
                        sensor_data_now[x].encode(encoding = "ascii", errors = "replace")
                    pass
                    connection.sendall(host.send(self, sensor_data_now[0] + b" " + sensor_data_now[1] + b" " + sensor_data_now[2] + b" " + sensor_data_now[3] + b" " + sensor_data_now[4]))
                elif command == b"rmca-1.0:command_ch_check":
                    connection.sendall(host.send(self, b"rca-1.2:connection_acknowledge"))
                    connection.sendall(host.send(self, ch_check()))
                elif command == b"rca-1.0:command_auto_start":
                    # TODO add automatic operation status switching
                    pass
                else:
                    connection.sendall(host.send(self, b"rmca-1.0:unknown_command"))
                pass # add more keys here
            pass
        pass
    pass
    def state_reset(self):
        """
        Resets state values
        """
    pass
    def auto(self):
        """
        Automatic management of AquaSilva system. Intended to be ran through host.create_process.
        :return: none.
        """
        while True:
            sensor_data_now = self.sensor_data[self.sensor_data_index]
            if sensor_data_now[4] == "HIGH":
                host.serial("/dev/ttyACM0", "send", "<")
                water_level_corrected = False
                while water_level_corrected is False:
                    if self.sensor_data[self.sensor_data_index][4] == "MID":
                        host.serial("/dev/ttyACM0", "send", "<")
                        water_level_corrected = True
                    elif self.sensor_data[self.sensor_data_index][4] == "LOW":
                        host.serial("/dev/ttyACM0", "send", "<")
                        host.serial("/dev/ttyACM0", "send", ">")
                    else:
                        pass
                    pass
                pass
            pass    
        pass
    pass
    @staticmethod
    def serial(port, direction, message):
        """
        Sends or receives serial communications to the Arduino integration.
        Valid send keys are Toggle ValveOutlet, Toggle ValveInlet, Toggle Light, Light Brightness Increase, and Light Brightness Decrease in the order they appear in the message list check.
        :param port: the port that the Arduino is connected to.
        :param direction: whether to expect to receive or send.
        :param message: what contents to send, or if receiving leave as None.
        :return: if receiving, decoded string, if sending or invalid direction, none.
        """
        arduino_connect = serial.Serial(port = port, timeout = 5)
        if direction == "receive":
            return arduino_connect.readline().decode(encoding = "utf-8", errors = "replace")
        elif direction == "send":
            if message not in ["<", ">", "L", "[", "]"]: # TODO list all possible commands
                return None
            pass
            arduino_connect.write(message.encode(encoding = "ascii", errors = "replace"))
            return None
        else:
            return None
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
    def send(self, message):
        """
        Wrapper for host.encrypt, formats output to be readable for sending.
        Use as socket.sendall(host.send(self, b"message")).
        :param message: message to be encrypted.
        :return: formatted byte string with encrypted message, HMAC validation, and nonce.
        """
        encrypted = host.encrypt(self, message)
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
        return host.decrypt(self, encrypted_message, hmac, nonce)
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
            self.socket.close()
            host.restart()
            raise Exception("[FAIL]: Message is not authentic, failed HMAC validation!")
        pass
        ciphering = Salsa20.new(self.key, nonce = nonce)
        return ciphering.decrypt(encrypted_input)
    pass
    def receive_acknowledgement(self):
        """Listens for an acknowledgement byte string, returns booleans whether string was received or failed."""
        try:
            acknowledgement = host.receive(self, self.socket.recv(4096))
        except socket.error as sae:
            print("[FAIL]: Failed to receive acknowledgement string. See below for details.")
            print(sae)
            return False
        pass
        if acknowledgement == b"rmca-1.0:connection_acknowledge":
            print("[INFO]: Received acknowledgement.")
            return True
        else:
            print("[FAIL]: Did not receive an acknowledgement. Instead received: ")
            print(acknowledgement.decode(encoding = "uft-8", errors = "replace"))
        pass
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
    def restart():
        """Restarts application."""
        print("[INFO]: Restarting application...")
        Popen("main.py")
        host.exit(0)
    pass
    @staticmethod
    def shutdown():
        """Shuts down bot."""
        call("sudo shutdown now", shell = True)
    pass
    @staticmethod
    def reboot():
        """Reboots bot."""
        call("sudo reboot now", shell = True)
    pass
    @staticmethod
    def exit(status):
        """Stops application."""
        print("[INFO]: Stopping application...")
        app_end(status)
    pass
    @staticmethod
    def os_update():
        """Updates apt packages and host operating system."""
        call("sudo apt-get update && sudo apt-get upgrade -y", shell = True)
        call("sudo apt update && sudo apt upgrade -y", shell = True)
        return True
    pass
    def sensor_collect(self):
        """
        Collects sensor data from serial connection and adds to data list.
        Intended to be ran through host.create_process.
        """
        while True:
            host.serial("/dev/ttyACM0", "send", "%")
            temperature = host.serial("/dev/ttyACM0", "receive", None) 
            humidity = host.serial("/dev/ttyACM0", "receive", None)
            water_level = host.serial("/dev/ttyACM0", "receive", None)
            data_bundle = [strftime("%Y-%m-%d %H:%M:%S UTC"), str(int(time())), temperature, humidity, water_level]
            self.sensor_data.append(data_bundle)
            self.sensor_data_index += 1
            # TODO ensure receive format matches Arduino instructions
            sleep(1)
        pass
    pass
pass

h = host()
