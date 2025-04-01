
from io import BytesIO
import zipfile
from pathlib import Path
from flask import Flask,send_file,render_template,request,jsonify,send_from_directory,session,redirect,url_for
import os
import time
import re
from datetime import datetime, timedelta
import psutil
import threading
from flask_socketio import SocketIO, emit
import tkinter as tk
from tkinter import filedialog,messagebox
import webbrowser
import socket
import sys
import pystray
from PIL import Image, ImageDraw
import netifaces
import io
import base64
import json
import portalocker
import asyncio
import aiofiles
import aiofiles.os
from pathlib import Path
import subprocess
async def get_file_size(file_path):
    """异步获取文件大小"""
    try:
        stat = await aiofiles.os.stat(file_path)
        return stat.st_size
    except:
        return 0

async def scan_folder(path):
    """异步扫描文件夹"""
    entries = await aiofiles.os.scandir(path)
    files, dirs = [], []
    for entry in entries:
        if entry.is_dir():
            dirs.append(entry.path)
        elif entry.is_file():
            files.append(entry.path)
    return files, dirs


async def build_folder_structure_async(root_dir):
    """异步构建文件夹结构"""
    structure = {"files": []}
    
    files, dirs = await scan_folder(root_dir)
    
    # 处理文件
    for file_path in files:
        structure["files"].append(os.path.basename(file_path))
    
    # 处理子文件夹（并发）
    tasks = []
    for dir_path in dirs:
        dir_name = os.path.basename(dir_path)
        task = asyncio.create_task(process_subfolder(dir_path, dir_name))
        tasks.append(task)
    
    subfolders = await asyncio.gather(*tasks)
    structure["files"].extend(subfolders)
    
    return structure

async def process_subfolder(dir_path, dir_name):
    """异步处理子文件夹"""
    total_size = 0
    files, dirs = await scan_folder(dir_path)
    
    # 统计文件大小（并发）
    size_tasks = [asyncio.create_task(get_file_size(file)) for file in files]
    sizes = await asyncio.gather(*size_tasks)
    total_size = sum(sizes)
    
    # 递归处理子文件夹
    items = (await build_folder_structure_async(dir_path))["files"]
    items.reverse()
    return {
        "folder": dir_name,
        "size": round(total_size / (1024*1024), 2),
        "items": items
    }

async def main(root_dir):
    print("启用加速扫描模式")
    structure = await build_folder_structure_async(root_dir)
    structure["files"].reverse()
    return structure











admin = {"username": "admin", "password": "123"}
Cache = None
thre = threading.Thread()
root = tk.Tk()
root.withdraw()
thre2 = threading.Thread()
filelen = 0

def get_all_ips():
    Publik_ips = []
    private_ips = []
    interfaces = netifaces.interfaces()  # 获取所有网络接口
    for interface in interfaces:
        addrs = netifaces.ifaddresses(interface)
        if netifaces.AF_INET in addrs:  # 只获取 IPv4 地址
            for addr in addrs[netifaces.AF_INET]:
                if 1 < int(addr['addr'].split('.')[0]) < 191:
                    if addr['addr'] == '127.0.0.1':
                        continue
                    Publik_ips.append(addr['addr'])
                elif 191 < int(addr['addr'].split('.')[0]) < 223:
                    private_ips.append(addr['addr'])
    return [Publik_ips,private_ips]


def get_port_process(port=5000):
    for conn in psutil.net_connections():
        if conn.laddr.port == port and conn.status == 'LISTEN':
            return psutil.Process(conn.pid)  # 返回进程对象‌:ml-citation{ref="3,4" data="citationList"}

def open_browser():
    webbrowser.open('http://localhost:5000')

