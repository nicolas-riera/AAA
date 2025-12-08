# Librairies
from flask import *
from datetime import datetime
import platform
import socket
import os
import psutil
from datetime import *
import subprocess

app = Flask(__name__)

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

def get_specific_file_nb(extension):
    START_DIR = "/home/"
    count = 0
    for root, dirs, files in os.walk(START_DIR):
        for f in files:
            try:
                if os.path.splitext(f)[1].lower() == extension:
                    count += 1
            except Exception:
                continue
    return (count)

def get_process_cpu_usage():
    processes = []
    for proc in psutil.process_iter(attrs=["pid", "name"]):
        try:
            proc.cpu_percent(interval=None)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    import time
    time.sleep(0.1)
    for proc in psutil.process_iter(attrs=["pid", "name"]):
        try:
            cpu = proc.cpu_percent(interval=None)
            processes.append({
                "pid": proc.info["pid"],
                "name": proc.info["name"],
                "cpu_percent": cpu
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    return processes

def get_process_ram_usage():
    processes = []
    for proc in psutil.process_iter(attrs=["pid", "name", "memory_percent"]):
        try:
            info = proc.info
            processes.append({
                "pid": info["pid"],
                "name": info["name"],
                "ram_percent": info["memory_percent"]
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return processes

def get_top3_cpu_processes(processes):
    processes_sorted = sorted(processes, key=lambda p: p["cpu_percent"], reverse=True)
    return processes_sorted[:3]

# Variables that can be calculed once

machine_name = socket.gethostname()
os_name = platform.platform()
os_boot_time = datetime.fromtimestamp(psutil.boot_time())

cpu_cores_nb = os.cpu_count()

total_ram = round(psutil.virtual_memory().total / (1024**3), 1)

# Flask things

@app.route('/') 

def home():
    
    # Variables that needs to be refreshed

    uptime = os.popen('uptime -p').read()[:-1]
    user_nb = len(set(u.name for u in psutil.users()))

    try :
        output = subprocess.check_output("lscpu | grep 'MHz'", shell=True).decode().strip()
    
        cpu_mhz = float(output.split(":")[1].strip())
        cpu_frequency = round(cpu_mhz / 1000, 2)
    except:
        try : 
            cpu_frequency = round(psutil.cpu_freq().current / 1000, 2)
        except :
            cpu_frequency = "N/A"

    cpu_usage = psutil.cpu_percent(interval=1) 

    ram_usage_nb = round(psutil.virtual_memory().used / (1024**3), 1)
    ram_usage_percentage = psutil.virtual_memory().percent

    ip_address = socket.gethostbyname(socket.gethostname())

    list_process_cpu_usage = get_process_cpu_usage()
    list_process_ram_usage = get_process_ram_usage()
    process1 = get_top3_cpu_processes(list_process_cpu_usage)[0]
    process2 = get_top3_cpu_processes(list_process_cpu_usage)[1]
    process3 = get_top3_cpu_processes(list_process_cpu_usage)[2]

    txt_file_nb = get_specific_file_nb(".txt")
    py_file_nb = get_specific_file_nb(".py")
    pdf_file_nb = get_specific_file_nb(".pdf")
    jpg_file_nb = get_specific_file_nb("jpg")
    
    return render_template(
        'template.html',
        machine_name=machine_name,
        os_name=os_name,
        os_boot_time=os_boot_time,
        uptime=uptime,
        user_nb=user_nb,
        cpu_cores_nb=cpu_cores_nb,
        cpu_frequency=cpu_frequency,
        cpu_usage=cpu_usage,
        total_ram=total_ram,
        ram_usage_nb=ram_usage_nb,
        ram_usage_percentage=ram_usage_percentage,
        ip_address=ip_address,
        process1=process1,
        process2=process2,
        process3=process3,
        list_process_cpu_usage=list_process_cpu_usage,
        list_process_ram_usage=list_process_ram_usage,
        txt_file_nb=txt_file_nb,
        py_file_nb=py_file_nb,
        pdf_file_nb=pdf_file_nb,
        jpg_file_nb=jpg_file_nb
    )

app.run(debug=True)