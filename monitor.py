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
import shutil

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

def get_process_list():
    cpu_count = psutil.cpu_count(logical=True)

    for proc in psutil.process_iter():
        try:
            proc.cpu_percent(None)
        except:
            pass

    time.sleep(1)

    process_list = []

    for proc in psutil.process_iter(['pid', 'name', 'memory_percent']):
        try:
            info = proc.info

            cpu = proc.cpu_percent(None) / cpu_count  
            mem = info["memory_percent"] or 0.0

            process_list.append({
                "pid": info["pid"],
                "name": info["name"],
                "cpu_percent": round(cpu, 1),
                "memory_percent": round(mem, 1)
            })

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    return process_list

def get_network_speed():

    counters = psutil.net_io_counters(pernic=True)
    interface = max(counters, key=lambda nic: counters[nic].bytes_recv + counters[nic].bytes_sent)

    sent0, recv0 = psutil.net_io_counters(pernic=True)[interface][:2]
    t0 = time.time()

    time.sleep(1)

    sent1, recv1 = psutil.net_io_counters(pernic=True)[interface][:2]
    t1 = time.time()

    ul_kB_s = ((sent1 - sent0) / (t1 - t0) / 1024.0)*8
    dl_kB_s = ((recv1 - recv0) / (t1 - t0) / 1024.0)*8

    if ul_kB_s > 1000:
        ul_kB_s = str(round((ul_kB_s / 1000), 1)) + " MB/s"
    else:
        ul_kB_s = str(round(ul_kB_s, 1)) + " KB/s"

    if dl_kB_s > 1000:
        dl_kB_s = str(round((dl_kB_s / 1000), 1)) + " MB/s"
    else:
        dl_kB_s = str(round(dl_kB_s, 1)) + " KB/s"

    return ul_kB_s, dl_kB_s

def get_top3_cpu_processes(process_list):
    top3 = sorted(process_list, key=lambda p: p["cpu_percent"], reverse=True)[:3]
    return [
        f"PID: {p['pid']}, Nom: {p['name']}, CPU: {p['cpu_percent']}%, RAM: {p['memory_percent']}%"
        for p in top3
    ]

def generate_pie_chart_css(txt_nb, py_nb, pdf_nb, jpg_nb):
    files_data = [
        {"count": txt_nb, "color": "blue"},  
        {"count": py_nb,  "color": "green"},  
        {"count": pdf_nb, "color": "yellow"},
        {"count": jpg_nb, "color": "orange"}  
    ]

    total = sum(item['count'] for item in files_data)

    if total == 0:
        return "gray 0% 100%"

    current_start = 0
    gradient_parts = []
    
    for item in files_data:
        count = item['count']
        color = item['color']
        
        percent = (count / total) * 100
        current_end = current_start + percent
        
        part = f"{color} {current_start:.2f}% {current_end:.2f}%"
        gradient_parts.append(part)
        
        current_start = current_end

    css_gradient_value = f"brown, {', '.join(gradient_parts)}"

    return css_gradient_value

def get_all_threads_cpu_percent():

    threads_usage = []

    for proc in psutil.process_iter():
        try:
            proc.cpu_percent(None)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    time.sleep(1)

    for proc in psutil.process_iter():
        try:
            for thread in proc.threads():
                tid = thread.id
                cpu = thread.user_time + thread.system_time  
                threads_usage.append({
                    "pid": proc.pid,
                    "tid": tid,
                    "cpu_percent": proc.cpu_percent(None) 
                })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    cpu_count = psutil.cpu_count()
    for t in threads_usage:
        t["cpu_percent"] = min(t["cpu_percent"] / cpu_count, 100.0)

    return threads_usage


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

    process_list = sorted(get_process_list(), key=lambda p: p["name"].lower()) 
    process1 = get_top3_cpu_processes(process_list)[0]
    process2 = get_top3_cpu_processes(process_list)[1]
    process3 = get_top3_cpu_processes(process_list)[2]

    total_storage, used_storage, free_storage = shutil.disk_usage("/")

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
        "total_storage": total_storage // (2**30),
        "used_storage": used_storage // (2**30),
        "free_storage": free_storage // (2**30),
        "txt_file_nb": txt_file_nb,
        "py_file_nb": py_file_nb,
        "pdf_file_nb": pdf_file_nb,
        "jpg_file_nb": jpg_file_nb,
        "process_list": process_list,
        "pie_chart_css_value": generate_pie_chart_css(txt_file_nb, py_file_nb, pdf_file_nb, jpg_file_nb)
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