def create_image():
    # 创建一个空白的图像
    # image = Image.new('RGB', (64, 64), 'white')
    # dc = ImageDraw.Draw(image)
    # dc.rectangle((16, 16, 48, 48), fill='blue')
    bs4data = b'iVBORw0KGgoAAAANSUhEUgAAAMgAAABrCAMAAAAFDj3sAAAAAXNSR0IB2cksfwAAAAlwSFlzAAAOxAAADsQBlSsOGwAAAaRQTFRFICJYIydiRm3FQmjBHRtMGxlIGRVAFxM7GxdEqM7/LT+IIB9TJjBxAivlJCpnJS1sPGC+S3XNFRA1QWS6KTZ8KjqBSXHJHx1P7fX/Pl+yOly3L0OPTnrRUX7WGSibMUeVOFSnNk+fJziNGSOR9Pr/zeH/1eb/Mk2m5/L/FRl2mcH/HR1QM0qaO1qsEymmVILd0vb+N1nAo8n/ETHGKDR4NVjJsNX/LkqvGyykj7r+X4/oHy6TM1fVWYXWDC3QwNX9Kj+aITabFx2Gnsb/BTDgiLP7x9v+FBRqLESkO2TIHDGvNlWwuuH/HCeHKDR1QXnZE0XdZZftISRdCDrfs8z94u7/WIniRGvLMVK6TG/Wb5/0eKj4MlrnDznVhK74IUPJYI3cFS23NFzdob/2iKvoGzbBOGjWaOr/Lk7JIj2zFh1+u8/8FzvNNm3kYNz/aJXgM2P0T5Trrsb2F1HoRYTkLEq7IlPaISl8TKv7l7fxWZ7yJzJ0cZ7mU8L9FBJbicz8Q5L3OHf2crX6YrL7xNn3fKLlmpagODJQ3Or/xL+y/NI5ZVZDFqA/EAAAFbpJREFUeJy12glDU9fWBuCj0dZYa+MFaUBGJQniAETDjJEpEqYYJYNEBg3kAiGl0ABCsaDCbe53//S31trD2WcKQe2rzJGs56w9HVB7rKex8R5kZANyH/PiBfx98eIvzLUffvzXP5QfnfKDNddkrpqiNT42UBpRQgyB4ZK/rv7wfS2O9TspnBFXr165ojWaJY33GAEo2Bldgl35Rso5xdsbrp1noGhYuirBATbCxxYbYy++rSs/Vlg+AOwGk6qwMK7o0R6bJDS8SPKCQ5hETpZKy7pYbAkVtUJCqHbLRGHja2NE74mwXP3hnwZcu2bsgxWh1//3f//z95VfIdo7PqLME2WE2rGxISeKbvk+TXHogclgZRgb8et//+/vXwny5N27x+YIycj9+3IxVilX1dFcYdnnVf+DuQ3nTYor1Ihf//c/AXlipbDBNYLjamNjQ+4r9xWJbcpXWjYWQiUIkZ8gCLFSaGe8N8NmyMaIlEjKla8tmJddVlB2UhgUP+khyCZSDJhGAWETRd/tab+Hl7++TeIAsFmbTAZDL34yQ55sbj5hlnfvJiflcWVmZmRkZoPG14hKIc4D+0qu2Vd9HsBOYIO4YiMQkLFnCFlYWNh8wkfZu0nRkxlyMIhFcqWMwqHaSgVXrjgSEGFyaCw//zy2wCQLm5uiM5NCMjPDJvvICKdslJd8ffHCYNMG2zlhQDAIUp4tUFhTVomCSxdARhSJsS0vrl7lZcEL/a243AoHUlmFZsrYz4zCsikpUsIptB6LtvCt5cKlVl5+uXlto4A8e2agCMkqSHob2fDCwmdmhERaNu7/9fXVlwUYt4kyw0nNkycLJgqbKUgRErKM0N5ibMtfVJKoid63K7l80U4Aq8Ku/lc8tPw+WxjTJS8XNjf5+EJJo5CMcInal/sPKi7xooIKRtMrNTC0sOiF14LyEsIom6uCMsNyzyjBfA+JqXzbTaI8giA/jxHlmUr54+VLPr5A0iuaoksUC5M8ePCAXsqVW/7yE6EygxXBID+bKa9BwiibxplyzxAuefGgbND3QKn2gf7OA8dd+gKKSyIam+fP0GJHWV1dneQUSyqSOKRs/edNbDNCh0A4ZUFQ/oBICoyvewMDDpZXP/30AP46hr50Xt3l6ieDkXHJEgnhlAVO4RKibCKlcWBggEYX606jYtEqrbJM/fjHEVGuE5CbEBXCJ4voyus/ZFOAgk1ByQxKGu81NiqjbeOrJVqZ8m0ZdgYWA0Sf92M0vhTK6rpBwnKPz//7+tPKwpwqNz6qPKHscLppjAkiKc90CpMsrU9C6TMz+0Bp7JUSosxcqqiwC6ZMKxTALzd/gQBkzCzRKfClMTnpl6AnMN9pP2mclJJ9kuzDOv59iofyz5sTCkIJ7OzPLBY5wCB81i8tgWR9mFNkS0Cyjy25ecl2l3rFq9NfV9yCc6aEUYGQd+Li21AWGAUleySZlJJGo2T/koPEgHolQK9eicvvFOv6eskecYPlF+0x3EU9eWa1CMrrsdfUFJSskwSmPAwoMPSyvuzDR/s3nXpy4dgQHDpxQw39yFRYTBRxO/+advo9hNDoIgk1pZc0M/v7+zDfDE9NJX1j+Tark43iTwxAoBROsQ4xomwiBSR7e0u7JAFKIw6vAVRgbCXWoEyxXaLyKxUoCqUNf+rRaIj0Km0Zs+nKJp7u9/bWSELDq1GV9KLkxi/0bOdoKow9weQgwOxTyqxG2xtVIywGyhhRVlc3N7Epa7s9E7wpuDkOCEjvwL5OEaFyvg1gszzZIJ5Ww4sGW9qAvLR2QwwoC0hZouGV7pmYAMvwXXsJ25zKxKZ0R8FNu+WJGWZnJYJHwyEyMDA8PMwrmhRtGVMorxfwELz0cg+awijDjCIkk5PDd+G73bhhWt3Los6J43gyK25DGGR4GIfLcG+jqS1CM8Yp60t7kBCn3L1LTWEOlNy9Xc3WdGtuXoRkEJiG06xUSAMLg6RzudAujHwxXx6b2oISpKwj5e370FQgAOPrOVJgXKJjfXUVJHer/7xhzAU4JrtKIMXsrFRUVxsZ16/f1rCU4VDycDvHtghhmdTbwiQGStdUc2CiZwIoYBnunVxfGtxbmoCPnuoLoqOHhtwvttXrBuMiqxvU8cQMLAyyHirEogzCMdgW1TKmUNb23r7NeWqbAz2Mcnd4cn0vWdxbgh5VVz+VsXDsBp0FYdomZkXsWiEUdwRkeL1nly+qKkUZYjyMsrs2+L6QcxHlOVDg3+8WtgprKLldrUfnlG2P6bBhIaiTQldIBIvG1yzKwICFog4xJgHKElIKhZSr9tFUGijPn0/0hHK5tSVFQk9WLRtk7Y5t/jQKjH2wawWlqamJQWwl0jJpsLxmlN3dEFBil6tq62gR60nnYiTBxUs8l8BwzuysM8deYEBYFNeF4uHDh01adTVOWFtJY6NCeUc/LnpNEDhFAiUdyhViDTWuqq50T09PV+woFtqFoz6TXL/T9PCO1UKa2T9NmbUTqARlmTUymOJhINCiscfdpeVnACUWTq/elpcvF17zvISmpKO5YnGovuZytAtUxWI0DRJchq/fvfOwzhNoQsp1XoCqeTprk6eW3doZoTYjAJmq0sRD78oM4B9TOGWV3aIwCVDSXdFYMbm8PFSfikZzsWIujfdfE8/hOQKuW3UTTfBsioVpnqqZVd6vNglUgnVIcUYLKKbqanYAclv+i7sOIcsw7d+EebagUzyphv740dFWRyxWXImTZGni+fOmQJ2nKx14KCimzhg81ZbcNuf69euOjLr6lbw/ot0+B6FrcA71CgvrC1DWuly3kvOZxcx8fHu7mOtaI8nDicBUOnqEkiZ6XiPmtrV2B4GBgBuGidE8Vbfij4TDYa0yBW17LLwvq084ZW8tWpOMZ/r6+j7Pb8dyoUG8Ke6BKxWNJdOBACwoTRxzx9Fy20ZgVYgtAxngaGkBxlSd6zSSh2gGxJ3nMiaF/LxigdtglLzcG8w19Gf6gsH28fn+WO493IGtTU15YtuxOjiUteCy0tTEOQaLU67b5I6qYO1ohnZ4bq0kwuCY02wVdplg4RjZFvrN0F4uhpJu9+j4fBIog6F0XbS4FfNMTTU3BzjmoUKxxdjVb1IwBjlawOGp2Tr1heeoI5Jxh4rFtSzA6zUxeijSApRVDL8NLhTji6Pd093u4/lksZCLemA9i3nq6qbQ0kzf1mzhIuf6DQRVAYwWGFZVBwl/OD83lw8LCGvGBK5kmB6yTJgYaQxRxCATFLwN/uNtYXu+zz09Pd19/Hm7GMulYsVijcsDFsSwzthTKjFwBCmYA/ox5PfNYfI42elR0lFX58GnnurpCUwYAo6uaBQ2vrRsCmZ9fW+PKHjLVfh0+Pl4urOzc/r482ExVtyGVymXyyMxbJCxqV+xQBoEo6WFHI/qak4jqEBIJKLpVx3a4YlGU7C1wQ4wRfXqDHDEtg+3Y9EuJhGUid0P77ErsFJxipsoo58PtzHF+oZ6wEQ9bJQJiq3FDDAYeC8Eo/lRbdVWIkzNAIYOgdnRM4XjGhKLRT00iJSk09Hicffxh1iUDy9OmVgPxXbXmQQohcLJ4XF3p9dLXdnePjxMbvXXp1INqZRLUh6KrpDGpnwTwaRgDoDUn/ryhPD5Ij5NOmBcRYsfvmDowhskeBgpfgFJMRdK7+4a2oVZX1pikveFTydfjqfbWluJApZ4PNnQcHS2DK0miqEp5wp0hFAgAx21VZe3Sj5/yQ/x+fyaKAUa0pU7PJ7GHG/nULKrJ70WglPh9uEJ7HihNZSYLEyytgd3XIXi9pfjTm+r7Eo8mUx2dLx5k0rBAINpHzBukw71KwRFQQzmcNWcldpKsK1HSiVfXpOOHrron48hX+C6Q72GhAbf5wqFAuwRg/ARUdRJtMsggwgpFE9gqnS2EeXL4WH8MBPvj/cjJeqRw8uucjuCbuAKYHCHHxSwF9LCxSEBBoGVBq4gLp6DJsgglMgzaEcJ4Pijx+XgLgW+DS1gNMC+fP7c3v05IyRdNLyU/d6hfiNBKhijtqrKNVRq8/si4Aju5GGyw54R4PO5C4/ilFxu0BIgvGWxaUoggKeRAKwJIZAApFgkCs6Vbujx9HRfZr6/o4EkOLpaWh6WS4s5zTqDOy43nCbAgQ3J46qlrEtdoWiORxZtyO+fPv2OgXcHuSTAzgK4leJrPMXB2neI2whQ2LRv6xw9bk10j87Hkx18dKHElmIRSAJXIIMct2Cq82EFS5dP0x0AwcuJjOLJh5MPkBMILx7y6eTjbx8xHz78rksMgQkAe2osvo19xaZAV1qxK53ekq8PJDC6aHA1NxslVoAJwRS6o34FTr1zO8EgOQCSlsH5jFO1UMCKWf4NgTdY+4eP4iP8xAlK0mZIM4NEY7FUiiA4QdydSOlMtMLwwnnCWtJsX7qtwaDg/Vhpg34Eg8EdBonokFChCMV+hC7AnnhyAnVT4Q75DSW416gMcNBxBA4IcEKgwXX4BXafTliMMdN9ME/E4HKiNNsSpAIY4KgZSiRgfuyAAyGwI2ohTFdXV6hwgo6PBTazcULQ6IJP/aZHkXx6b4TQcbMO9wo66MRi/f3ggOXcPZ1IdBLE6wuO00RBjEccJp3y6JEFgQp0XK5Z9nvh/A4dCc7RyPJpWDZhQmxlGuTvouXt73J6YKBL6BKwk0Ho45TsRjNBRDwuF8yS5OcvwU5f8Hi0u4QQfx7uvNhuUlcpQRokAx23Gs68/jmYImzJikTCGt8aQubwFVddvSTqhHpVCCFkio2p2im6X/NIiMcFXenPuN2nwc+Z8fGgz9taci/Oi22x7tGjCxm4gjFqbtUP7ZT4guXz++DcmNdodvNOdMkIir4NvjevyHgbiBC6suw+xhOLeZSWpFLFQzhuHcbn5zOL7T5/u3QQ5JFT/WZDlQwyoB236hvO4OQLDF84T3t7OKLRoPn0e+G9AcItIcueqG/v+PD0lJq66HKHS2lJNBWLx4sdyWR/f3w+0z4Hm3sStsQU3m3VWkq374NBQQxoR/3Q0DISImF+W4VDiy2oHz8UBo0OQTGMNSVWB4wsmOoKxJWKLRdjDQ0dHURZ7E/C1v4mRXdatXYSJ4JUCMbQ8pav5EvQdoi7IUQTq2khJyBQhaNGCT1UYTzSZzqDwCxpaIi9gQAFLR3kAEhVlSjWpn4zAQ2EAAWNKmSs+ODAiD88yZMCTvLaR2R8BEc0xBUUc3fMIE5WHI+koRZfVSFkCDbG1BuyNBADHS6XDrHGYmAIwYB2bB0d7MBNgjdR8tHCizckJb8GiyrMkUKOQfQr2mW1WMIfanIQxOPBMlIsb2RSCMESL2TgCmA0DC0flPwlXMy9kLYS7wd0pAAKuM0ACCwm+vIphkcXftJjIXhY6mwCFcG/vOXixTBKjWBgQwySKmtcpkbUSAY4tuB+sOTlkIRfgTAGd3hMjnJRZrYJUlXlqXfpVzWlRkCcoht0AiKIAY5TuL1to2NCGxtaMK4gCY2f26McwjTnEFiiUVNLavGP2Lg86qWVjMuuMhDLjGCChq2js7OzZWCcZfPhBHN4S37qhs+fYNG4wgC5WHSI8xjhjMsMYqC41BhnBCqGVg52drIH2Z2VoyOs2+enA2jCz1Jqo7ni9WpRma9jlB8kenUpVqPLMcq8puUJt4uhoZVs9gACr7P5EpxFIqwfiUQbTnV41cqjQKKm0ly4p2HoDXwg/sqX88a6sUIniPrlGoUBu8XBzlw2m92hZCMlnBIlWboxEuJ8qcqE6i1jsDjKRZ/b9bTrreCPevAHovk8/eLA15aAWd1mhVBbtK8kVJgLGfTpjYeQMxw8bQk82+ZpD/e3lWh98npVAz4IR5vGnzFlKeEfr78G/8jcuqWvs+g4yrYySAQgcE4/9cNCBX9gdrQpjjb4kHWEre30UvEggCDUYj3vitvmlh62W+CwWt46wDKRQXeysFdAzTC0oG6a6CzIwA/gsZqyVxmeGS7Xd0gl5UsDY9C2d7RyClsF7hMRsPgS3laaIEAAB1ZP4469ZSQN1sXUZV1S7trhF/EhXy0wV28wEAKOltiPox3cuXHL9tPRsOQVg4iXr4R9KqHV4Emo7LOVs50b+9qV8hUEnvbhNmy5f2sFBwtdbHwLxeqDiYV1BXd0GnAQze4p5fd3quI7lS8AiiKJ//tg5ZQEBPEqEcWzUP0lvsP7NLsnEt/7PE9lMRdvrJ8JyID3xEdZPIWU9Pmsjiab+in0AzrjE7JvPSSiYEz55vIFQBgA0R+PZ3xYG04OZRZYG+DjiUzLaIYnWl5ZOdjagsl2doRvBAY5TqIK0uAgSCYlARH4w5YIHmr99GsoWqRs68cGUPHdPAQRYwi+/8pOfgdPNpGd00jCv4KU5SEdY0j5yi2123Qg2Z/Bs+DBfBwNi32LGTc7mvvlwCnp5cvipw0EEbdbg1tpnoMDds7M7sxF4ETjZ11ZHlJjV6D1kjsAlEEEHcjAM2Xb27PZRehEcM49FwEAv93z6eECc+UGBCSoZbeS/El2GAMcPjrPlHY4xYRh0S/A+fV3qGOIBtF435y7HTPa3h4cHcV6TcWLBpQRgAF/+Av/Hl5ppUg/SZLQZRhW9Psftuu3eg/OJEXPEFREEIpz8eZJwAg4E+YzcHyagwKC8Gzwxu0zjf7wefWzIEFG8/nj9GRneBe2g+fMCByV2+i07PX7DpBCMXmWk8kOhyRNgLgAYDKZzCJMBh/7KSHEHXR340+hnat3u01tUOofbefR8r7TeD88JYwqZOD/I8BpBqsFOy1nz2CDOgCPAJ2tHDEXltqRtFRvaoAQZCiLi+Pj431huvYkoUtrvNDiM8pH+kN0Bo4pHJucos25I4vwbIvjOwShmxj2U8gSjS//3HgWV8LSwRFlJXwayR4Apr8/aUx/WQAKxvsw7d14/Y2FW4vHoWP4PLyQgUofDfLeoIG+qxbOQ5fzsFrg70sQgad/Ojgn2PBqY8t4wnuaPfUfHITnwjj28kfxflPi5wFoco+yGswKoyBIr+iNm01nGkTMAcsDkiQBMz6uhen605oHbyNo8EWoHWxoeRNsdwIWHqbhvtlfwt/ULh7FjZmftwr6pIAPhmCwHIBVHRSPCyqzud2QPjXjFA1v6PEEIA4veA+WSMg7Yzw+s80VPs/OPexMms3MG5KxAGQHKgAoF948j/mbPj4fTPXzLC5qQCjJkwxcfHH/JSBw1BEnzjblJNca7hvPKLEdQ5UA3KZLj//M7R41NQC/nx0ACSxagh/qZdqMkATrhCl4lCv53OOsfHUMCUFl9Qdtho7+gbj47UgzGhbN0Xj1iZJ4Rz9BUzvYQDMfqtlx1B8ZlfWfDwgqsRv78oM+axzr55+GOcLvs2gOAIPdz7OuiFuxhHKL3CZO1OxEFJZr+sUE7ZaM4tdgJsDD260Aq0Ag4G1fti9z9P+tpaNYM0T42QAAAABJRU5ErkJggg=='
    image_file = io.BytesIO(base64.b64decode(bs4data))
    image = Image.open(image_file)
    return image

