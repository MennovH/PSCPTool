import datetime as dt
import io
import os
import re
import subprocess as sp
import sys
import threading
import time
import tkinter as tk
import webbrowser as wb
from io import StringIO
from ipaddress import ip_address
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from pexpect import EOF, TIMEOUT, popen_spawn
from PIL import Image, ImageTk
from pyperclip import copy, paste

__author__ = "MennovH"
__version__ = "1.0.7"
__status__ = "Production"

# hide python console window (.pyw extension breaks functionality)
try:
    import win32con
    import win32gui
    frgrnd_wndw = win32gui.GetForegroundWindow()
    wndw_title  = win32gui.GetWindowText(frgrnd_wndw)
    if wndw_title.endswith("py.exe") or wndw_title.endswith("python.exe"):
        win32gui.ShowWindow(frgrnd_wndw, win32con.SW_HIDE)
except:
    pass


def known_hosts():
    hosts = []
    try:
        tmp_hosts = sp.check_output('more %USERPROFILE%\\.ssh\\known_hosts', shell=1).decode().split()
    except:
        tmp_hosts = []

    if len(tmp_hosts) > 0:
        for host in tmp_hosts:
            try:
                if ']:' in host:
                    hosts.append(host[host.index('['):].replace('[', '').replace(']', ''))
                elif ip_address(host):
                    hosts.append(f'{host}:22')
            except:
                continue
        hosts = sorted(list(set(hosts)))
    return hosts


def alert(header, message, icon, default='no'):
    # create and show messagebox
    try:
        pop_up = tk.Tk()
        pop_up.withdraw()
        if icon == 'error':
            result = messagebox.showerror(header, message, icon=icon)
        else:
            result = messagebox.askquestion(header, message, icon=icon, default=default)
        pop_up.destroy()
    except:
        result = 2
    return result


def validate_ip(IP: str) -> str:
    # validate IP address
    try: return isinstance(type(ip_address(IP)), type)
    except ValueError: return False


def convert_to_timestamp(seconds):
    # convert seconds to timestamp
    seconds = seconds % (24 * 3600)
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    return "%d:%02d:%02d" % (hour, minutes, seconds)


def convert_to_seconds(timestamp):
    # convert timestamp to seconds
    h, m, s = timestamp.split(':')
    try:
        h=int(h)*3600
        m=int(m)*60
        s=int(s)
    except:
        return 150
    return s+m+h


def set_basepath(path=None):
    # set local path
    if path is not None:
        if (os.path.isdir(path) or os.path.isfile(path)) and path is not None:
            # return current path value
            return path
    
    # return the path of the compile if compiled else return path of script
    return os.path.split(sys.executable)[0] if hasattr(sys, 'frozen') else os.path.dirname(os.path.realpath(__file__))


