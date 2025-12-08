# Librairies
from flask import *
from datetime import datetime
import platform
import socket
import os
import psutil
from datetime import *

# Functions

def get_users():
    users = []
    try:
        with open("/etc/passwd", "r") as f:
            for line in f:
                parts = line.split(":")
                username = parts[0]
                uid = int(parts[2])
                if uid >= 1000 and uid != 65534:
                    users.append(username)
    except:
        pass
    return len(users)

def get_txt_file_nb():
    START_DIR = "/home/"
    extension = ".txt"
    count = 0
    for root, dirs, files in os.walk(START_DIR):
        for f in files:
            try:
                if os.path.splitext(f)[1].lower() == extension:
                    count += 1
            except Exception:
                continue
    return (count)

def get_py_file_nb():
    START_DIR = "/home/"
    extension = ".py"
    count = 0
    for root, dirs, files in os.walk(START_DIR):
        for f in files:
            try:
                if os.path.splitext(f)[1].lower() == extension:
                    count += 1
            except Exception:
                continue
    return (count)

def get_pdf_file_nb():
    START_DIR = "/home/"
    extension = ".pdf"
    count = 0
    for root, dirs, files in os.walk(START_DIR):
        for f in files:
            try:
                if os.path.splitext(f)[1].lower() == extension:
                    count += 1
            except Exception:
                continue
    return (count)

def get_jpg_file_nb():
    START_DIR = "/home/"
    extension = ".jpg"
    count = 0
    for root, dirs, files in os.walk(START_DIR):
        for f in files:
            try:
                if os.path.splitext(f)[1].lower() == extension:
                    count += 1
            except Exception:
                continue
    return (count)


# Variables

machine_name = socket.gethostname()
os_name = platform.platform()
os_boot_time = datetime.fromtimestamp(psutil.boot_time())
uptime = os.popen('uptime -p').read()[:-1]
user_nb = len(set(u.name for u in psutil.users()))

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

txt_file_nb = get_txt_file_nb()
py_file_nb = get_py_file_nb()
pdf_file_nb = get_pdf_file_nb()
jpg_file_nb = get_jpg_file_nb()

# Debugging
print(machine_name, os_name, os_boot_time, uptime, user_nb, cpu_cores_nb, cpu_frequency, cpu_usage, total_ram, ram_usage_nb, ram_usage_percentage, ip_adress, process1, process2, process3, txt_file_nb, py_file_nb, pdf_file_nb, jpg_file_nb)