# 定义菜单选项的回调函数
def on_clicked():
    open_browser()



def check_port(ip, port,isopen=True):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
    sock.settimeout(5)  
  
    try:  
        result = sock.connect_ex((ip, port))  
        if result == 0:
            if isopen:
                open_browser()
            sys.exit(0)
        else:  
            return False
    except Exception as e:  
        print(f"错误: {str(e)}")  
    finally:  
        sock.close()

def monitor_bandwidth(process, interval=1):
    io_start = process.io_counters()
    time.sleep(interval)
    io_end = process.io_counters()
    return {
        "sent": round((io_end.write_bytes - io_start.write_bytes) / (1024**2),2),
        "recv": round((io_end.read_bytes - io_start.read_bytes) / (1024**2),2)
    }  # 需持续调用‌:ml-citation{ref="3,4" data="citationList"}


def get_directory_size_mb(directory):
    total_size_bytes = 0
    for dirpath, dirnames, filenames in os.walk(directory):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            if os.path.isfile(filepath):
                # 累加文件大小
                total_size_bytes += os.path.getsize(filepath)
    # 将总大小从字节转换为兆字节
    total_size_mb = total_size_bytes / (1024 * 1024)
    return total_size_mb

def CacheGet():
    global thre,filelen,Cache,config
    def get_cache():
        global Cache
        Cache = build_folder_structure(config["FileCataloguePath"]) if filelen <= int(config["asyncMax"]) and config["asyncStart"] else asyncio.run(main(config["FileCataloguePath"]))
    if thre.is_alive():
        return -1
    else:
        thre = threading.Thread(target=get_cache,args=())
        thre.start()

