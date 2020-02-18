#!/usr/bin/env bash
echo setting up boot startup...
sudo mv rca-startup.sh /etc/init.d/
sudo chmod +x /etc/init.d/rca-startup.sh
echo done with rca boot setup.
