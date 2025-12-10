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

def get_specific_file_data(extension):
    START_DIR = "/home/"
    count = 0
    total_size = 0

    for root, dirs, files in os.walk(START_DIR):
        for f in files:
            try:
                if os.path.splitext(f)[1].lower() == extension.lower():
                    count += 1
                    full_path = os.path.join(root, f)
                    total_size += os.path.getsize(full_path)
            except Exception:
                continue

    return count, total_size


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

def generate_pie_chart_css(txt_nb, py_nb, pdf_nb, jpg_nb, png_nb, docx_nb, xlsx_nb, pptx_nb, mp3_nb, mp4_nb, zip_nb):
    files_data = [
        {"count": txt_nb, "color": "blue"},  
        {"count": py_nb,  "color": "green"},  
        {"count": pdf_nb, "color": "yellow"},
        {"count": jpg_nb, "color": "orange"},
        {"count": png_nb, "color": "purple"},
        {"count": docx_nb, "color": "red"},
        {"count": xlsx_nb, "color": "cyan"},
        {"count": pptx_nb, "color": "magenta"},
        {"count": mp3_nb, "color": "lime"},
        {"count": mp4_nb, "color": "pink"},
        {"count": zip_nb, "color": "brown"},
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
    used_storage_percent = round((used_storage * 100) / total_storage, 2)

    txt_file_nb, txt_file_size = get_specific_file_data(".txt")
    py_file_nb, py_file_size = get_specific_file_data(".py")
    pdf_file_nb, pdf_file_size = get_specific_file_data(".pdf")
    jpg_file_nb, jpg_file_size = get_specific_file_data(".jpg")
    png_file_nb, png_file_size = get_specific_file_data(".png")
    docx_file_nb, docx_file_size = get_specific_file_data(".docx")
    xlsx_file_nb, xlsx_file_size = get_specific_file_data(".xlsx")
    pptx_file_nb, pptx_file_size = get_specific_file_data(".pptx")
    mp3_file_nb, mp3_file_size = get_specific_file_data(".mp3")
    mp4_file_nb, mp4_file_size = get_specific_file_data(".mp4")
    zip_file_nb, zip_file_size = get_specific_file_data(".zip")

    pie_chart_css_value = generate_pie_chart_css(txt_file_nb, py_file_nb, pdf_file_nb, jpg_file_nb, png_file_nb, docx_file_nb, xlsx_file_nb, pptx_file_nb, mp3_file_nb, mp4_file_nb, zip_file_nb)
    cores_usage =  psutil.cpu_percent(interval=0.5, percpu=True)

    return {
        "machine_name": machine_name,
        "os_name": os_name,
        "os_boot_time": os_boot_time,
        "uptime": uptime,
        "user_nb": user_nb,
        "cpu_cores_nb": cpu_cores_nb,
        "cpu_frequency": cpu_frequency,
        "cpu_usage": cpu_usage,
        "cores_usage" : cores_usage,
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
        "used_storage_percent" : used_storage_percent,
        "txt_file_nb": txt_file_nb,
        "py_file_nb": py_file_nb,
        "pdf_file_nb": pdf_file_nb,
        "jpg_file_nb": jpg_file_nb,
        "png_file_nb": png_file_nb,
        "docx_file_nb": docx_file_nb,
        "xlsx_file_nb": xlsx_file_nb,
        "pptx_file_nb": pptx_file_nb,
        "mp3_file_nb": mp3_file_nb,
        "mp4_file_nb": mp4_file_nb,
        "zip_file_nb": zip_file_nb,
        "txt_file_size": txt_file_size,
        "py_file_size": py_file_size,
        "pdf_file_size": pdf_file_size,
        "jpg_file_size": jpg_file_size,
        "png_file_size": png_file_size,
        "docx_file_size": docx_file_size,
        "xlsx_file_size": xlsx_file_size,
        "pptx_file_size": pptx_file_size,
        "mp3_file_size": mp3_file_size,
        "mp4_file_size": mp4_file_size,
        "zip_file_size": zip_file_size,
        "process_list": process_list,
        "pie_chart_css_value": pie_chart_css_value
    }

# Flask things
@app.route('/process')

def process_page():
    vars = {"machine_name": machine_name, "process_list": sorted(get_process_list(), key=lambda p: p["name"].lower())}
    vars['base_process_url'] = '/'
    return render_template('process.html', **vars)

@app.route('/') 

def home():
    vars = get_dashboard_vars()
    vars['base_process_url'] = "process"
    return render_template('template.html', **vars)

def generate_static_html():
    vars = get_dashboard_vars()
    with open(TEMPLATE_FILE, "r", encoding="utf-8") as f:
        template_content = f.read()
        
    with app.app_context():
        vars['base_process_url'] = 'process.html'
        with app.test_request_context('/'):
            rendered_index = render_template_string(template_content, **vars)
        with open(os.path.join(BASE_DIR, "index.html"), "w", encoding="utf-8") as f:
            f.write(rendered_index)
        
        vars['base_process_url'] = 'index.html' 
        with app.test_request_context('/process'):
            rendered_process = render_template('process.html', **vars)
        with open(os.path.join(BASE_DIR, "process.html"), "w", encoding="utf-8") as f:
            f.write(rendered_process)

generate_static_html()
app.run(debug=False)
