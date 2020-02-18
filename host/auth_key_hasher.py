"""
# Raspbot Remote Control Application (Raspbot RCA, Raspbot RCA-G), v1.2
# Authentication Key Hashing Tool, allows for users to hash a chosen auth key and automatically put the output into the host configuration.
# Made by Taian Chen
"""

import configparser
from Cryptodome.Hash import SHA3_512

config_parse = configparser.ConfigParser()
config_parse["ENCRYPT"]["auth"] = SHA3_512.new(input("Please enter your chosen auth code: ").encode(encoding = "ascii", errors = "replace")).hexdigest()
with open("main.cfg", "w") as config_write:
    config_parse.write(config_write)
pass
config_write.close()
print("[AKH][INFO]: Done.")