class windows(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        # create startupinfo for hidden subprocess(es)
        self.startupinfo = sp.STARTUPINFO()
        self.startupinfo.dwFlags = sp.CREATE_NEW_CONSOLE | sp.STARTF_USESHOWWINDOW
        self.startupinfo.wShowWindow = sp.SW_HIDE
        
        try:
            # locate PSCP in native directory
            self.pscp = sp.check_output('where /r "c:\program files\" pscp', startupinfo=self.startupinfo)
            if self.pscp:
                self.pscp = self.pscp.decode().replace('\r', '').replace('\n', '')
        except:
            if os.path.isfile(r'..\PuTTY\pscp.exe'):
                self.pscp = r'..\PuTTY\pscp.exe'
            else:
                self.pscp = 'pscp.exe'

        # set GUI layout including controls
        self.wm_title(f"PSCPTool - v{__version__}")
        self.geometry('400x446')

        self.icon = ImageTk.PhotoImage(Image.open(io.BytesIO(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00 \x00\x00\x00 \x08\x06\x00\x00\x00szz\xf4\x00\x00\x00\x01sRGB\x00\xae\xce\x1c\xe9\x00\x00\x00\x04gAMA\x00\x00\xb1\x8f\x0b\xfca\x05\x00\x00\x00\tpHYs\x00\x00\x0e\xc3\x00\x00\x0e\xc3\x01\xc7o\xa8d\x00\x00\x01%IDATXG\xc5\x92a\x12\x85 \x08\x84=zG\xebf\xbdV\xc0\xd0\xc1\x12\xa5\xde7\xb3\x93"\xec\xf2\xa3\x14\xc0\xe1T(\xc7\xbe\xef\xc3\xda\xb6-t\x89c\x14\t\x7fe\x81\x94`z\xaf\x0f\x16\xc0\xb7\xaf?,\x90C\xca\xfd\xe3\x05P\xff\xcb\x02\x14\xda\x86C\x1f,@\xc1V8\xf4\xf2\x02\xf8\x92p\xc6\xb5\xd5k\x0b@\x08\x86\xe8lc, \x9a\xe6\xb4\xad\xc3%\xe0N\xe8\xc32@\xee0\xf3R\x82%|T:|f\x81<\xa0\xc3{\xa2>\x9b\xd9\xff\xe1\x1c}\x16\xfa \x84\xf4$\xe1z\x812\xe8U\x1b\xaeC\xda^\xd4\xf4\x02\\\xcf\x9c\x06>h\xa6\x0e\x17\xe3\x11\xa1\x1f\xc1\x02<\xa5X\xd4\x83\xde\xae\xe0IUd\xe3\x11\xa8\xb7\n\x0f\xa1\x98[\x12\xe8\\\x85C!\xe4\x80;\xa8\xa7^\x8a\xcf!dC\x01w]\xa3s]\x03\xdc\x17\x02[\xda\xe0\xdd\xea\xe1z\x08ly\x85\x89\xee\xe0\x9e\x10\xd8\xd2\x07\xe6h|\x1dm\xf8(\x81\xef!\xb0\xa5\x0f\xcc\xd1\xf8:\xda\xd0\x94\x05\xbf\x85\xc0\x96>0G\xe3\xeb\xb0\xe5\x05j\x964\\\x0b\x81-}`\x8e\xc6\xd7\x11\xb3\x19-\x92\xd2\x0f\xd8F0uC\xc6\x9b\x88\x00\x00\x00\x00IEND\xaeB`\x82')))
        self.iconphoto(False, self.icon)

        self.keyImage = ImageTk.PhotoImage(Image.open(io.BytesIO(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x12\x00\x00\x00\x11\x08\x06\x00\x00\x00\xd0Z\xfc\xf9\x00\x00\x01SIDAT8Ocd\xa0\x12`\xa4\x929\x0c\x03c\x90|\xc9N\'\xc6\x7f\xffK\x81\xbe\xf0\xf8\xcf\xf0\x7f\xc9\xc3>\xcfX\x98\x8f\x88v\x91B\xe1\xf6\x08\x06\x06\xc6R\xa0\x1f\x8c\xa0\x9a\'<\xe8\xf3($\xc9 \x85\xa2\xed\t\xff\x19\x18g\x03me\x01j|\xc1\xf0\xef\x7f$\x90~\xf0`\x82\xe7\x03\xbc\x06I\xe7n\x93aec\xe6y\xd0\xeb~C\xbexg3\xe3\xff\xff5@\r?\x18\xfe3\x9c\xf8\xcf\xc4\xf8\xe6a\xaf{(z$\xa1x\rd\x00\x0b\x1bs?\xc3\xff\xff\x01P\xdb\xe1\xea\xff30\x1cy\xd8\xe7a\x8b+\x96\x11\x065\xecgQ\xf8\xfc\xf34\xd0V\x03t\xc5@C\xbe\xfc\xff\xf7/\xf1\xd1\x04\xaf5\x04\r\x92+\xdc\xe1\xc2\xc4\xc8\xb0\x1b\xa8\xe9\x0f\xd0\xf4;@\r\x1a0M\xff\x19\x19[\x80\xde\xa9\xc5\x97\xe6\xe0.\x02\x05(0V\xe630\xfc+|\xd0\xe75A\xa1x\xe7r\xa0\x17\x811\x05\x02\x8c\r\x0f\xfa\xdc\x1b\x892H\xaex\xbb\r\xd3\x7f\xc6\xc3\xc0\xd8Y\xf2\x8f\x89\xa1\x93\xf9\xff\xff\xc5po\xfeg\xf0|\xd0\xef\xb1\x83(\x83@\x8a\x801\xb4\x1a\x18C!\xc8\x1a\x80\xdeZ\x83-\x96\xf0\xc6\x1a\xd8\xb0\xc2\x1d9\x8c\x8c\x0c\xde\xe0\xb0\xfa\xcf\xb0\xf5\x01?\xfb\x1c\x86\x06\xc7?\x84\xf2$\xd1){\xe8\x19\x04\x00\xc2\x1eq\x12n\xc2\xbf\xe5\x00\x00\x00\x00IEND\xaeB`\x82")))
        self.fileImage = ImageTk.PhotoImage(Image.open(io.BytesIO(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x0f\x00\x00\x00\x0f\x08\x06\x00\x00\x00;\xd6\x95J\x00\x00\x00BIDAT(Scd\x80\x80\xffP\x1a\x1b\xc5\x88K\x0e&AH3H\x1e\xc3\x10R4\x83\x1c\x80b\x00\xa9\x9aQ\x0c V3Vo\x13\xa3\x19g \x8ej\xc6\x93\xcc\xd0\xa4\xc0a5\xc4\x03\x8cx\xdf"\xa9\x04\x00\xdd\xf3\x11\x10)1\x98\xd9\x00\x00\x00\x00IEND\xaeB`\x82')))
        self.folderImage = ImageTk.PhotoImage(Image.open(io.BytesIO(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x0f\x00\x00\x00\x11\x08\x06\x00\x00\x00\x02\n\xf6\xa1\x00\x00\x00uIDAT8Ocd\xa0\x000R\xa0\x97\x81r\xcdb\r\x7f\x02\xfe\xfd\xfb\xaf\x8f\xee\x8a7M\xac\x8d\xf8\\\x06\xb6Y\xb4\xee\xf7\x7fl\x8a^7\xb1\xe2u\x19^\xcd@\x13\x1b\xb0\x19\ns\x11^\xcd\xb8\x9c\xcc\xc8\xc8\xf8\xebU#\x0b;Y\x9aA\x86\x82\xbc4\xaa\x99\x84\xb4Jv\x80\x01\xe3\xff\x170\xae!Q%\\\xf7\xc7\x9f\x91\xe1\xbf\x01\xb1\x16\xa3$\x12b5\xa1\xab\xa3(W\x01\x00\xbe\x929\x12yk_\xb3\x00\x00\x00\x00IEND\xaeB`\x82')))
        self.listDir = ImageTk.PhotoImage(Image.open(io.BytesIO(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\r\x00\x00\x00\r\x08\x06\x00\x00\x00r\xeb\xe4|\x00\x00\x00\x01sRGB\x00\xae\xce\x1c\xe9\x00\x00\x01\x9fIDAT(SE\x92Qr\xd30\x10\x86\xff\x95\xdci\x87\\B\xdc\xc0M\xe93qxb8\x04\xf19Hb\x8b&\xe7H.A\xf2f\xcb\xcfM\xd2\xe1\x04\xf5%``\x82v\x19I6\xe8i\xed\xd5\xfe\xfb\xef\xb7"\x8c\x87\x80\xc7MW\xfd\xf1<SZ\x19\x11v\xc4\xd2]\xd6\x1f\xf6B\x02\xc8p\x91\x08\x04"\xe4\xf57\xa3\xf5\xa4U\x84=\x98\xbb+\xff\xea5\xdd\xcdD\xa9\x8a\xe0\xddy9/C\t\x11 \x12\x8b\x80\xdc6mF\xb0\xa7\xf5\xdc\x05\xd1\x94\x05\xf2\xfa`D\xdf\xee2\xd2\xee\xb4\x9c\xd9\xf0;$h\xfa\xb5Y\x08\xd1\xe7\x97UQ\x04\x05\t\xb7\t Iqn\x0fFg\x93\xf6\xbc|\xff6&b\xd1\xa6\xd9\x81\xa9\xbb\xac\x8b=\xd1P\x14\xebB\x1c\xba\n\xeem\xdbj\xc0\x9e\xd7\x85\x93\x90\xc9\x9f\x9a\xf6F\xc8>W\x85\x1b\xd5G\xc5\xd4\x12H\xc2\tJ\xec\xf4\xb8\xed*\x0fo._\xe6e\xb4\x9c\xc6\x89\xf6Fd\xd3m\xf7\xca\xd7\x1f\xc5\x8b\xfd\xd4C\x04to\x8f\x86\xb27-_\x7f\x16\xdf\xeb\x8f}\x80\x10\xe7\n6D\xf0\xb0\xed*\x166\x97\x81`\xec\x14\xbcO\x9f\x9a\x05\x02^\xe6\xf2\xb4*\xdc\xb8\xbaw\x9b\xae\x12\xa0\x06\xfc~\xc4\x1e\x1dG\x13aW\xd5\xc1\x90\xbe\xdb)\xa5\x0c\xb3\xef\x15\xa9\x19\x0b\xbb\x80\xdbCj\x02\xf5$\\\x9eW\x85\x0b\xc0\x86e\xa7\x19\xf2\xfahn\xd4\xady^\xcdc\xc7\x80\\\xe9I\x0b\xc0\x88x\'\xfew\x19\x97\xfb\xff\x89\x8c\xf1\x00|\x10\xcc\xabct\x91)\xe5<\xb0\x88\xc0\xe2It\x03\x9c\x7f\xdfq\xcf\xf1\xe9\xa4\xfc\xc3\xc6\xbd\x82\xc5\xfe\x05\x9d}\xcc\xcbk]\xc9\xd8\x00\x00\x00\x00IEND\xaeB`\x82')))
        self.refreshImage = ImageTk.PhotoImage(Image.open(io.BytesIO(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x0b\x00\x00\x00\r\x08\x06\x00\x00\x00\x7f\xf5\x94;\x00\x00\x00\x01sRGB\x00\xae\xce\x1c\xe9\x00\x00\x01YIDAT(SERAN\x02A\x10\xac\x9a\xf9\xc8\x1e\x16\x03w\x1f\xb0<C!\x8aW=\xf8\x04\x97/\xf8\x01Ld\xc1\x0fx\xf0\x04\x0f\xf0\x03\x08*\xc6\x07\x98x3\xb2]\xa6g \xcea&\xe9\xae\xea\xae\xea\x1e\x82\x00\x85t\xd2C\xa0so\n\xc4S+^n\x86\xe1-g\x012\xa1\x01\t\xe8\xcd\xad\xf85U\x04\'\x99\xac\xefH\\\xad\x06a\xba\xaf\x93Y\xdd\x99\xaa\x9di\xe1L:\xd9+\xa5\x0b\x1ff\xbaz;\x8b\x8f\x1eO\xc0_a\xc1\x0c\xa9\x05\xd5\x1e\x07\xf8\xf0#\\~\x0e\xf9\x95y$:3[\xc0P\xc5\x80\xfe\xea$,\xcb\xa6\xf5\xdc\xf5f\x10o\xb3\x0f\xa5V\xec\xce\xacj\xc5\x05\x88\xe5\xe64\xf4=z4\xb3\xe3\x97Ax\x96\xd7\xca\xb6s\x9f\xb2\xd1\x88\x80\x1b\xba\xdb\x0cx\xe1\x9d\xdc,\xa9\x0c\xd3\xff\xb8XN\xed\x06d\r\xa1~\x1d\x86\xf1\x7f>\x83I\xa2\x9c\xda\x08\xc49\xdd\\+%\x19\xeb\xd3\x98d$+\xfb\xc9\xbb\x94Nc\x13\x08#\xf6\xe6*v\x86w\xc7\xc4\xa8\xfe\xea$.E\x1d<%J\xd9\x98\xa8}\x81\xa4[\x9a0b+s\xedq\xec\xe8n\xa3bGL\x94\x17\x95\xc7\xd9\x9d\xabh\r\xe7\x90j7\x18\x88m+\x14\x9e\x94\x04\x06\xa6I\xa5\xa5\x1c\xfeD9\xd5\r\x83*\xb4\xac\xd2/\xa0\xb6\x12\xef\xd6C\x8e\x1d\xf7\x07\xb4\xc9\xb4y\xe9:\xa3\x98\x00\x00\x00\x00IEND\xaeB`\x82")))

        self.action_selection_label = ttk.Label(self, text='Action')
        self.action_selection = ttk.Combobox(self, textvariable='', values=['Download from remote host', 'Upload to remote host'], state='readonly')
        self.action_selection.set('Download from remote host')

        self.set_timeout_label = ttk.Label(self, text='Timeout (h:m:s)')
        self.set_timeout = ttk.Combobox(self, textvariable='', values=[f'{convert_to_timestamp(tm*10)}' for tm in range(1, 721)], state='readonly')
        self.set_timeout.set('0:02:30')

        self.remote_host_label = ttk.Label(self, text='Remote host IP address or FQDN')
        
        self.remote_host = ttk.Combobox(self, textvariable='', values=known_hosts())
        self.refresh_remote_host = tk.Button(self, image=self.refreshImage, command=self.refresh_remote_hosts, cursor='hand2', takefocus=0)

        self.remote_host_port_label = ttk.Label(self, text='Port')
        self.remote_host_port = ttk.Entry(self, show='', foreground='Black')
        self.remote_host_port.insert(0, 22)

        self.remote_host_username_label = ttk.Label(self, text='Remote host username')
        self.remote_host_username = ttk.Entry(self, show='', foreground='Black')
        self.remote_host_password_label = ttk.Label(self, text='Remote host password')
        self.remote_host_password = ttk.Entry(self, show='*', foreground='Black')

        self.putty_private_key_label = ttk.Label(self, text='Putty Private Key (PPK)')
        self.putty_private_key = ttk.Entry(self, show='', foreground='Black')

        self.remote_label = ttk.Label(self, text='Remote path of file or directory')
        # self.remote_folder = ttk.Entry(self, show='', foreground='Black')
        
        self.remote_folder = ttk.Combobox(self, textvariable='', values=[])
        self.listdir_button = tk.Button(self, image=self.listDir, command=self.listdir, cursor='arrow', takefocus=0, state='disabled')

        self.local_label = ttk.Label(self, text='Local path of file or directory')
        self.local_label_item = ttk.Label(self, text='Directory set (open)', cursor='hand2')
        self.local_label_item.config(foreground='RoyalBlue3')
        self.local_folder = ttk.Entry(self, show='', foreground='Black')
        
        self.local_folder.insert(0, set_basepath())
    
        self.file_button = tk.Button(self, image=self.fileImage, command=self.set_file_path, cursor='hand2', takefocus=0)
        self.folder_button = tk.Button(self, image=self.folderImage, command=self.set_folder_path, cursor='hand2', takefocus=0)
        self.ppk_button = tk.Button(self, image=self.keyImage, command=self.set_key_path, cursor='hand2', takefocus=0)
        
        self.style = ttk.Style()
        self.style.configure('TButton', foreground='black')
        self.run_button = ttk.Button(self, text='Download item(s)', command=self.run, state='disabled', takefocus=0)

        self.checkbox_var = tk.IntVar(value=1)
        self.recursive_checkbox = ttk.Checkbutton(self, text='Recursive', variable=self.checkbox_var, onvalue=1, offvalue=0)
        
        self.status_label = ttk.Label(self, text='', foreground='RoyalBlue3', anchor=tk.CENTER)

        columns = ['Time', 'Action', 'File or folder', 'Status']
        self.log = ttk.Treeview(self, show='headings', columns=columns, height='6', selectmode='browse', takefocus=0)

        for k in columns:
            self.log.heading(column=f'{k}', text=f'{k}',anchor='w')
            self.log.column(column=f'{k}', width=64 if k in ['Action'] else 52 if k in ['Time'] else 112 if k in ['Status'] else 144, minwidth=5, stretch=False)
        
        self.log.column(column='#0', width=0)
        
        device_scrollbar = ttk.Scrollbar(self, orient='vertical', command=self.log.yview)
        self.log.configure(yscrollcommand=device_scrollbar.set)

        # set bindings to controls
        self.action_selection.bind('<<ComboboxSelected>>', self.action_selection_warning)
        self.remote_host.bind('<FocusOut>', self.validate_remote_ip)
        self.remote_host.bind('<KeyRelease>', self.validate_remote_ip1)
        self.remote_host.bind('<<ComboboxSelected>>', self.validate_remote_ip2)
        self.local_folder.bind('<KeyRelease>', self.validate_input)
        self.remote_host_port.bind('<KeyRelease>', self.validate_port)
        self.remote_host_username.bind('<KeyRelease>', self.validate_input)
        self.remote_host_password.bind('<KeyRelease>', self.validate_input)
        self.remote_folder.bind('<KeyRelease>', self.validate_input)
        self.remote_folder.bind('<<ComboboxSelected>>', self.validate_input)
        self.local_folder.bind('<KeyRelease>', self.validate_local_path)
        self.putty_private_key.bind('<KeyRelease>', self.validate_key_path)

        self.local_label_item.bind('<Button-1>', self.open_file_folder)
        self.remote_host_username.bind('<Button-3>', lambda event: self.copy_paste_pass(event, 'Username'))
        self.remote_host_password.bind('<Button-3>', lambda event: self.copy_paste_pass(event, 'Password'))
        self.remote_host.bind('<Button-3>', lambda event: self.copy_paste_pass(event, 'Remote IP address'))
        self.remote_folder.bind('<Button-3>', lambda event: self.copy_paste_pass(event, 'Remote path'))
        self.local_folder.bind('<Button-3>', lambda event: self.copy_paste_pass(event, 'Local path'))
        self.putty_private_key.bind('<Button-3>', lambda event: self.copy_paste_pass(event, 'PuTTY PPK'))

        self.remote_host.bind('<Return>', self.run)
        self.local_folder.bind('<Return>', self.run)
        self.remote_host_port.bind('<Return>', self.run)
        self.remote_host_username.bind('<Return>', self.run)
        self.remote_host_password.bind('<Return>', self.run)
        self.remote_folder.bind('<Return>', self.run)
        self.recursive_checkbox.bind('<Return>', self.run)

        # set placement of controls
        self.action_selection_label.place(x=5, y=2, width=289)
        self.action_selection.place(x=5, y=20, width=289)
        self.set_timeout_label.place(x=295, y=2, width=100)
        self.set_timeout.place(x=295, y=20, width=100)
        
        self.status_label.place(x=125, y=1, width=150)

        self.remote_host_label.place(x=5, y=44, width=289)
        self.refresh_remote_host.place(x=275, y=44, width=19, height=19)
        self.remote_host.place(x=5, y=62, width=289)
        self.remote_host_port_label.place(x=295, y=44, width=100)
        self.remote_host_port.place(x=295, y=62, width=100)

        self.remote_host_username_label.place(x=5, y=86, width=195)
        self.remote_host_username.place(x=5, y=104, width=195)
        self.remote_host_password_label.place(x=200.5, y=86, width=194)
        self.remote_host_password.place(x=200.5, y=104, width=194)

        self.putty_private_key_label.place(x=5, y=128, width=390)
        self.putty_private_key.place(x=5, y=146, width=390)
        self.ppk_button.place(x=376, y=128, width=19, height=19)

        self.remote_label.place(x=5, y=170, width=390)
        self.remote_folder.place(x=5, y=188, width=390)
        self.listdir_button.place(x=376, y=170, width=19, height=19)

        self.local_label.place(x=5, y=212, width=195)
        self.local_label_item.place(x=200.5, y=212, width=144)
        self.local_folder.place(x=5, y=230, width=390)

        self.file_button.place(x=357, y=212, width=19, height=19)
        self.folder_button.place(x=376, y=212, width=19, height=19)

        self.recursive_checkbox.place(x=5, y=262, width=195)
        self.run_button.place(x=200.5, y=260, width=195)

        self.log.place(x=5, y=294, width=390)
        device_scrollbar.place(x=377, y=295, height=145)


    def colors(self, param=None):
        warning_color = 'darkorange'
        action = 'Download' if self.action_selection.get() == 'Download from remote host' else 'Upload'
        for label in filter(lambda w:isinstance(w,ttk.Label), self.children.values()):
            if action == 'Download':
                label.config(background='SystemButtonFace')
            else:
                label.config(background=warning_color)

        if action == 'Download':
            self.config(bg='SystemButtonFace')
            self.style.configure("TCheckbutton", background="SystemButtonFace", foreground="black")
            self.local_label_item.config(background='SystemButtonFace', foreground='RoyalBlue3')
        else:
            self.config(bg=warning_color)
            self.style.configure("TCheckbutton", background=warning_color)
            self.local_label_item.config(background=warning_color, foreground='blue')


    def open_file_folder(self, param=None):
        if 'open' in self.local_label_item.cget('text'):
            lf = self.local_folder.get()
            if os.path.isfile(lf):
                os.startfile(lf)
            elif os.path.isdir(lf):
                wb.open(lf)


    def copy_timer(self):
        # countdown for copy action
        try:
            self.counter += 1
            if self.counter > 0:
                value = self.status_label.cget('text').split('copied')[0].rstrip()
                self.status_label.config(text=f'{value} copied ({9 - self.counter})')
                self.status_label.update()
                if self.counter > 9 or self.sig == 1:
                    self.t.cancel()
                    self.stop_timer()
                else:
                    self.t = threading.Timer(1, self.copy_timer)
                    self.t.start()
        except:
            self.stop_timer()


    def stop_timer(self):
        # stops copy_timer
        self.status_label.config(text=f'')
        self.status_label.update()
        copy('')


    def copy_paste_pass(self, event=None, param=None):
        # copy or paste (copied) value
        copied = 0
        if param == 'Username':
            if len(self.remote_host_username.get()) == 0:
                self.remote_host_username.delete(0, 'end')
                self.remote_host_username.insert(0, paste())
                copy('')
                self.validate_input()
            else:
                copy(self.remote_host_username.get())
                copied = 1
        elif param == 'Password':
            if len(self.remote_host_password.get()) == 0:
                self.remote_host_password.delete(0, 'end')
                self.remote_host_password.insert(0, paste())
                self.validate_input()
                copy('')
            else:
                copy(self.remote_host_password.get())
                copied = 1
        elif param == 'Remote IP address':
            if len(self.remote_host.get()) == 0:
                self.remote_host.delete(0, 'end')
                self.remote_host.insert(0, paste())
                self.validate_remote_ip()
                copy('')
            else:
                copy(self.remote_host.get())
                copied = 1
        elif param == 'Remote path':
            if len(self.remote_folder.get()) == 0:
                self.remote_folder.delete(0, 'end')
                self.remote_folder.insert(0, paste())
                self.validate_input()
                copy('')
            else:
                copy(self.remote_folder.get())
                copied = 1
        elif param == 'Local path':
            if len(self.local_folder.get()) == 0:
                self.local_folder.delete(0, 'end')
                self.local_folder.insert(0, paste())
                self.validate_local_path()
                copy('')
            else:
                copy(self.local_folder.get())
                copied = 1
        elif param == 'PuTTY PPK':
            if len(self.putty_private_key.get()) == 0:
                self.putty_private_key.delete(0, 'end')
                self.putty_private_key.insert(0, paste())
                self.validate_key_path()
                copy('')
            else:
                copy(self.putty_private_key.get())
                copied = 1

        self.sig = 1
        try: self.t.cancel()
        except: pass
        if copied:
            self.counter, self.sig = 0, 0
            self.status_label.config(text=param.capitalize() if 'IP' not in param else 'IP address')
            self.t = threading.Timer(1, self.copy_timer)
            self.copy_timer()
        else:
            self.status_label.config(text=f'')
            self.status_label.update()


    def set_key_path(self, param=None):
        # set PPK key path
        path = self.putty_private_key.get()
        filepath=filedialog.askopenfile(initialdir=set_basepath(path), filetypes=[('PuTTY Private Key files', '*.ppk')], title="Select PuTTY PPK file")
        if not filepath:
            filepath = path if os.path.isfile(path) else ''
        else:
            filepath = filepath.name
        self.putty_private_key.delete(0, 'end')
        self.putty_private_key.insert(0, filepath)


    def set_file_path(self, param=None):
        # set local file path
        path = self.local_folder.get()
        filepath=filedialog.askopenfile(initialdir=set_basepath(path), title="Select local file path")
        if not filepath:
            filepath = set_basepath()
        else:
            filepath = filepath.name
        self.local_folder.delete(0, 'end')
        self.local_folder.insert(0, filepath)
        self.validate_input()


    def set_folder_path(self, param=None):
        # set local folder path
        path = self.local_folder.get()
        filepath=filedialog.askdirectory(initialdir=set_basepath(path), title="Select local folder path")
        if not filepath:
            filepath = set_basepath()
        self.local_folder.delete(0, 'end')
        self.local_folder.insert(0, filepath)
        self.validate_input()


    def action_selection_warning(self, param=None):
        # color button based on dropdown selection
        self.colors()
        if self.action_selection.get() == 'Download from remote host':
            self.run_button['text'] = 'Download item(s)'
            self.style.configure('TButton', foreground='Black')
        else:
            self.run_button['text'] = 'Upload item(s)'
            self.style.configure('TButton', foreground='Red')
        self.validate_local_path()


    def refresh_remote_hosts(self, param=None):
        self.remote_host['values'] = known_hosts()


    def validate_remote_ip2(self, param=None):
        if param is not None:
            if param.keysym.lower() in ['tab', 'shift_l', 'shift_r', 'return']:
                return
        rh = self.remote_host.get()
        
        self.remote_host_port.delete(0, 'end')
        try:
            rh2 = rh.split(':')
            self.remote_host.set(rh2[0])
            
            self.remote_host_port.insert(0, rh2[1])
        except:
            self.remote_host.set('')
            self.remote_host_port.insert(0, '22')
        
        self.validate_remote_ip()


    def validate_remote_ip1(self, param=None):
        # validate remote IP address
        if param is not None:
            if param.keysym.lower() in ['tab', 'shift_l', 'shift_r', 'return']:
                return
        rh = self.remote_host.get()
        rh = re.sub('[^0-9\.]', '', rh).replace(' ', '')
        if validate_ip(rh):
            self.remote_host.delete(0, 'end')
            self.remote_host.insert(0, rh)
            self.remote_host.config(foreground='Black' if validate_ip(rh) and rh not in ['0.0.0.0', '127.0.0.1'] else 'Red')
            self.validate_input()


    def validate_remote_ip(self, param=None):
        # validate remote host (IP address and/or FQDN)
        if param is not None:
            if param.keysym.lower() in ['tab', 'shift_l', 'shift_r', 'return']:
                return
        rh = self.remote_host.get()
        rh2 = re.sub('[^0-9\.]', '', rh)
        if rh != rh2 and not validate_ip(rh2):
            rh = rh.replace(';', '')
            try:
                rh3 = sp.check_output(f'nslookup {rh}', startupinfo=self.startupinfo).decode().split(rh)[1]
                rh3 = rh3.replace('Addresses:', '').replace('Address:', '').replace('\t', '').replace('\r', '').replace(' ', '').split('\n')
                for item in reversed(rh3):
                    if item == '' or not validate_ip(re.sub('[^0-9\.]', '', item)):
                        rh3.remove(item)

                if len(rh3) > 1:
                    rh = ' / '.join(rh3)
                    self.remote_host.delete(0, 'end')
                    self.remote_host.insert(0, rh)
                elif len(rh3) == 1 and validate_ip(rh3[0]):
                    rh = rh3[0].replace(' ', '')
                    self.remote_host.delete(0, 'end')
                    self.remote_host.insert(0, rh)
            except:
                pass
        elif validate_ip(rh2):
            rh = rh2.replace(' ', '')
            self.remote_host.delete(0, 'end')
            self.remote_host.insert(0, rh)

        self.remote_host.config(foreground='Black' if validate_ip(rh) and rh not in ['0.0.0.0', '127.0.0.1'] else 'Red')
        self.validate_input()


    def validate_port(self, param=None):
        # validate port number
        if param.keysym.lower() not in ['tab', 'shift_l', 'shift_r', 'return']:
            port = self.remote_host_port.get()
            try:
                int(port.replace(' ', '.'))
                self.remote_host_port.config(foreground='Black')
            except:
                self.remote_host_port.delete(0, 'end')
                port = re.sub('[^0-9]', '', port)
                self.remote_host_port.insert(0, port.replace(' ', ''))
                try:
                    port = int(port)
                    self.remote_host_port.config(foreground='Black')
                except:
                    self.remote_host_port.config(foreground='Red')
            self.validate_input()            


    def validate_input(self, param=None):
        # validate input
        if param is not None:
            if param.keysym.lower() in ['return']:
                return
        rh = self.remote_host.get()
        ru = self.remote_host_username.get()
        rp = self.remote_host_password.get()
        rhp = self.remote_host_port.get()
        rf = self.remote_folder.get()
        lf = self.local_folder.get()
        kp = self.putty_private_key.get()

        try: rhp = int(rhp)
        except: pass
        
        action = 'Download' if self.action_selection.get() == 'Download from remote host' else 'Upload'
        rf_check = 0 if action == 'Download' and len(rf) == 0 else 1

        if os.path.isdir(lf):
            self.local_label_item.config(text = 'Directory set (open)', cursor='hand2')
        elif os.path.isfile(lf):
            self.local_label_item.config(text = 'File set (open)', cursor='hand2')
        elif action == 'Upload':
            self.local_label_item.config(text = 'Nothing set', cursor='arrow')
            self.local_label_item
        elif (os.path.isdir(os.path.dirname(lf)) and \
                not os.path.isfile(lf) and \
                not os.path.isdir(lf)) or (os.path.isdir(lf) or os.path.isfile(lf)):
            self.local_label_item.config(text = 'Nonexistent item set', cursor='arrow')

        if action == 'Upload':
            if os.path.isfile(lf) or os.path.isdir(lf):
                path = 1
            else:
                path = 0
        else:
            if (os.path.isdir(os.path.dirname(lf)) and \
                not os.path.isfile(lf) and \
                not os.path.isdir(lf)) or (os.path.isdir(lf) or os.path.isfile(lf)):
                path = 1
            else:
                path = 0

        if os.path.isfile(kp) or len(kp) == 0:
            key_path = 1
        else:
            key_path = 0

        if validate_ip(rh) and \
            len(ru) > 0 and \
            len(rp) > 0 and \
            key_path and \
            isinstance(rhp, int):
            self.listdir_button['state'] = 'normal'
            self.listdir_button['cursor'] = 'hand2'
            
            if path and rf_check:
                self.run_button['state'] = 'normal'
                self.run_button['cursor'] = 'hand2'
            else:
                self.run_button['state'] = 'disabled'
                self.run_button['cursor'] = 'arrow'
        else:
            self.run_button['state'] = 'disabled'
            self.run_button['cursor'] = 'arrow'
            self.listdir_button['state'] = 'disabled'
            self.listdir_button['cursor'] = 'arrow'


    def validate_key_path(self, param=None):
        # validate PPK path
        key_path = self.putty_private_key.get()
        if len(key_path) > 0:
            if os.path.isfile(key_path):
                self.putty_private_key.config(foreground='Black')
            else:
                self.putty_private_key.config(foreground='Red')


    def validate_local_path(self, param=None):
        # validate local path
        action = 'Download' if self.action_selection.get() == 'Download from remote host' else 'Upload'
        path = self.local_folder.get()
        if action == 'Upload':
            if len(path) > 0:
                if os.path.isfile(path):
                    self.local_folder.config(foreground='Black')
                    self.local_label_item.config(text='File set (open)', cursor='hand2')
                    # self.local_label_item.config(foreground='RoyalBlue3')
                    self.run_button['state'] = 'normal'
                    self.run_button['cursor'] = 'hand2'
                elif os.path.isdir(path):
                    self.local_folder.config(foreground='Black')
                    self.local_label_item.config(text='Directory set (open)', cursor='hand2')
                    # self.local_label_item.config(foreground='RoyalBlue3')
                    self.run_button['state'] = 'normal'
                    self.run_button['cursor'] = 'hand2'
                else:
                    self.local_folder.config(foreground='Red')
                    self.local_label_item.config(text='Nothing set', cursor='arrow')
                    # self.local_label_item.config(foreground='Red')
                    self.run_button['state'] = 'disabled'
                    self.run_button['cursor'] = 'arrow'
        else:
            if len(path) > 0:
                if (os.path.isdir(os.path.dirname(path)) and \
                    not os.path.isfile(path) and \
                    not os.path.isdir(path)) or (os.path.isdir(path) or os.path.isfile(path)):
                    self.local_folder.config(foreground='Black')
                    self.local_label_item.config(
                        text='File set (open)'
                            if os.path.isfile(path)
                            else 'Directory set (open)'
                            if os.path.isdir(path)
                            else 'Nonexistent item set',
                        cursor='arrow'
                        if not os.path.isdir(path) and not os.path.isfile(path)
                        else 'hand2')
                    # self.local_label_item.config(foreground='RoyalBlue3')
                    self.run_button['state'] = 'normal'
                    self.run_button['cursor'] = 'hand2'

                else:
                    self.local_folder.config(foreground='Red')
                    self.local_label_item.config(text='Nothing set')
                    # self.local_label_item.config(foreground='Red')
                    self.run_button['state'] = 'disabled'
                    self.run_button['cursor'] = 'arrow'
        self.validate_input()


    def listdir(self, param=None):
        # run validation checks
        self.validate_remote_ip(param=None)
        self.run_button['state'] = 'disabled'
        self.run_button['cursor'] = 'arrow'
        self.listdir_button['state'] = 'disabled'
        self.listdir_button['cursor'] = 'arrow'
        self.update()
        rhp = self.remote_host_port.get()
        rh = self.remote_host.get()
        rf = self.remote_folder.get()
        un = self.remote_host_username.get()
        pw = self.remote_host_password.get()
        kp = self.putty_private_key.get()
        action = 'Download' if self.action_selection.get() == 'Download from remote host' else 'Upload'
        
        if not param:
            tm = dt.datetime.now().strftime('%H:%M:%S')
            self.log.insert('', 0, values=(tm, 'List dir', rf, 'Running',))

        try: rhp = int(rhp)
        except: pass
        
        if validate_ip(rh) and \
            len(un) > 0 and \
            len(pw) > 0 and \
            (os.path.isfile(kp) or len(kp) == 0) and \
            isinstance(rhp, int):
            self.run_button['text'] = 'Fetching info'
            self.update()

            kp = f'-i {kp}' if os.path.isfile(kp) else ''
            
            # run PSCP
            encoding = 'utf-8'
            timeout = convert_to_seconds(self.set_timeout.get())

            # start pexpect process
            self.error = ''
            
            self.session = popen_spawn.PopenSpawn(f'"{self.pscp}" {kp} -scp -ls -P {rhp} {un}@{rh}:\"{rf}\"', encoding=encoding, timeout=timeout)
            
            # handle pexpect feedback
            condition_list = ['Connection refused', 'Access denied', 'FATAL ERROR', 'No such file or directory', 'Too many failures',
                'Cannot assign requested address', 'nvalid', 'ncorrect', 'diffie', 'cache?', 'key to continue', 'begin', 'ser: ',
                'sername: ', 'ogin: ', 'ogin as: ', "ssword:", 'phrase', '100%', '-p -r -d options not supported', EOF, TIMEOUT]
            action_list = [0, 0, 0, 0, 0, 0, 0, 0, 'y', 'n', '\n', '\n', un, un, un, un, pw, pw, 0, 0, 0, 0]
            self.send_on_condition([condition_list, action_list])

            # parse feedback
            err = str(self.error)
            err = '0%; EOF' if 'EOF' in err else \
                'Address error' if 'Cannot assign requested address' in err else \
                'Timeout' if 'TIMEOUT' in err else \
                'Item not found' if err == 'No such file or directory' else \
                'Failed to recurse' if '-p -r -d options not supported' in err else \
                err
            
            items = []
            
            with StringIO(self.session.before) as f:
                lines = f.readlines()
                for line in lines:
                    try:
                        split_line = line.split()
                        if split_line[0].lower() == 'total' or \
                            split_line[-1] in ['.', '..']:
                            continue
                        
                        parsed_line = " ".join(split_line[8:])
                        if rf != parsed_line:
                            if len(rf.replace(' ', '')) > 0:
                                parsed_line = f'{rf}/{parsed_line}'
                            items.append(parsed_line)
                    except:
                        pass

            if err in ['0%; EOF', 'Access Denied'] and len(items) > 0:
                err = f'{len(items)} item{"" if len(items) == 1 else "s"} found'

            if not param:
                self.remote_folder['values'] = items
            else:
                return items

            self.run_button['state'] = 'normal'
            self.run_button['cursor'] = 'hand2'
        else:
            self.run_button['state'] = 'disabled'
            self.run_button['cursor'] = 'arrow'

        self.log.set(self.log.get_children()[0], 3, err)
        
        # auto scroll down treeview
        try: self.log.see(self.log.get_children()[0])
        except: pass
        self.run_button['text'] = 'Upload item(s)' if action == 'Upload' else 'Download item(s)'
        self.listdir_button['state'] = 'normal'
        self.listdir_button['cursor'] = 'hand2'
        self.update()


    def run(self, param=None):
        # run validation checks
        self.validate_remote_ip(param=None)
        self.run_button['state'] = 'disabled'
        self.run_button['cursor'] = 'arrow'
        self.listdir_button['state'] = 'disabled'
        self.listdir_button['cursor'] = 'arrow'
        self.update()
        rhp = self.remote_host_port.get()
        rh = self.remote_host.get()
        rf = self.remote_folder.get()
        un = self.remote_host_username.get()
        pw = self.remote_host_password.get()
        lf = self.local_folder.get()
        kp = self.putty_private_key.get()
        rs = self.checkbox_var.get()

        try: rhp = int(rhp)
        except: pass
        
        action = 'Download' if self.action_selection.get() == 'Download from remote host' else 'Upload'
        rf_check = 0 if action == 'Download' and len(rf) == 0 else 1

        if action == 'Upload':
            if os.path.isfile(lf) or os.path.isdir(lf):
                path = 1
            else:
                path = 0
        else:
            if (os.path.isdir(os.path.dirname(lf)) and \
                not os.path.isfile(lf) and \
                not os.path.isdir(lf)) or (os.path.isdir(lf) or os.path.isfile(lf)):
                path = 1
            else:
                path = 0

        if validate_ip(rh) and \
            len(un) > 0 and \
            len(pw) > 0 and \
            rf_check and \
            path and \
            (os.path.isfile(kp) or len(kp) == 0) and \
            isinstance(rhp, int):
            self.run_button['text'] = 'Running'
            self.update()

            kp = f'-i {kp}' if os.path.isfile(kp) else ''
            
            # if action equals upload, prompt user for confirmation
            if action == 'Upload':
                result = alert('Please confirm', f'Attention! You are going to upload items to the remote host!\nDo you want to continue?', 'warning')
                if not result or result in ['no', 2]:
                    file = os.path.basename(lf)
                    tm = dt.datetime.now().strftime('%H:%M:%S')
                    self.log.insert('', 'end', values=(tm, action, file, 'Aborted',))

                    # auto scroll down treeview
                    try: self.log.see(self.log.get_children()[0])
                    except: pass
                    self.run_button['text'] = 'Upload item(s)'
                    self.run_button['state'] = 'normal'
                    self.update()
                    return

            # run PSCP
            encoding = 'utf-8'
            timeout = convert_to_seconds(self.set_timeout.get())

            # start pexpect process
            self.error = ''
            tm = dt.datetime.now().strftime('%H:%M:%S')
            file = os.path.basename(rf) if action == 'Download' else os.path.basename(lf)

            self.log.insert('', 0, values=(tm, action, file, 'Running',))
            recursive = '-r' if rs else ''
            if action == 'Download':
                # self.session = popen_spawn.PopenSpawn(f'"{self.pscp}" {kp} -scp {recursive} -P {rhp} {un}@{rh}:{rf} \"{lf}\"', encoding=encoding, timeout=timeout) #original
                # self.session = popen_spawn.PopenSpawn(f'"{self.pscp}" {kp} -scp {recursive} -P {rhp} {un}@{rh}:\"\'{rf}\'\" \"{lf}\"', encoding=encoding, timeout=timeout)
                self.session = popen_spawn.PopenSpawn(str(self.pscp) + " " + str(kp)  + " -scp " + str(recursive) + " -P " + str(rhp) + " " + str(un) + "@" + str(rh)  + ":" + str(rf) + " " + str(lf).replace("\'",""), encoding=encoding, timeout=timeout)
            else:
                # self.session = popen_spawn.PopenSpawn(f'"{self.pscp}" {kp} -scp {recursive} -P {rhp} "{lf}" {un}@{rh}:{rf}', encoding=encoding, timeout=timeout)
                self.session = popen_spawn.PopenSpawn(str(self.pscp) + " " + str(kp)  + " -scp " + str(recursive) + " -P " + str(rhp) + " " + lf.replace("\'","") + " " + str(un) + "@" + str(rh) + ":" + str(rf), encoding=encoding, timeout=timeout)
            
            # handle pexpect feedback
            condition_list = ['Connection refused', 'Access denied', 'FATAL ERROR', 'No such file or directory',
                'Too many failures', 'Cannot assign requested address', 'nvalid', 'ncorrect', 'diffie', 'cache?',
                'key to continue', 'begin', 'ser: ', 'sername: ', 'ogin: ', 'ogin as: ', "ssword:", 'phrase', '100%',
                '-p -r -d options not supported', EOF, TIMEOUT]

            action_list = [0, 0, 0, 0, 0, 0, 0, 0, 'y', 'n', '\n', '\n', un, un, un, un, pw, pw, 0, 0, 0, 0]
            self.send_on_condition([condition_list, action_list])

            # parse feedback
            err = str(self.error)
            err = '0%; EOF' if 'EOF' in err else \
                'Address error' if 'Cannot assign requested address' in err else \
                'Timeout' if 'TIMEOUT' in err else \
                'Item not found' if err == 'No such file or directory' else \
                'Failed to recurse' if '-p -r -d options not supported' in err else \
                err
            
            if err in ['0%; EOF', 'Access Denied'] and action == 'Upload':
                self.log.set(self.log.get_children()[0], 3, 'Validating')
                validate_transfer = self.listdir(param='list')
                if Path(lf).name in validate_transfer:
                    err = '100%'

            if action == 'Download' and err == '100%':
                self.log.set(self.log.get_children()[0], 3, 'Validating')
                for _ in range(100):
                    if os.path.isfile(os.path.join(lf, os.path.basename(rf))) or \
                        os.path.isfile(os.path.join(lf, f"'{os.path.basename(rf)}'")) or \
                        os.path.isdir(os.path.join(lf, os.path.basename(rf))):
                        self.log.set(self.log.get_children()[0], 3, err)
                        break
                if os.path.isfile(os.path.join(lf, f"'{os.path.basename(rf)}'")):
                    ext = os.path.splitext(os.path.basename(rf))[1]
                    for i in range(100):
                        if i == 0:
                            if not os.path.isfile(os.path.join(lf, os.path.basename(rf))):
                                os.rename(
                                    os.path.join(lf, f"'{os.path.basename(rf)}'"),
                                    os.path.join(lf, os.path.basename(rf))
                                )
                        else:
                            if not os.path.isfile(os.path.join(lf, os.path.basename(f'{rf}-{i}'))):
                                os.rename(
                                    os.path.join(lf, f"'{os.path.basename(rf)}'"),
                                    os.path.join(lf, os.path.basename(rf.replace(ext, f'-{i}{ext}')))
                                )

            else:
                self.log.set(self.log.get_children()[0], 3, err)
            self.run_button['state'] = 'normal'
            self.run_button['cursor'] = 'hand2'
            self.listdir_button['state'] = 'normal'
            self.listdir_button['cursor'] = 'hand2'
        else:
            self.run_button['state'] = 'disabled'
            self.run_button['cursor'] = 'arrow'
            self.listdir_button['state'] = 'disabled'
            self.listdir_button['cursor'] = 'arrow'
        
        # auto scroll down treeview
        try: self.log.see(self.log.get_children()[0])
        except: pass
        self.run_button['text'] = 'Upload item(s)' if action == 'Upload' else 'Download item(s)'
        self.update()
        

    def local_path(self, param=None):
        # set local file directory
        filepath=filedialog.askdirectory(initialdir=set_basepath(), title="Select directory")
        if not filepath:
            filepath = set_basepath()
        self.local_folder.delete(0, 'end')
        self.local_folder.insert(0, filepath)


    def send(self, param, line=None):
        # send parameter to pexpect session
        self.session.sendline(param) if line is None else self.session.send(param)


    def send_on_condition(self, parameter):
        # conditionally send commands, like passwords
        condition_list, action_list = parameter
        while True:
            try:
                time.sleep(0.2)
                self.update()
                index = self.session.expect(condition_list)
                self.update()
                time.sleep(0.3)
                if action_list[index] in [0, 1]:
                    self.error = condition_list[index]
                    break
                else:
                    time.sleep(0.2)
                    self.send(action_list[index])
            except Exception as e:
                self.error = f'{e}'
                break
                

if __name__ == '__main__':
    app = windows()
    app.option_add('*TCombobox*Listbox.background', 'Turquoise1')
    app.attributes('-topmost', True)
    app.attributes('-topmost', False)
    app.remote_host.focus_force()
    app.resizable(0,0)
    app.mainloop()