def build_folder_structure(root_dir):
    """
    递归构建文件夹结构
    :param root_dir: 根文件夹路径
    :return: 嵌套字典结构
    """
    structure = {"files": []}  # 初始化结构

    # 遍历根文件夹
    for item in os.listdir(root_dir):
        item_path = os.path.join(root_dir, item)
        if os.path.isdir(item_path):  # 如果是文件夹
            total = 0
            for path in Path(item_path).rglob('*'):
                if path.is_file() and not path.is_symlink():  # 跳过符号链接
                    total += path.stat().st_size
            folder_structure = {
                "folder": item,
                "size": total if total < 0 else round(total / (1024*1024), 2),
                "items": build_folder_structure(item_path)["files"]  # 递归处理子文件夹
            }
            structure["files"].append(folder_structure)
        else:  # 如果是文件出
            structure["files"].append(item)

    return structure
def lockf(lockstart, close=False):
    global lock,config_readif
    if config_readif:
        print("检测到文件")
        if lockstart:
            print("打开文件")
            lock = open("FilleTransferConfig.json", "r+")
            print("文件上锁")
            portalocker.lock(lock, portalocker.LOCK_EX)
        elif not lockstart:
            print("开锁")
            try:
                portalocker.unlock(lock)
            finally:
                if close:
                    print("关闭文件锁")
                    lock.close()
                    print(lock)
        

