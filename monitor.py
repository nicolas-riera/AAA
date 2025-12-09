# Librairies
from flask import *
from datetime import datetime
import platform
import socket
import os
import psutil
from datetime import *
import subprocess
import time

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_FILE = os.path.join(BASE_DIR, "templates", "template.html")
STATIC_FILE = os.path.join(BASE_DIR, "index.html")

# Functions

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

def get_network_speed(dt=1.0):

    counters = psutil.net_io_counters(pernic=True)
    interface = max(counters, key=lambda nic: counters[nic].bytes_recv + counters[nic].bytes_sent)

    sent0, recv0 = psutil.net_io_counters(pernic=True)[interface][:2]
    t0 = time.time()

    time.sleep(dt)

    sent1, recv1 = psutil.net_io_counters(pernic=True)[interface][:2]
    t1 = time.time()

    ul_kB_s = (sent1 - sent0) / (t1 - t0) / 1024.0
    dl_kB_s = (recv1 - recv0) / (t1 - t0) / 1024.0

    if ul_kB_s > 1000:
        ul_kB_s = str(round((ul_kB_s / 1000), 1)) + " Mo/s"
    else:
        ul_kB_s = str(round(ul_kB_s, 1)) + " Ko/s"

    if dl_kB_s > 1000:
        dl_kB_s = str(round((dl_kB_s / 1000), 1)) + " Mo/s"
    else:
        dl_kB_s = str(round(dl_kB_s, 1)) + " Ko/s"

    return ul_kB_s, dl_kB_s

def get_top3_cpu_processes(processes):
    processes_sorted = sorted(processes, key=lambda p: p["cpu_percent"], reverse=True)
    return [f"PID: {p['pid']}, Nom: {p['name']}, CPU: {p['cpu_percent']}%, RAM: {p['memory_percent']}%" for p in processes_sorted[:3]]

# Variables that can be calculed once

machine_name = socket.gethostname()
os_name = platform.platform()
os_boot_time = datetime.fromtimestamp(psutil.boot_time())

cpu_cores_nb = os.cpu_count()

total_ram = round(psutil.virtual_memory().total / (1024**3), 1)

# Variables that needs to be refreshed

def get_dashboard_vars():
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
    up_speed, dl_speed = get_network_speed()

    process_list = []
    
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            p_info = proc.info
            
            p_info['cpu_percent'] = round(p_info['cpu_percent'] or 0, 1)
            p_info['memory_percent'] = round(p_info['memory_percent'] or 0, 1)
            
            process_list.append(p_info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    
    process_list = sorted(process_list, key=lambda p: p['memory_percent'], reverse=True)
    process1 = get_top3_cpu_processes(process_list)[0]
    process2 = get_top3_cpu_processes(process_list)[1]
    process3 = get_top3_cpu_processes(process_list)[2]

    txt_file_nb = get_specific_file_nb(".txt")
    py_file_nb = get_specific_file_nb(".py")
    pdf_file_nb = get_specific_file_nb(".pdf")
    jpg_file_nb = get_specific_file_nb(".jpg")

    return {
        "machine_name": machine_name,
        "os_name": os_name,
        "os_boot_time": os_boot_time,
        "uptime": uptime,
        "user_nb": user_nb,
        "cpu_cores_nb": cpu_cores_nb,
        "cpu_frequency": cpu_frequency,
        "cpu_usage": cpu_usage,
        "total_ram": total_ram,
        "ram_usage_nb": ram_usage_nb,
        "ram_usage_percentage": ram_usage_percentage,
        "ip_address": ip_address,
        "up_speed" : up_speed,
        "dl_speed" : dl_speed,
        "process1": process1,
        "process2": process2,
        "process3": process3,
        "txt_file_nb": txt_file_nb,
        "py_file_nb": py_file_nb,
        "pdf_file_nb": pdf_file_nb,
        "jpg_file_nb": jpg_file_nb,
        "process_list": process_list
    }

# Flask things

@app.route('/') 

def home():
    return render_template('template.html', **get_dashboard_vars())

def generate_static_html():
    vars = get_dashboard_vars()
    with open(TEMPLATE_FILE, "r", encoding="utf-8") as f:
        template_content = f.read()
        
    with app.app_context():
        with app.test_request_context('/'):
            rendered = render_template_string(template_content, **vars)

    with open(STATIC_FILE, "w", encoding="utf-8") as f:
        f.write(rendered)

generate_static_html()
app.run(debug=False)
