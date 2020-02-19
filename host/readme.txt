This directory contains the software for running the host server-side remote control application.
To install, copy contents into the user "pi"'s home directory.
Next, to add a start-up script to automatically start the host RCA upon booting the bot, run "sudo ./boot_run.sh", not "rca-startup.sh". Please remember to CHMOD boot_run.sh before running.
Afterwards please ensure you have Python 3 installed, and all necessary Python and Linux packages. See requirements.txt for more details.
Before rebooting, please edit the configuration files. For security purposes there are three independent keys, the encryption key, HMAC key, and auth key.
The encryption key is hashed by MD5 and used in the Salsa20 encryption, please pick a random string of characters you would like to use, and copy them onto both host and client configurations.
The HMAC key is for verification purposes, create your own and replace the default in both host and client.
The authentication key is a final layer of security, and may be edited. In host configurations however, you must hash the password yourself (the hash type is SHA3-512). There is a tool included to do this.
Please also remember to edit what hardware your bot supports and network configurations (i.e ports and host IP).
For additional convenience, you may want to set the bot's network interface to be static. Please see online resources on how to this and why.
To access outside of your local network, set up port forwarding on your router to pass TCP connections on your selected port (default is 67777 as mentioned) to your bot IP.
See your router manual if this feature exists and how to use it.
This is the end of the install instructions. If you have questions send an email to an attached contact from the main portfolio.