def count_items_in_directory(directory):
    total_count = 0
    try:
        for root, dirs, files in os.walk(directory):
            total_count += len(dirs) + len(files)
        return total_count
    except FileNotFoundError:
        print(f"目录不存在: {directory}")
        return 0
    
def is_valid_path(path):
    try:
        # 尝试创建 Path 对象
        Path(path)
        return True
    except (TypeError, AttributeError):
        path_check(path)
def path_check(path):
    if re.search(r'[:*?"<>|]', path):
        return False
    else:
        return True


def config_read():
    global config
    try:
        if os.path.exists("FilleTransferConfig.json"):
            with open("FilleTransferConfig.json", "r", encoding="utf-8") as f:
                config = json.load(f)
            return True
        else:
            print("配置文件不存在")
            return False
    except:
        print("配置文件读取失败")
        return False

def windowapp():
    try:
        subprocess.run(['PyQt5Gui.exe'])
    except:
        pass

class SysTrayIcon():
    def __init__(self) -> None:
        self.menu = (
            pystray.MenuItem('访问控制台', lambda: windowapp()),
            pystray.MenuItem('访问用户界面', lambda: on_clicked()),
            pystray.MenuItem('终止服务器', lambda: self.sys_stop())
        )
        self.icon = pystray.Icon("test_icon", create_image(), "文件互传", self.menu)
    # 运行图标
    def sys_stop(self):
        self.icon.stop()
        global config_readif
        if config_readif:
            lockf(False,True)
        os._exit(0)
    def start_server(self):
        self.icon.run()
    def start_icon(self):
        threicon = threading.Thread(target=self.start_server, daemon=True)
        threicon.start()


