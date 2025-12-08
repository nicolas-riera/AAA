from flask import *
import platform
import socket
import os

machine_name = socket.gethostname()
os_name = platform.platform()
uptime = os.popen('uptime -p').read()[:-1]
user_nb = None

cpu_cores_nb = None
cpu_frequency = None
cpu_usage = None

total_ram = None
ram_usage_nb = None
ram_usage_percentage = None

ip_adress = None

process1 = None
process2 = None
process3 = None

txt_file_nb = None
py_file_nb = None
pdf_file_nb = None
jpg_file_nb = None
