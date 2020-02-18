"""
# Raspbot Remote Control Application (Raspbot RCA, Raspbot RCA-G), v1.1
# computer_hardware_check module
# Sourced from an WIP version of RemotePotentia, an open-source remote server management software
# Made by Taian Chen
"""

class ch_check:
  def __init__(self):
    "collects system vitals"
    print("[CH-CHECK][INFO]: Vitals loaded!")
    global cpu_percentage, cpu_frequency, memory, disk_part, os_platform, os_release, os_version, disk_usage, disk_io_statistics, net_interface, sensor_temperature, sensor_fans, sensor_power, system_users, hostname
    print("[CH-CHECK][INFO]: Attempting to import SLEEP from TIME software package for Python...")
    try:
      from time import sleep
    except ImportError:
      sleep = None
      print("[CH-CHECK][FAIL]: Importing of SLEEP from TIME failed!")
      ch_check.noDelay_stop(self)
    pass
    print("[CH-CHECK][INFO]: Attempting to import PSUTIL software package for Python under name STAT...")
    try:
      import psutil as stat
    except ImportError:
      stat = None
      print("[CH-CHECK][FAIL]: Importing of PSUTIL as STAT failed!")
      sleep(30)
      print("[CH-CHECK][INFO]: 30 second grace period ended, calling application stopper.")
      ch_check.stop(self, 1)
    pass
    print("[CH-CHECK][INFO]: Import complete.")
    try:
      print("[CH-CHECK][INFO]: Attempting to retrieve CPU percentage statistics with STAT...")
      cpu_percentage = stat.cpu_percent(interval=0.1)
      print("[CH-CHECK][INFO]: Retrieval successful.")
    except stat.Error:
      print("[CH-CHECK][FAIL]: CPU percentage statistics unattainable. Setting as None...")
      cpu_percentage = None
      pass
    pass
    try:
      print("[CH-CHECK][INFO]: Attempting to retrieve CPU frequency information with STAT...")
      cpu_frequency = stat.cpu_freq()
      print("[CH-CHECK][INFO]: Retrieval sucessful.")
    except stat.Error:
      print("[CH-CHECK][FAIL]: CPU frequency information unattainable. Setting as none...")
      cpu_frequency = None
      pass
    pass
    try:
      print("[CH-CHECK][INFO]: Attempting to retrieve memory statistics with STAT...")
      memory = stat.virtual_memory()
      print("[CH-CHECK][INFO]: Retrieval successful.")
    except stat.Error:
      print("[CH-CHECK][FAIL]: Memory statistics unattainable. Setting as none...")
      memory = None
      pass
    pass
    try:
      print("[CH-CHECK][INFO]: Attempting to retrieve disk information with STAT...")
      disk_part = stat.disk_partitions(all=False)
      print("[CH-CHECK][INFO]: Retrieval successful.")
    except stat.Error:
      print("[CH-CHECK][FAIL]: Disk information unattainable. Setting as none...")
      disk_part = None
      pass
    pass
    print("[CH-CHECK][INFO]: Attempting to import SYSTEM, RELEASE, and VERSION from PLATFORM software package for Python...")
    try:
      from platform import system, release, version
    except ImportError:
      system = None
      release = None
      version = None
      print("[CH-CHECK][FAIL]: Importing of SYSTEM, RELEASE, AND VERSION from PLATFORM failed!")
      sleep(30)
      print("[CH-CHECK][INFO]: 30 second grace period ended, calling application stopper.")
      ch_check.stop(self, 1)
    pass
    try:
      print("[CH-CHECK][INFO]: Attempting to retrieve OS version and name...")
      os_platform = system()
      os_release = release()
      os_version = version()
      print("[CH-CHECK][INFO]: Retrieval successful.")
    except stat.Error:
      print("[CH-CHECK][FAIL]: OS version and name data unattainable. Setting as none...")
      os_platform = "No Data"
      os_release = "No Data"
      os_version = "No Data"
      pass
    pass
    print("[CH-CHECK][INFO]: Attempting to retrieve disk usage...")
    disk_usage = stat.disk_usage("/")
    print("[CH-CHECK][INFO]: Retrieval successful.")
    try:
      print("[CH-CHECK][INFO]: Attempting to retrieve disk statistics...")
      disk_io_statistics = stat.disk_io_counters()
      print("[CH-CHECK][INFO]: Retrieval successful.")
    except stat.Error:
      print("[CH-CHECK][FAIL]: Disk statistics unattainable. Setting as none...")
      disk_io_statistics = None
      pass
    pass
    try:
      print("[CH-CHECK][INFO]: Attempting to retrieve network interfaces...")
      net_interface = stat.net_if_addrs()
      print("[CH-CHECK][INFO]: Retrieval successful.")
    except stat.Error:
      print("[CH-CHECK][FAIL]: Network interface information unattainable. Setting as No Data string...")
      net_interface = "No Data"
      pass
    pass
    print("[CH-CHECK][INFO]: Attempting to import GETHOSTNAME and ERROR as SOCKET_ERROR from SOCKET...")
    try:
      from socket import gethostname
      from socket import error as socket_error
    except ImportError:
      gethostname = None
      socket_error = None
      print("[CH-CHECK][FAIL]: Importing of GET and EXCEPTIONS from REQUESTS failed!")
      sleep(30)
      print("[CH-CHECK][INFO]: 30 second grace period ended, calling application stopper.")
      ch_check.stop(self, 1)
    try:
      print("[CH-CHECK][INFO]: Attempting to retrieve system hostname...")
      hostname = gethostname()
      print("[CH-CHECK][INFO]: Retrieval complete.")
    except socket_error:
      print("[CH-CHECK][INFO]: Hostname unattainable. Setting as None.")
      hostname = None
    pass
    print("[CH-CHECK][INFO]: Attempting to retrieve system sensor data... (automatic fallback)")
    sensor_temperature = stat.sensors_temperatures()
    if sensor_temperature == {}:
      sensor_temperature = "No Data"
    pass
    sensor_fans = stat.sensors_fans()
    if sensor_fans == {}:
      sensor_fans = "No Data"
    pass
    sensor_power = stat.sensors_battery()
    if sensor_power is None:
      sensor_power = "No Data"
    pass
    system_users = stat.users()
    if not system_users:
      system_users = "No Data"
    pass
    print("[CH-CHECK][INFO]: Retrieval complete.")
    print("[CH-CHECK][INFO]: All vitals retrieved. Cycle complete.")
  pass
  def stop(self, exitcode):
    print("[CH-CHECK][INFO]: Stopping application...")
    from sys import exit
    exit(exitcode)
  pass
  def noDelay_stop(self):
    print("[CH-CHECK][INFO]: Stopping application with no delay...")
    from sys import exit
    exit(1)
  pass
  def str_conversion(self):
    "converts all values into strings with their proper units of measurement, with fallback entries in case of failure"
    global cpu_percentage_str, cpu_frequency_str, memory_total_str, memory_available_str, memory_used_str, memory_percentage_str, disk_usage_total_str, disk_usage_used_str, disk_usage_free_str, disk_usage_percent_str, disk_io_statistics_readCount_str, disk_io_statistics_writeCount_str, disk_io_statistics_byteReadCount_str, disk_io_statistics_byteWriteCount_str
    print("[CH-CHECK][INFO]: Vital data conversion started.")
    print("[CH-CHECK][INFO]: This may take awhile, please standby.")
    if cpu_percentage is not None:
      cpu_percentage_str = str(cpu_percentage) + "%"
    else:
      cpu_percentage_str = "No Data"
    pass
    if cpu_frequency is not None:
      cpu_frequency_str = str(cpu_frequency[0]) + "MHz"
    else:
      cpu_frequency_str = "No Data"
    pass
    if memory is not None:
      memory_total = memory[0]
      memory_total_mb = memory_total/1000000000
      memory_total_rounded = round(memory_total_mb, 2)
      memory_available = memory[1]
      memory_available_mb = memory_available/1000000000
      memory_available_rounded = round(memory_available_mb, 2)
      memory_used = memory[3]
      memory_used_mb = memory_used/1000000000
      memory_used_rounded = round(memory_used_mb, 2)
      memory_percentage = memory[2]
      memory_total_str = str(memory_total_rounded) + "MB Total"
      memory_available_str = str(memory_available_rounded) + "MB Available"
      memory_used_str = str(memory_used_rounded) + "MB Used"
      memory_percentage_str = str(memory_percentage) + "%"
    else:
      memory_total_str = "No Data"
      memory_available_str = "No Data"
      memory_used_str = "No Data"
      memory_percentage_str = "No Data"
    pass
    if disk_part != 0:
      disk_part_numindex = 0
      disk_part_list = list(disk_part)
      for x in disk_part_list:
        disk_part_numindex += 1
      pass
    else:
      disk_part_numindex = 0
      disk_part_list = ["No Data"]
    pass
    disk_usage_total = disk_usage[0]
    disk_usage_used = disk_usage[1]
    disk_usage_free = disk_usage[2]
    disk_usage_percent = disk_usage[3]
    disk_usage_total_mb = disk_usage_total/1000000000
    disk_usage_total_rounded = round(disk_usage_total_mb, 2)
    disk_usage_used_mb = disk_usage_used/1000000000
    disk_usage_used_rounded = round(disk_usage_used_mb, 2)
    disk_usage_free_mb = disk_usage_free/1000000000
    disk_usage_free_rounded = round(disk_usage_free_mb, 2)
    disk_usage_total_str = str(disk_usage_total_rounded) + "MB Total"
    disk_usage_used_str = str(disk_usage_used_rounded) + "MB Used"
    disk_usage_free_str = str(disk_usage_free_rounded) + "MB Free"
    disk_usage_percent_str = str(disk_usage_percent) + "%"
    if disk_io_statistics is not None:
      disk_io_statistics_readCount = disk_io_statistics[0]
      disk_io_statistics_writeCount = disk_io_statistics[1]
      disk_io_statistics_byteReadCount = disk_io_statistics[2]
      disk_io_statistics_byteReadCount_mb = disk_io_statistics_byteReadCount/1000000000
      disk_io_statistics_byteReadCount_rounded = round(disk_io_statistics_byteReadCount_mb, 2)
      disk_io_statistics_byteWriteCount = disk_io_statistics[3]
      disk_io_statistics_byteWriteCount_mb = disk_io_statistics_byteWriteCount/1000000000
      disk_io_statistics_byteWriteCount_rounded = round(disk_io_statistics_byteWriteCount_mb, 2)
      disk_io_statistics_readCount_str = str(disk_io_statistics_readCount) + " Reads"
      disk_io_statistics_writeCount_str = str(disk_io_statistics_writeCount) + " Writes"
      disk_io_statistics_byteReadCount_str = str(disk_io_statistics_byteReadCount_rounded) + "MB Read"
      disk_io_statistics_byteWriteCount_str = str(disk_io_statistics_byteWriteCount_rounded) + "MB Written"
    else:
      disk_io_statistics_byteReadCount_str = "No Data"
      disk_io_statistics_byteWriteCount_str = "No Data"
      disk_io_statistics_byteReadCount_str = "No Data"
      disk_io_statistics_byteWriteCount_str = "No Data"
    pass
    print("[CH-CHECK][INFO]: Conversion completed.")
    print("[CH-CHECK][INFO]: Returning strings...")
  pass
  def report(self):
    print("[CH-CHECK][INFO]: Attempting to import GMTIME, SLEEP, and STRFTIME from TIME...")
    try:
      from time import gmtime
      from time import strftime
      from time import sleep
    except ImportError:
      gmtime = None
      strftime = None
      sleep = None
      print("[CH-CHECK][FAIL]: Importing of GMTIME, SLEEP, and STRFTIME from TIME failed!")
      print("[CH-CHECK][INFO]: 30 second grace period ended, calling application stopper.")
      ch_check.stop(self, 1)
    pass
    print("[CH-CHECK][INFO]: Generating timestamps...")
    timestamp = strftime("%b %d %Y %H:%M:%S"), gmtime()
    timestamp_output = timestamp[0]
    print("[CH-CHECK][INFO]: Generation complete.")
    local_ips = []
    for x in net_interface:
      local_ips.append(net_interface[x][0][1])
    pass
    local_ips_str = str(local_ips)
    sensor_temperature_str = str(sensor_temperature)
    sensor_fans_str = str(sensor_fans)
    sensor_power_str = str(sensor_power)
    system_users_str = str(system_users)
    print("[CH-CHECK][INFO]: Assembling text report...")
    output = "[Vitals Report]" + "\n" + "Report Timestamp: " + timestamp_output + "\n" + "Bot: " + hostname + "\n" + "\n" + "Local IP(s): " + local_ips_str + "\n" + "OS Platform: " + os_platform + "\n" + "OS Release: " + os_release + "\n" + "OS Version: " + os_version + "\n" + "CPU Frequency: " + cpu_frequency_str + "\n" + "CPU Usage: " + cpu_percentage_str + "\n" + "Memory Percentage: " + memory_percentage_str + "\n" + "Memory Available: " + memory_available_str + "\n" + "Memory Used: " + memory_used_str + "\n" + "Memory Total: " + memory_total_str + "\n" + "Disk Percentage: " + disk_usage_percent_str + "\n" + "Disk Usage: " + disk_usage_used_str + "\n" + "Disk Available: " + disk_usage_free_str + "\n" + "Disk Total: " + disk_usage_total_str + "\n" + "Disk Reads: " + disk_io_statistics_readCount_str + "\n" + "Disk Read: " + disk_io_statistics_byteReadCount_str + "\n" + "Disk Writes: " + disk_io_statistics_writeCount_str + "\n" + "Disk Written: " + disk_io_statistics_byteWriteCount_str + "\n" + "Temperature Telemetry: " + sensor_temperature_str + "\n" + "Fan Telemetry: " + sensor_fans_str + "\n" + "Power Telemetry: " + sensor_power_str + "\n" + "System Users: " + system_users_str
    return output
  pass
pass