config = {"SingleUpload":False,"download":True,"write":True,'dirwrite':True,"FileMax":1024,"sysMax":1,"MaxSpeed":1024,"SysCataloguePath":"download","FileCataloguePath":"","log":{"upload":[],"download":[],"error":[]},"type":["zip","txt"],"IPsecure":["192.168.0.5"],"typeinspect":False,'download_Dir':6,'asyncStart':True,'asyncMax':2000,"IPwhiteStart":False,"IPwhiteList":['127.0.0.1']}
def start(filepath):
    global filelen
    if filepath == "":
        config["SingleUpload"] = True
        print("服务器已设置只允许文件上传")
        open_browser()
        return True
    else:
        filepath.replace("\\", "/")
        filepath = re.sub(r'"', '', filepath)
        if os.path.exists(filepath):
            if os.path.isdir(filepath):
                filelen = count_items_in_directory(filepath)
                print(f"文件数量：{filelen}")
                if filelen >= 10000:
                    mode = messagebox.askyesno(title="确认", message=f"当前目录文件数量{filelen}超过10000,数量过多可能导致加载过慢\n你需要重新选择目录吗?")
                    if mode:
                        return False
                config["FileCataloguePath"] = filepath
                print("路径存在,准备上传...")
                CacheGet()
                time.sleep(1)
                print("请访问http服务器地址获取文件")
                open_browser()
                return True
            else:
                messagebox.showinfo('提示', "路径存在，但不是一个有效目录，请重新输入文件路径")
                return False
        else:
            messagebox.showinfo('提示', "路径不存在，请重新输入文件路径")
            return False
app = Flask(__name__)
app.config['ENV'] = 'production'
app.config['SECRET_KEY'] = 'secret_key'
Public_network = get_all_ips()
# print(Public_network)

def UpCache():
    global Cache,thre
    if Cache == None and not thre.is_alive():
        CacheGet()
        while True:
            if not thre.is_alive():
                break
            time.sleep(0.5)
    if Cache == None and thre.is_alive():
        while True:
            if not thre.is_alive():
                break
            time.sleep(0.5)


def Ipjudge(ip_address,json_data=None,msg=0):
    global config
    if config["IPwhiteStart"]:
        if ip_address not in config["IPwhiteList"]:
            if json_data:
                return [jsonify({'code': json_data,'msg':msg}),0]
            else:
                return [render_template("end.html",title="服务器已开启仅白名单访问,你未获得权限,无权限访问"),1]
        else:
            return None
    else:
        if ip_address in config["IPsecure"]:
            if ip_address not in config["IPwhiteList"]:
                if json_data:
                    return [jsonify({'code': json_data,'msg':msg}),0]
                else:
                    return [render_template("end.html",title="服务器已开启安全访问,你未获得权限,无权限访问"),1]
            return None
        return None


@app.route('/')
def download_home():
    return  render_template("index.html",network=Public_network)
