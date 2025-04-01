import os
from pathlib import Path
import time
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
        else:  # 如果是文件
            structure["files"].append(item)

    return structure
# start = time.time()
# print(build_folder_structure("C:/Users/Administrator/Desktop"))
# end = time.time()
# print(f"总耗时: {end - start:.2f}秒")
# # 示例用法
# folder_path = "C:/Users/Administrator/Desktop/其他"  # 替换为你的文件夹路径
# structure = build_folder_structure(folder_path)
# print(structure)

# import psutil
# import time
# def get_port_process(port=5000):
#     for conn in psutil.net_connections():
#         if conn.laddr.port == port and conn.status == 'LISTEN':
#             return psutil.Process(conn.pid)  # 返回进程对象‌:ml-citation{ref="3,4" data="citationList"}

# process = get_port_process()
# def monitor_bandwidth(process, interval=1):
#     io_start = process.io_counters()
#     time.sleep(interval)
#     io_end = process.io_counters()
#     return {
#         "sent_KB/s": (io_end.write_bytes - io_start.write_bytes) / 1024 / interval,
#         "recv_KB/s": (io_end.read_bytes - io_start.read_bytes) / 1024 / interval
#     }  # 需持续调用‌:ml-citation{ref="3,4" data="citationList"}

# # # 示例用法
# while True:
#     print(monitor_bandwidth(process))
#     time.sleep(1)


# import pystray
# from PIL import Image, ImageDraw
# import threading

# class CustomSysTrayIcon:
#     def __init__(self):
#         # 创建自定义图标
#         self.icon_image = self.create_custom_icon()
#         # 创建菜单
#         self.menu = (
#             pystray.MenuItem('选项1', self.on_clicked),
#             pystray.MenuItem('选项2', self.on_clicked),
#             pystray.MenuItem('退出', self.sys_stop)
#         )
#         # 创建系统托盘图标
#         self.icon = pystray.Icon("my_app", self.icon_image, "我的自定义应用", self.menu)
#         # 用于控制线程退出的标志
#         self.stop_event = threading.Event()

#     # 创建自定义图标
#     def create_custom_icon(self):
#         image = Image.new('RGBA', (64, 64), (255, 255, 255, 0))  # 透明背景
#         draw = ImageDraw.Draw(image)
#         draw.ellipse((10, 10, 54, 54), fill='blue', outline='white')
#         draw.text((20, 20), "Py", fill='white')
#         return image

#     # 菜单项回调函数
#     def on_clicked(self):
#         print("菜单项被点击")

#     # 停止系统托盘图标
#     def sys_stop(self):
#         print("正在退出程序...")
#         self.icon.stop()
#         self.stop_event.set()

#     # 启动系统托盘图标
#     def start(self):
#         self.icon.run()

# # 启动系统托盘图标
# if __name__ == "__main__":
#     tray_icon = CustomSysTrayIcon()
#     # 使用多线程运行系统托盘图标
#     tray_thread = threading.Thread(target=tray_icon.start, daemon=True)
#     tray_thread.start()

#     # 模拟主程序运行
#     try:
#         while not tray_icon.stop_event.is_set():
#             print("主程序运行中...")
#             threading.Event().wait(5)  # 模拟主程序每隔5秒执行一次
#     except KeyboardInterrupt:
#         print("主程序已退出")


# import tkinter as tk
# from tkinter import messagebox
# import threading
# from PIL import Image, ImageTk,ImageDraw
# import pystray



# class CustomTrayIcon:
#     def __init__(self):
#         # 创建自定义图标
#         self.icon_image = self.create_custom_icon()
#         # 创建系统托盘图标
#         self.icon = pystray.Icon("my_app", self.icon_image, "我的自定义应用")
#         # 创建 Tkinter 根窗口（隐藏）
#         self.root = tk.Tk()
#         self.root.withdraw()  # 隐藏主窗口
#         # 创建自定义菜单
#         self.create_custom_menu()

#     # 创建自定义图标
#     def create_custom_icon(self):
#         image = Image.new('RGBA', (64, 64), (255, 255, 255, 0))  # 透明背景
#         draw = ImageDraw.Draw(image)
#         draw.ellipse((10, 10, 54, 54), fill='blue', outline='white')
#         draw.text((20, 20), "Py", fill='white')
#         return image

#     # 创建自定义菜单
#     def create_custom_menu(self):
#         self.menu = tk.Menu(self.root, tearoff=0, bg='black', fg='white', font=('Arial', 10))
#         self.menu.add_command(label="选项1", command=self.on_option1)
#         self.menu.add_command(label="选项2", command=self.on_option2)
#         self.menu.add_separator()
#         self.menu.add_command(label="退出", command=self.sys_stop)

#     # 显示自定义菜单
#     def show_custom_menu(self):
#         try:
#             self.menu.tk_popup(self.root.winfo_pointerx(), self.root.winfo_pointery())
#         finally:
#             self.menu.grab_release()

#     # 菜单项回调函数
#     def on_option1(self):
#         messagebox.showinfo("提示", "你点击了选项1")

#     def on_option2(self):
#         messagebox.showinfo("提示", "你点击了选项2")

#     # 停止系统托盘图标
#     def sys_stop(self):
#         self.icon.stop()
#         self.root.quit()

#     # 启动系统托盘图标
#     def start(self):
#         self.icon.run()

# # 启动系统托盘图标
# if __name__ == "__main__":
#     tray_icon = CustomTrayIcon()
#     # 使用多线程运行系统托盘图标
#     tray_thread = threading.Thread(target=tray_icon.start, daemon=True)
#     tray_thread.start()

#     # 模拟主程序运行
#     try:
#         while True:
#             tray_icon.root.update()  # 更新 Tkinter 事件循环
#     except KeyboardInterrupt:
#         print("主程序已退出")


# a = open("C:/Users/Administrator/Desktop/其他/服务器/局域网文件互传/1.txt",'w')
# print(a)
# a.close()
# print(a)
from pathlib import Path
import re

def is_valid_directory_path(path):
    # 1. 基础检查
    if not isinstance(path, str) or not path.strip():
        return False
    if re.search(r'[:*?"<>|\0]', path):
        return False

    # 2. 解析路径
    try:
        path_obj = Path(path)
    except Exception:
        return False

    # 3. 检查文件路径特征（精确后缀匹配）
    last_part = path_obj.name
    if "." in last_part:
        common_file_exts = {".txt", ".zip", ".exe", ".pdf"}  # 自定义扩展列表
        if any(last_part.lower().endswith(ext) for ext in common_file_exts):
            return False

    # 4. 禁止相对路径跳转
    if not path_obj.is_absolute() and ".." in path_obj.parts:
        return False

    return True

print(is_valid_directory_path("C:/Users/Administrator/Desktop/其他/服务器/局域网文件互传"))