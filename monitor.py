from flask import *
import platform
import socket
import os

def get_users():
    users = []
    try:
        with open("/etc/passwd", "r") as f:
            for line in f:
                parts = line.split(":")
                username = parts[0]
                uid = int(parts[2])
                if uid >= 1000:
                    users.append(username)
    except:
        pass
    return len(users)

machine_name = socket.gethostname()
os_name = platform.platform()
uptime = os.popen('uptime -p').read()[:-1]
user_nb = get_users()

cpu_cores_nb = os.cpu_count()
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

print(machine_name,os_name,uptime,user_nb,cpu_cores_nb, cpu_frequency,cpu_usage,total_ram,ram_usage_nb,ram_usage_percentage,ip_adress,process1,process2,process3,txt_file_nb,py_file_nb,pdf_file_nb,jpg_file_nb)