#     global filepath
#     return send_file(filepath, as_attachment=True)
@app.route('/upload', methods=['POST', 'GET'])
def upload_zip():
    ip_address = request.remote_addr
    ipC = Ipjudge(ip_address)
    if ipC:
        return ipC[0]
    if request.method == 'POST':
        if not config["write"]:
            time.sleep(0.3)
            return jsonify({'code': '服务器禁止上传文件','msg':2})
        try:
            print("开始上传文件...")
            # 检查是否有文件被上传
            if 'file' not in request.files:
                return jsonify({'code': 'No file part','msg':0})
            
            f = request.files['file']
            path = request.form.get('filepath')
            isdir = int(request.form.get('isDir'))
            if config["typeinspect"]:
                if f.filename.split(".")[-1] not in config["type"]:
                    types = "、".join(config["type"])
                    return jsonify({'code': f'文件类型不支持\n只支持文件{types}','msg':0})
            filelen = round(request.content_length / (1024 * 1024),2)
            print(f"文件大小：{filelen}MB")
            print(config["FileMax"],'限制')
            if filelen > float(config["FileMax"]):
                return jsonify({'code': f'文件大小超过{config["FileMax"]}MB','msg':0})
            oslen = get_directory_size_mb(config["SysCataloguePath"])
            print(f"系统存储空间已用：{oslen}MB")
            if oslen + filelen > float(config["sysMax"]) * 1024:
                return jsonify({'code': f'额定空间已满，请删除部分文件后再上传','msg':0})
            if f.filename == '':
                return jsonify({'code': 'No selected file','msg':0})
            if not os.path.exists(config["SysCataloguePath"]):
                os.mkdir(config["SysCataloguePath"])
            dirpath = config["SysCataloguePath"]
            print(path,'自选路径')
            if path:
                print(config["dirwrite"])
                if not config["dirwrite"]:
                    return jsonify({'code': '服务器禁止提交目录','msg':2})
                print('自定义路径')
                save_path = f"{dirpath}/{path}"
                print(f"保存目录：{save_path}")
                if not os.path.exists(save_path):
                    os.makedirs(save_path)
                save_path = f"{save_path}/{f.filename}"
            else:
                if isdir:
                    print(config["dirwrite"])
                    if not config["dirwrite"]:
                        return jsonify({'code': '服务器禁止提交目录','msg':2})
                # 构建完整的文件路径
                save_path = f"{dirpath}/{f.filename}"
                # 提取目录部分
                directory = os.path.dirname(save_path)
                print(f"保存目录：{directory}")
                # 检查目录是否存在，如果不存在则创建
                if not os.path.exists(directory):
                    try:
                        print("创建目录")
                        os.makedirs(directory)
                    except Exception as e:
                        print("创建目录失败",e)
            print(f"文件保存路径：{save_path}")
            
            # 保存文件
            f.save(save_path)
            
            # 检查文件是否保存成功
            if os.path.exists(save_path):
                print("文件上传成功")
                config["log"]["upload"].append(f"{datetime.now()}->{request.remote_addr}上传了{f.filename}")
                return jsonify({'code': '文件上传成功','msg':1})
            else:
                print("文件上传失败")
                return jsonify({'code': '文件上传失败','msg':0})
        except Exception as e:
            print(f"文件上传过程中发生错误：{e}")
            config["log"]["error"].append(f"{datetime.now()}->{request.remote_addr}上传文件时发生错误：{e}")
            return render_template("end.html",title=f"文件上传失败：{e}")
    else:
        string = "、".join(config["type"]).upper()
        print(config["typeinspect"])
        print(string)
        print(config["write"])
        return render_template('upload.html',istype=config["typeinspect"],typefile=string,dirwrite=config["dirwrite"],filewrite=config["write"],size=config["FileMax"],typeAll=config["type"])

@app.route('/files', methods=['GET', 'POST'])
def get_files():
    global Cache
    ip_address = request.remote_addr
    ipC = Ipjudge(ip_address)
    if ipC:
        return ipC[0]
    if request.method == 'GET':
        print('dom',config["download"])
        if config["SingleUpload"]:
            return render_template("end.html",title="服务器已设置只允许文件上传")
        elif config["FileCataloguePath"] == "":
            return render_template("end.html",title="服务器未设置文件目录")
        return render_template("download.html")
    elif request.method == 'POST':
        if config["SingleUpload"]:
            return jsonify({"code": "服务器已设置只允许文件上传"})
        UpCache()
        return jsonify({"code": Cache})
@app.route(f'/get_files/<path:filename>', methods=['GET'])
def custom_static(filename):
    global Cache,thre2,thre
    ip_address = request.remote_addr
    ipC = Ipjudge(ip_address)
    if ipC:
        return ipC[0]
    if config["SingleUpload"]:
        return render_template("end.html",title="服务器已设置只允许文件上传")
    if not config["download"]:
        return render_template("end.html",title="服务器禁止下载文件")
    config["log"]["download"].append(f"{datetime.now()}->{request.remote_addr}下载了{filename}")
    if not os.path.exists(config["FileCataloguePath"]+'/'+filename):
        Cache = None
        if not thre2.is_alive() and not thre.is_alive():
            thre2 = threading.Thread(target=UpCache,args=())
            thre2.start()
        return "文件不存在,服务器正在更新数据中,请返回刷新页面"
    return send_from_directory(config["FileCataloguePath"],filename,as_attachment=True)

