#!/usr/bin/python3
import subprocess
import os
import sys
import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
from tkinter.messagebox import showerror
import urllib.request
from threading import Thread
import shutil

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.geometry('600x400')
        # self.resizable(0, 0)
        self.title("Installer")
        # Change the theme
        ttk.Style(self).theme_use('clam')
        # Grid configurations
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=4)
        self.rowconfigure(3, weight=1)
        self.rowconfigure(4, weight=1)
        self.rowconfigure(5, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        ## Label 1
        ttk.Label(self, text='When you are ready press start to initiate the installation process.').grid(row=0, column=0, columnspan=2, sticky='sw', padx=5)
        ## Label 2
        ttk.Label(self, text='Internet connection is required to download the required application packages.', foreground='red').grid(row=1, column=0, columnspan=2, sticky='nw', padx=5)
        # Text window
        self.text_wind = ScrolledText(self, height=10, wrap='word')
        self.text_wind.grid(row=2, column=0, sticky='nesw',columnspan=2, padx=5, pady=5)
        # Check button
        self.agreement = tk.IntVar()
        chk_btn = ttk.Checkbutton(self, text='Create a desktop shortcut', variable=self.agreement, onvalue=1, offvalue=0)
        self.agreement.set(1)
        chk_btn.grid(row=3, column=0, padx=5, pady=5, sticky='w')
        # Progressbar
        self.progressbar = ttk.Progressbar(self, orient='horizontal', mode='determinate', length=590)
        self.progressbar.grid(row=4, column=0, columnspan=2, padx=5, pady=5)
        self.progress = 100/7
        # Close button
        self.btn1 = ttk.Button(self, text='Close', command=self.destroy)
        self.btn1.grid(row=5, column=0, sticky='ew', padx=5, pady=5)
        # Start button
        self.btn2 = ttk.Button(self, text='Start', command=self.start)
        self.btn2.grid(row=5, column=1, sticky='ew', padx=5, pady=5)
        self.thread = Thread(target=self.main)
        self.errors = 0
    
    def start(self):
        # Disable the buttons until finished
        self.btn1.state(['disabled'])
        self.btn2.state(['disabled'])
        self.title('Installing...')
        # Start the main function
        self.after(500, self.thread.start())
    
    def main(self):
        self.text_wind.insert('end', 'Installing required Python modules...\n\n')
        # Install pillow
        self.install_module('PIL', 'Pillow', 'pillow')
        # Install Tkinter ToolTip
        self.install_module('tktooltip', 'Tkinter ToolTip', 'tkinter-tooltip')
        # Install Google Translate
        self.install_module('googletrans', 'Google Translate', 'googletrans==3.1.0a0')
        # Install Pandas
        self.install_module('pandas', 'Pandas', 'pandas')
        # Install Openpyxl
        self.install_module('openpyxl', 'Openpyxl', 'openpyxl')
        # Install Pyshortcuts
        self.install_module('pyshortcuts', 'Pyshortcuts', 'pyshortcuts')
        # Check if all packages are installed
        if self.errors > 0:
            self.text_wind.insert('end', ('Installation is finished with %i errors\n' %self.errors))
            self.text_wind.see('end')
            showerror(title='Installation failed', message='Installation is finished with %i errors.' %self.errors)
            return
        else:
            # Copy application files, and make shortcuts
            from pyshortcuts import make_shortcut
            # Check operating system
            if os.name == 'nt':
                install_directory = os.path.join(os.environ["ProgramW6432"], 'imdb-get')
                icon = os.path.join(install_directory, 'images', 'logo.ico')
                app_executable = os.path.join(install_directory, 'main-tk.py')
                # Copy application files
                if os.path.isdir(install_directory):
                    shutil.rmtree(install_directory)
                    os.mkdir(install_directory)
                else:
                    os.mkdir(install_directory)
                src_dir = os.path.join(os.path.realpath(os.path.dirname(__file__)), 'files')
                shutil.copytree(src_dir, install_directory, dirs_exist_ok=True)
                # Create shortcuts
                if self.agreement.get() == 0:
                    make_shortcut(app_executable, name='IMDB Get', description='IMDB Get is a tool that uses the OMDB API to get info about movies.', folder=None,icon=icon, terminal=False, desktop=False, startmenu=True)
                elif self.agreement.get() == 1:
                    make_shortcut(app_executable, name='IMDB Get', description='IMDB Get is a tool that uses the OMDB API to get info about movies.', folder=None,icon=icon, terminal=False, desktop=True, startmenu=True)
                self.progressbar.step(self.progress)
            elif os.name == 'posix' or sys.platform.startswith('darwin'):
                install_directory = os.path.join(os.path.expanduser('~'), 'imdb-get')
                icon = os.path.join(install_directory, 'images', 'logo.ico')
                app_executable = os.path.join(install_directory, 'main-tk.py')
                # Copy application files
                if os.path.isdir(install_directory):
                    shutil.rmtree(install_directory)
                    os.mkdir(install_directory)
                else:
                    os.mkdir(install_directory)
                src_dir = os.path.join(os.path.realpath(os.path.dirname(__file__)), 'files')
                shutil.copytree(src_dir, install_directory, dirs_exist_ok=True)
                # Create shortcuts
                if self.agreement.get() == 0:
                    make_shortcut(app_executable, name='IMDB Get', description='IMDB Get is a tool that uses the OMDB API to get info about movies.', folder=None,icon=icon, terminal=False, desktop=False, startmenu=True)
                elif self.agreement.get() == 1:
                    make_shortcut(app_executable, name='IMDB Get', description='IMDB Get is a tool that uses the OMDB API to get info about movies.', folder=None,icon=icon, terminal=False, desktop=True, startmenu=True)
                self.progressbar.step(self.progress)
            # Enable buttons again after finishing
            self.text_wind.insert('end', 'Installation is finished successfully.\n')
            self.text_wind.see('end')
            self.btn1.state(['!disabled'])
            self.btn2.state(['!disabled'])
            self.title('Installer')
    
    def install_module(self, module_name, plain_name, pkg_name):
        try:
            import module_name
            self.text_wind.insert('end', ('%s is installed.\n\n' %plain_name))
            self.text_wind.see('end')
        except ImportError:
            if self.check_conn() is True:
                self.text_wind.insert('end', ('Installing %s...\n' %plain_name))
                self.text_wind.see('end')
                process = subprocess.run(['pip', 'install', pkg_name])
                if process.returncode == 0:
                    self.text_wind.insert('end', ('%s is installed.\n\n' %plain_name))
                    self.text_wind.see('end')
                else:
                    self.text_wind.insert('end', ('%s installation is failed.\n\n' %plain_name))
                    self.text_wind.see('end')
                    self.errors+=1
                    return
            else:
                self.text_wind.insert('end', "Connection is offline.\n\n")
                self.text_wind.see('end')
                showerror(title='Error!', message='Internet connection is offline.')
                self.errors+=1
                return
        self.progressbar.step(self.progress)
    
    def check_conn(self):
        try:
            url = 'https://www.google.com'
            urllib.request.urlopen(url, timeout=3)
            return True
        except Exception:
            return False

if __name__ == "__main__":
    app = App()
    app.mainloop()