@app.route('/downloadzip/<path:filename>')
def download_zip(filename):
    ip_address = request.remote_addr
    ipC = Ipjudge(ip_address,'无权限',0)
    if ipC:
        return ipC[0]
    if not config["download"]:
        return render_template("end.html",title="服务器禁止下载文件")
    # 1. 定义要压缩的文件夹路径
    folder_path = config["FileCataloguePath"]+"/"+filename  # 修改为你的目标文件夹
    if not os.path.exists(folder_path):
        return jsonify({"code": "文件夹不存在",'msg':0})
    total = 0
    for path in Path(folder_path).rglob('*'):
        if path.is_file() and not path.is_symlink():  # 跳过符号链接
            total += path.stat().st_size
    if round(total / (1024*1024*1024), 2) > float(config["download_Dir"]):
        return jsonify({"code": "文件夹大小超过"+str(config["download_Dir"])+"GB",'msg':0})
    print(f"压缩文件大小：{round(total / (1024*1024*1024), 2)}GB,限制{config['download_Dir']}GB")
    
    # 2. 在内存中创建 ZIP 文件
    memory_buffer = BytesIO()
    
    # 3. 压缩文件夹到内存
    with zipfile.ZipFile(memory_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                # 计算 ZIP 内的相对路径
                arcname = os.path.relpath(file_path, folder_path)
                zipf.write(file_path, arcname=arcname)
    
    # 4. 重置指针位置（关键步骤！）
    memory_buffer.seek(0)

    # 5. 发送 ZIP 数据流
    return send_file(
        memory_buffer,
        mimetype='application/zip',
        as_attachment=True,
        download_name=filename + '.zip'
    )

@app.route('/shutdown')
def shutdown():
    # 关闭服务器
    adminis = session.get('username')
    if not adminis:
        return redirect(url_for('get_log'))
    lockf(False,True)
    os._exit(0)  # 强制退出程序

@app.route('/config', methods=['GET', 'POST'])
def config_server():
    user = session.get('username')
    if not user:
        return redirect(url_for('get_log'))
    return render_template("config.html", config=config)

@app.route('/set_config', methods=['POST'])
def set_config():
    if not session.get('username'):
        return jsonify({'code': '请先登录','msg':0})
    jsondata = request.get_json()
    filepathif = jsondata.get('FileCataloguePath')
    dirpathif = jsondata.get('SysCataloguePath')
    asyncMax = jsondata.get('asyncMax',None)
    if asyncMax == '' and asyncMax != None:
        return jsonify({'code': '异步上传最大值不能为空','msg':0})
    
    if filepathif:
        if not os.path.exists(filepathif.replace(' ','')):
            return jsonify({"code":"文件目录不存在,请重新选择"})
    if dirpathif:
        if not os.path.exists(dirpathif.replace(' ','')):
            if is_valid_path(filepathif.replace(' ','')):
                pass
            else:
                return jsonify({"code":"下载目录不合法,请重新选择"})
    for key in jsondata:
        config[key] = jsondata.get(key)
        print(f"修改配置：{key}={config[key]}")
    
    print(config)
    return jsonify({"code":"OK"})
@app.route('/log', methods=['GET', 'POST'])
def get_log():
    if session.get('username'):
        return redirect(url_for('config_server'))
    if request.method == 'GET':
        return render_template("login2.html", error="")
    elif request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        new_password = request.form.get('new_password')
        if username == admin["username"] and password == admin["password"]:
            if new_password:
                print(f"修改密码：{new_password}")
                admin["password"] = new_password
            session['username'] = username
            return redirect(url_for('config_server'))  # 重定向到配置页面
        else:
            return render_template("login2.html", error="用户名或密码错误")
@app.route('/logout', methods=['GET'])
def logout():
    session.clear()
    return render_template("login2.html")

@app.route('/port', methods=['GET','POST'])
def port():
    if request.method == 'POST':
        return jsonify(monitor_bandwidth(get_port_process()))
    else:
        return jsonify(monitor_bandwidth(get_port_process()))

@app.route('/dataup', methods=['POST'])
def dataup():
    ip_address = request.remote_addr
    ipC = Ipjudge(ip_address)
    if ipC:
        return ipC[0]
    global Cache,thre,thre2
    if thre.is_alive() or thre2.is_alive():
        return jsonify({'code': '服务器已在更新中,请稍后再试','msg':0})
    elif not thre.is_alive() and not thre2.is_alive():
        Cache = None
        thre = threading.Thread(target=CacheGet,args=())
        thre.start()
        return jsonify({'code': '更新完毕,即将为你刷新页面','msg':1})
    else:
        return jsonify({'code': 'fatal error','msg':1})

@app.route('/save_config', methods=['POST'])
def save_config():
    if not session.get('username'):
        return jsonify({'code': '请先登录','msg':0})
    global config
    lockf(False,True)
    with open('FilleTransferConfig.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=4)
    lockf(True)
    return jsonify({'code': '保存成功','msg':1})

@app.route('/drop_config', methods=['POST'])
def drop_config():
    global config_readif
    if not session.get('username'):
        return jsonify({'code': '请先登录','msg':0})
    if os.path.exists('FilleTransferConfig.json'):
        lockf(False,True)
        config_readif = False
        os.remove('FilleTransferConfig.json')
        return jsonify({'code': '删除成功','msg':1})
    else:
        return jsonify({'code': '文件不存在','msg':0})
if __name__ == '__main__':
    check_port('localhost',5000,False)
    SysTrayIcon().start_icon()
    root = tk.Tk()
    root.withdraw()
    config_readif = config_read()
    lock = None
    if not config_readif:
        while True:
            root.attributes('-topmost', True)
            root.update()
            filepath = filedialog.askdirectory(title="选择一个文件作为下载目录,或直接关闭窗口跳过",parent=root)
            root.attributes('-topmost', False)
            root.update()
            if start(filepath):
                root.destroy()
                break
    else:
        lockf(True)
        open_browser()
    check_port('localhost',5000)
    app.run(debug=False,port=5000,host='0.0.0.0')