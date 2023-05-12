#!/usr/bin/python3
import log
import subprocess
import code_1
import configparser
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
from tkinter import Menu
from tkinter.messagebox import showerror, showinfo, showwarning, askyesno
from tkinter import simpledialog
from tkinter.scrolledtext import ScrolledText
from datetime import date
from threading import Thread
import os.path
import json
import webbrowser

try:
    from PIL import Image, ImageTk
    log.logger.debug('Pillow is installed.')
except ImportError:
    log.logger.debug('Pillow is not installed.')
    ask1 = askyesno(title='Import failed!', message='Pillow is not installed. \nDo you want to install it?')
    if ask1:
        process1 = subprocess.run(['pip', 'install', 'pillow'])
    else:
        exit()
    if process1.returncode == 0:
        showinfo(title='Success!', message='Pillow is installed successfully.')
        from PIL import Image, ImageTk
    else:
        showerror(title='Error!', message='Pillow installation is failed.')
        log.logger.error('Pillow installation is failed.')
        exit()

try:
    from tktooltip import ToolTip
    log.logger.debug('tkinter-tooltip is installed.')
except ImportError:
    log.logger.debug('ToolTip is not installed.')
    ask2 = askyesno(title='Import failed!', message='tkinter-tooltip is not installed. \nDo you want to install it?')
    if ask2:
        process2 = subprocess.run(['pip', 'install', 'tkinter-tooltip'])
    if process2.returncode == 0:
        showinfo(title='Success!', message='tkinter-tooltip is installed successfully.')
        from tktooltip import ToolTip
    else:
        showerror(title='Error!', message='tkinter-tooltip installation is failed.')
        log.logger.error('tkinter-tooltip installation is failed.')
        exit()

# Get the directory of the current python file
main_dir = os.path.realpath(os.path.dirname(__file__))

config = configparser.ConfigParser()
## Check for config.ini file
config_file = os.path.join(main_dir, 'config.ini')
if os.path.isfile(config_file):
	log.logger.debug('Config file is found')
	log.logger.debug(config_file)
else:
    log.logger.error('Config file is not found, the application is exiting now.')
    showerror(title='Error!', message='Config file is not found, \nthe application is exiting now.')
    exit()

config.read(config_file)

# Setting the main window
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.geometry('350x400')
        self.resizable(0, 1)
        self.title("IMDB Get")
        # Change the theme
        self.tk.call("source", os.path.join(main_dir, "azure.tcl"))
        self.tk.call("set_theme", "light")
        # Set the icon
        icon = os.path.join(main_dir, 'images', 'logo.png')
        self.iconphoto(False, tk.PhotoImage(file=icon))

        # menubar
        menubar = Menu(self)
        self.config(menu=menubar)
        # file menu
        file_menu = Menu(menubar, tearoff=0)
        file_menu.add_command(label='Search..',command=self.movie_viewer, underline=0)
        file_menu.add_command(label='Import a list..', command=self.process_text, underline=0)
        file_menu.add_command(label='Open a folder..', command=self.open, underline=0)
        file_menu.add_command(label='Excel viewer..',command=self.excel_viewer, underline=0)
        file_menu.add_command(label='Restore..',command=self.open_restore, underline=0)
        file_menu.add_separator()
        file_menu.add_command(label='Exit', command=self.destroy, underline=0)
        menubar.add_cascade(label='File', menu=file_menu, underline=0)
        # edit menu
        edit_menu = Menu(menubar, tearoff=0)
        edit_menu.add_command(label='Options..', command=self.open_option, underline=0)
        edit_menu.add_command(label='Blocklist..', command=self.open_blocklist, underline=0)
        menubar.add_cascade(label='Edit', menu=edit_menu, underline=0)
        # help menu
        help_menu = Menu(menubar, tearoff=0)
        help_menu.add_command(label='About..', command=self.open_about, underline=0)
        menubar.add_cascade(label='Help', menu=help_menu, underline=0)
        options = {'padx':5, 'pady':5, 'fill':'x', 'expand':True}

        # Search a movie
        img1 = ImageTk.PhotoImage(Image.open(os.path.join(main_dir, 'images/search.png')))
        search_btn = ttk.Button(self, text='Search a movie', image=img1, compound='left', command=self.movie_viewer)
        # Setting image again is a necessary, or the image will not appear
        search_btn.image = img1
        search_btn.pack(**options)
        search_btn.focus()
        ToolTip(search_btn, msg="Click to search a movie.", delay=0.3)

        # Import a list
        img2 = ImageTk.PhotoImage(Image.open(os.path.join(main_dir, 'images/list.png')))
        import_btn = ttk.Button(self, text='Import a list', image=img2, compound='left', command=self.process_text)
        # Setting image again is a necessary, or the image will not appear
        import_btn.image = img2
        import_btn.pack(**options)
        ToolTip(import_btn, msg="Click to import a list of moives from a text file.", delay=0.3)
        
        # Open a folder
        img3 = ImageTk.PhotoImage(Image.open(os.path.join(main_dir, 'images/folder.png')))
        browse_btn = ttk.Button(self, text='Open a folder', image=img3, compound='left', command=self.open)
        # Setting image again is a necessary, or the image will not appear
        browse_btn.image = img3
        browse_btn.pack(**options)
        ToolTip(browse_btn, msg="Click to open a folder, and list its files.", delay=0.3)

        # Open excel viewer
        img4 = ImageTk.PhotoImage(Image.open(os.path.join(main_dir, 'images/open_xls.png')))
        r_btn = ttk.Button(self, text='Excel Viewer', image=img4, compound='left', command=self.excel_viewer)
        r_btn.image = img4
        r_btn.pack(**options)
        ToolTip(r_btn, msg="Click to open the last created excel file using the excel viewer.", delay=0.3)

        # Edit blocklist
        img5 = ImageTk.PhotoImage(Image.open(os.path.join(main_dir, 'images/list.png')))
        b_btn = ttk.Button(self, text='Edit blocklist', image=img5, compound='left', command=self.open_blocklist)
        b_btn.image = img5
        b_btn.pack(**options)
        ToolTip(b_btn, msg="The blocklist window contains all the unwanted characters that needs to be removed from filenames.", delay=0.3)

        # Undo last operation
        img6 = ImageTk.PhotoImage(Image.open(os.path.join(main_dir, 'images/undo.png')))
        r_btn = ttk.Button(self, text='Undo last operation', image=img6, compound='left', command=self.open_restore)
        r_btn.image = img6
        r_btn.pack(**options)
        ToolTip(r_btn, msg="Click to restore the last edited files and folders to their original state.", delay=0.3)

        # Option
        img7 = ImageTk.PhotoImage(Image.open(os.path.join(main_dir, 'images/settings.png')))
        option_btn = ttk.Button(self, text='Options', image=img7, compound='left', command=self.open_option)
        option_btn.image = img7
        option_btn.pack(**options)

        # Exit
        img8 = ImageTk.PhotoImage(Image.open(os.path.join(main_dir, 'images/exit.png')))
        exit_btn = ttk.Button(self, text='Exit', image=img8, compound='left', command=self.destroy)
        exit_btn.image = img8
        exit_btn.pack(**options)
    
    def movie_viewer(self):
        app.withdraw()
        subprocess.run(['python3', os.path.join(main_dir, 'movie_viewer.py')])
        app.deiconify()

    def open_folder(self):
        # Get the location of the last opened directory
        if os.path.isfile(os.path.join(main_dir, 'last_location')):
            with open(os.path.join(main_dir, 'last_location'), 'r') as text_file:
                initialdir = text_file.read()
                log.logger.debug('Last location: %s' %initialdir)
        else:
            initialdir = main_dir
            log.logger.debug('Last location is not saved yet.')
        code_1.opened_dir = fd.askdirectory(title='open a directory', initialdir=initialdir)
        # Check if the open dialog is canceled
        if len(code_1.opened_dir) > 0:
            log.logger.debug('Main directory: %s' %code_1.opened_dir)
            with open(os.path.join(main_dir, 'last_location'), 'w') as file:
                file.write(os.path.realpath(code_1.opened_dir))
        else:
            log.logger.debug('Open dialog is cancelled, trying again...')
            return None
    
    def process_text(self):
        app.withdraw()
        progress_names = ProgressNames(self)
        app.deiconify()
    
    def open_restore(self):
        restore_w = Restore(self)
        restore_w.grab_set()
    
    def open_option(self):
        self.destroy()
        subprocess.run(['python3', os.path.join(main_dir, 'options.py')])
    
    def open_blocklist(self):
        blocklist_w = Blocklist(self)
        blocklist_w.grab_set()
    
    def excel_viewer(self):
        app.withdraw()
        subprocess.run(['python3', os.path.join(main_dir, 'excel_viewer.py')])
        app.deiconify()
        
    def open_about(self):
        about_w = About(self)
    
    def open(self):
        # Open a folder
        self.open_folder()
        # Check main directory
        if code_1.opened_dir == () or code_1.opened_dir == '':
            self.lower()
            showerror(title='Error!', message='You did not choose any folder,\nplease choose any folder and try again.')
            self.lift()
            log.logger.error('No directory is chosen.')
            return
        # Check API key
        if config['omdb']['api_key'] == '0':
            self.lower()
            answer = askyesno(title='Question', message="You did not enter your API key in the application options.\nDo you want get an API key?")
            self.lift()
            if answer:
                webbrowser.open_new('https://www.omdbapi.com/apikey.aspx')
                return
            else:
                self.lower()
                showwarning(title='Warning!', message='The application will continue, but it may not work correctly.')
                log.logger.error('API key is not set.')
                self.lift()
        
        # Store the data of the files to files.json
        code_1.Run.create_json_file()
        # load data of the files from json
        movie_names, years = code_1.Run.get_from_json()
        # Open movieNames window
        app.withdraw()
        MovieNames(app)

class MovieNames(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.geometry('650x400')
        self.title('Movie Names')
        # Set the icon
        icon = os.path.join(main_dir, 'images', 'logo.png')
        self.iconphoto(False, tk.PhotoImage(file=icon))
        # Choose what happens after closing the window
        self.protocol("WM_DELETE_WINDOW", self.close)

        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=4)
        self.rowconfigure(2, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self.columnconfigure(3, weight=1)
        
        # Update the json file
        self.thread = Thread(target=code_1.Run.update_json_file)
        self.after(500, self.thread.start())

        # Label
        ttk.Label(self, text='This is a list of the name of the movies extracted from the filenames of the local multimedia files, If there are unwanted sub-names in the name of the files, you can either add them to the blocklist, and start over, or you can edit them using the button below.', wraplength=640, justify='left').grid(row=0, column=0, columnspan=4)

        # Import the list
        n = 0
        self.movie_names = []
        json_file = open(os.path.join(code_1.opened_dir, 'files.json'), 'r', encoding="utf-8")
        data = json.load(json_file)
        for loop in range(0, len(data['files'])):
            self.movie_names.append(data['files'][n]['Renamed filename'])
            n+=1
        json_file.close()

        # listbox
        self.listbox_var = tk.Variable(value=self.movie_names)
        self.listbox = tk.Listbox(self, listvariable = self.listbox_var, selectmode=tk.SINGLE, font=20, height=11)
        self.listbox.grid(row=1, column=0, sticky='nsew', columnspan=4, padx=5, pady=5, ipadx=5, ipady=5)
        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.listbox.yview)
        self.listbox['yscrollcommand'] = scrollbar.set
        scrollbar.grid(row=1, column=3, padx=5, pady=5, sticky='ens')
        self.index = None    # reserved for the index of the selected listbox

        # Close button
        img1 = ImageTk.PhotoImage(Image.open(os.path.join(main_dir, 'images/exit.png')))
        close_btn = ttk.Button(self, text='Close', image=img1, compound='left', command=self.close)
        close_btn.grid(row=2, column=0, padx=5, pady=5, sticky='ew')
        close_btn.image = img1

        # Edit selection button
        img2 = ImageTk.PhotoImage(Image.open(os.path.join(main_dir, 'images/edit.png')))
        open_btn1 = ttk.Button(self, text='Edit selection', image=img2, compound='left', command=self.edit)
        open_btn1.grid(row=2, column=1, padx=5, pady=5, sticky='ew')
        open_btn1.image = img2
        ToolTip(open_btn1, msg="Click to edit the current selection.", delay=0.3)

        # Show original filenames button
        img3 = ImageTk.PhotoImage(Image.open(os.path.join(main_dir, 'images/list.png')))
        open_btn2 = ttk.Button(self, text='Show original filenames', image=img3, compound='left', command=self.open_original_names)
        open_btn2.grid(row=2, column=2, padx=5, pady=5, sticky='ew')
        open_btn2.image = img3
        ToolTip(open_btn2, msg="Click to show original filenames.", delay=0.3)

        # Start button
        img4 = ImageTk.PhotoImage(Image.open(os.path.join(main_dir, 'images/run.png')))
        start_btn = ttk.Button(self, text='Start', image=img4, compound='left', command=self.start)
        start_btn.grid(row=2, column=3, padx=5, pady=5, sticky='ew')
        start_btn.image = img4

    def start(self):
        if self.thread.is_alive():
            if config['folders']['translate'] == 'True' or config['files']['translate'] == 'True':
                self.lower()
                showinfo(title='Info', message='Translating files/folders may take a few minutes, so please wait a little while, and try again.')
                self.lift()
                return
            else:
                self.lower()
                showinfo(title='Info', message='The application is doing something in the background, so please wait a little while, and try again.')
                self.lift()
                return
        else:
            ## Open progress window
            MovieNames.destroy(self)
            ProgressFiles(app)
    
    def edit(self):
        if self.thread.is_alive():
            if config['folders']['translate'] == 'True' or config['files']['translate'] == 'True':
                self.lower()
                showinfo(title='Info', message='Translating files/folders may take a few minutes, so please wait a little while, and try again.')
                self.lift()
                return
            else:
                self.lower()
                showinfo(title='Info', message='The application is doing something in the background, so please wait a little while, and try again.')
                self.lift()
                return
        selected = self.item_selected()
        user_input = simpledialog.askstring(title='Edit MovieName', prompt='Edit as you wish, but do not leave it empty', initialvalue=selected)
        if user_input == '':
            self.lower()
            showerror(title='Invalid input', message='Invalid input, try again.')
            self.lift()
        else:
            n = 0
            json_file = open(os.path.join(code_1.opened_dir, 'files.json'), 'r', encoding="utf-8")
            data = json.load(json_file)
            for loop in range(0, len(data['files'])):
                if selected in (data['files'][n]['Renamed filename']):
                    renamed_filename = user_input + data['files'][n]['File extension']
                    data['files'][n].update({'Renamed filename': user_input})
                    new_file_path = os.path.join(data['files'][n]['New folder path'], renamed_filename)
                    data['files'][n].update({'New file path': new_file_path})
                    break
                n+=1
            json_file.close()
            with open(os.path.join(code_1.opened_dir, 'files.json'), 'w', encoding="utf-8") as json_file:
                json.dump(data, json_file, ensure_ascii=False, indent=4)
            self.listbox.delete(self.index)
            self.listbox.insert(self.index, user_input)
    
    def item_selected(self):
        self.index = self.listbox.curselection()
        selected = self.listbox.get(self.index)
        return selected
    
    def open_original_names(self):
        original_names_w = OriginalNames(self)
    
    def close(self):
        self.destroy()
        app.deiconify()

class ProgressNames(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.geometry('500x350')
        self.title('In progress...')
        # Set the icon
        icon = os.path.join(main_dir, 'images', 'logo.png')
        self.iconphoto(False, tk.PhotoImage(file=icon))
        # Choose what happens after closing the window
        self.protocol("WM_DELETE_WINDOW", self.close)
        # Choose what happens after closing the window
        self.protocol("WM_DELETE_WINDOW", self.close)

        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=4)
        self.columnconfigure(0, weight=1)

        # Progressbar
        self.progressbar = ttk.Progressbar(self, orient='horizontal', mode='indeterminate', length=450)
        self.progressbar.grid(row=0, column=0, columnspan=2, padx=5, pady=15)
        # Text window
        self.text_wind = ScrolledText(self, height=12, wrap='word')
        self.text_wind.bind('<<Modified>>', self.scrolldown)
        self.text_wind.grid(row=1, column=0, columnspan=2, sticky='nesw', padx=5, pady=5)
        self.text_wind['state'] = 'disabled'
        # Open the text file
        # Start the main function
        self.thread = Thread(target=self.run)
        self.after(500, self.thread.start())
    
    def open_txt_file(self):
        # Open the text file
        self.lower()
        filetypes = (('text files', '*.txt'), ('All files', '*.*'))
        txt_file = fd.askopenfile(title='Open text file', initialdir=main_dir, filetypes=filetypes)
        self.lift()
        # Check if the open dialog is canceled
        print(txt_file)
        if txt_file == None:
            log.logger.debug('Open dialog is cancelled.')
            return None
        if len(txt_file.name) > 0:
            log.logger.debug('Main directory: %s' %txt_file)
            return txt_file.name
        else:
            log.logger.debug('Open dialog is cancelled.')
            return None

    def load_text(self):
        if self.thread.is_alive():
            text_file = open(os.path.join(main_dir, 'info.log'), 'r')
            self.text_wind['state'] = 'normal'
            if self.text_wind.get('1.0','end') != None:
                self.text_wind.delete(1.0, 'end')
            self.text_wind.insert('end', text_file.read())
            self.text_wind['state'] = 'disabled'
            text_file.close()
        self.after(100, self.load_text)
    
    def scrolldown(self, event):
        self.text_wind.yview('end')
        self.text_wind.edit_modified(False)

    def close(self):
        self.destroy()
        app.deiconify()
    
    def run(self):
        self.progressbar.start(interval=10)
        # Extract data from the text file
        movie_names = []
        years = []
        txt_file = self.open_txt_file()
        if txt_file == None:
            self.destroy()
        else:
            with open(txt_file, 'r') as text_file:
                lines = text_file.readlines()
                for line in lines:
                    name, year = self.split(line)
                    movie_names.append(name)
                    years.append(year)
            
            # Load the text file
            self.after(1000, self.load_text)

            # Fetch data from OMDB
            code_1.Run.process_text(movie_names, years)

            # Download posters
            code_1.Run.download_posters(code_1.Poster, path=1)

            self.progressbar.stop()
            # Close the window and open the excel file
            self.destroy()
            app_path = os.path.join(main_dir, 'excel_viewer.py')
            file_path = os.path.join(main_dir, 'movies.xlsx')
            with open(os.path.join(main_dir, 'last_location'), 'w') as file:
                file.write(main_dir)
            subprocess.run(['python3', app_path, file_path])
    
    def split(self, name):
        ## Remove the year from the string and store it to be used later
        year = ''
        for y in range(1900, int(date.today().year)+1):
            if str(y) in name:
                year = str(y)
                name = name.replace(str(y), '')
        name = name.strip()
        return name, year
    
class ProgressFiles(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.geometry('500x350')
        self.title('In progress...')
        # Set the icon
        icon = os.path.join(main_dir, 'images', 'logo.png')
        self.iconphoto(False, tk.PhotoImage(file=icon))
        # Choose what happens after closing the window
        self.protocol("WM_DELETE_WINDOW", self.close)

        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=4)
        self.rowconfigure(2, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        
        # Progressbar
        self.progressbar = ttk.Progressbar(self, orient='horizontal', mode='indeterminate', length=450)
        self.progressbar.grid(row=0, column=0, columnspan=2, padx=5, pady=15)
        # Text window
        self.text_wind = ScrolledText(self, height=12, wrap='word')
        self.text_wind.bind('<<Modified>>', self.scrolldown)
        self.text_wind.grid(row=1, column=0, columnspan=2, sticky='nesw', padx=5, pady=5)
        self.text_wind['state'] = 'disabled'
        # Close button
        img1 = ImageTk.PhotoImage(Image.open(os.path.join(main_dir, 'images/exit.png')))
        self.btn1 = ttk.Button(self, text='Close', image=img1, compound='left', command=self.close)
        self.btn1.image = img1
        self.btn1.grid(row=2, column=0, sticky='ew', padx=5, pady=5)
        self.btn1.state(['disabled'])
        # Undo button
        img2 = ImageTk.PhotoImage(Image.open(os.path.join(main_dir, 'images/undo.png')))
        self.btn2 = ttk.Button(self, text='Undo..', image=img2, compound='left', command=self.restore)
        self.btn2.image = img2
        self.btn2.grid(row=2, column=1, sticky='ew', padx=5, pady=5)
        ToolTip(self.btn2, msg="Click to restore the last edited files and folders to their original state.", delay=0.3)
        self.btn2.state(['disabled'])
        # Load the text file
        self.after(500, self.load_text)
        # Start the main function
        self.thread = Thread(target=self.run)
        self.after(500, self.thread.start())

    def load_text(self):
        if self.thread.is_alive():
            text_file = open(os.path.join(main_dir, 'info.log'), 'r')
            self.text_wind['state'] = 'normal'
            if self.text_wind.get('1.0','end') != None:
                self.text_wind.delete(1.0, 'end')
            self.text_wind.insert('end', text_file.read())
            self.text_wind['state'] = 'disabled'
            text_file.close()
        self.after(100, self.load_text)
    
    def scrolldown(self, event):
        self.text_wind.yview('end')
        self.text_wind.edit_modified(False)
    
    def restore(self):
        # Move all moved files back to the main folder
        code_1.Run.move()
        # Restore filenames to their original names
        code_1.Run.restore_files()
        # Restore folder-names to their original names
        code_1.Run.restore_folders()
        self.lower()
        showinfo(title='Information', message='Previously renamed files and folders are restored to their original names successfully.')
        self.lift()

    def close(self):
        self.destroy()
        app.deiconify()
    
    def run(self):
        ## Start progressbar
        self.progressbar.start(interval=10)
        code_1.Run.run()
        log.logger.info('All operations are finished, you can close now.')
        self.progressbar.stop()
        self.lower()
        showinfo(title='Information', message="Finished, you can close now,\nor press 'Restore' to restore renamed files and folders to their original names.")
        self.lift()
        # Activate the buttons after finishing
        self.btn1.state(['!disabled'])
        self.btn2.state(['!disabled'])
        self.title('Done, you can close now.')
        # Open the created excel file
        app_path = os.path.join(main_dir, 'excel_viewer.py')
        file_path = os.path.join(code_1.opened_dir, 'movies.xlsx')
        subprocess.run(['python3', app_path, file_path])

# Original names window
class OriginalNames(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title('Original Names')
        self.geometry('550x350')
        # Set the icon
        icon = os.path.join(main_dir, 'images', 'logo.png')
        self.iconphoto(False, tk.PhotoImage(file=icon))

        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=4)
        self.rowconfigure(2, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)

        # Label
        ttk.Label(self, text='This is a list of the original names of all the multimedia files inside the main folder, and sub-folders.', wraplength=540, justify='left').grid(row=0, column=0, columnspan=3)

        # Import the list
        n = 0
        original_names = []
        json_file = open(os.path.join(code_1.opened_dir, 'files.json'), 'r', encoding="utf-8")
        data = json.load(json_file)
        for loop in range(0, len(data['files'])):
            original_names.append(data['files'][n]['Original Filename'])
            n+=1
        json_file.close()

        # listbox
        self.listbox_var = tk.Variable(value=original_names)
        self.listbox = tk.Listbox(self, listvariable = self.listbox_var, selectmode=tk.SINGLE, font=20, height=11)
        self.listbox.grid(row=1, column=0, sticky='nsew', columnspan=3, padx=5, pady=5, ipadx=5, ipady=5)
        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.listbox.yview)
        self.listbox['yscrollcommand'] = scrollbar.set
        scrollbar.grid(row=1, column=2, sticky='ens', padx=5, pady=5)

        # Close button
        img1 = ImageTk.PhotoImage(Image.open(os.path.join(main_dir, 'images/exit.png')))
        close_btn = ttk.Button(self, text='Close', image=img1, compound='left', command=self.destroy)
        close_btn.grid(row=2, column=1, padx=5, pady=5, sticky='ew')
        close_btn.image = img1

# Blocklist window
class Blocklist(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title('Blocklist')
        self.geometry('550x350')
        # Set the icon
        icon = os.path.join(main_dir, 'images', 'logo.png')
        self.iconphoto(False, tk.PhotoImage(file=icon))

        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=4)
        self.rowconfigure(2, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self.columnconfigure(3, weight=1)

        ## Import the list from the text file
        text_file = open(os.path.join(main_dir, 'blocklist.txt'), 'r')
        blocklist = [line.strip() for line in text_file]
        self.list = [name.lower() for name in blocklist]
        text_file.close()

        # Label
        ttk.Label(self, text='Here, you can add, edit, or remove the characters that you do not want to be included in the name of the movies.', wraplength=530, justify='left').grid(row=0, column=0, columnspan=4)

        ## Add listbox
        self.listbox_var = tk.Variable(value=self.list)
        self.listbox = tk.Listbox(self, listvariable = self.listbox_var, selectmode=tk.SINGLE, font=20, height=10)
        self.listbox.grid(row=1, column=0, sticky='nsew', columnspan=4, padx=5, pady=5, ipadx=5, ipady=5)
        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.listbox.yview)
        self.listbox['yscrollcommand'] = scrollbar.set
        scrollbar.grid(row=1, column=3, sticky='ens', padx=5, pady=5)

        ## Edit button
        img1 = ImageTk.PhotoImage(Image.open(os.path.join(main_dir, 'images/edit.png')))
        self.index = None    # reserved for the index of the selected item of the listbox
        edit_btn = ttk.Button(self, text='Edit selection', compound='left',image=img1, command=self.edit)
        edit_btn.grid(row=2, column=0,padx=5, pady=5, sticky='ew')
        edit_btn.image = img1

        ## Insert button
        img2 = ImageTk.PhotoImage(Image.open(os.path.join(main_dir, 'images/add.png')))
        add_btn = ttk.Button(self, text='Add',image=img2, compound='left' , command=self.add)
        add_btn.grid(row=2, column=1,padx=5, pady=5, sticky='ew')
        add_btn.image = img2

        ## Delete button
        img3 = ImageTk.PhotoImage(Image.open(os.path.join(main_dir, 'images/delete.png')))
        delete_btn = ttk.Button(self, text='Delete', image=img3, compound='left', command=self.delete)
        delete_btn.grid(row=2, column=2,padx=5, pady=5, sticky='ew')
        delete_btn.image = img3

        ## Save & close button
        img4 = ImageTk.PhotoImage(Image.open(os.path.join(main_dir, 'images/save.png')))
        save_btn = ttk.Button(self, text='Save and close',image=img4, compound='left', command=self.save)
        save_btn.grid(row=2, column=3, padx=5, pady=5, sticky='ew')
        save_btn.image = img4
    
    def edit(self):
        user_input = simpledialog.askstring(title='Edit', prompt='Edit as you wish, but do not leave it empty', initialvalue=self.item_selected())
        self.listbox.delete(self.index)
        self.listbox.insert(self.index, user_input)
    
    def item_selected(self):
        self.index = self.listbox.curselection()
        selected = self.listbox.get(self.index)
        return selected
    
    def add(self):
        user_input = simpledialog.askstring(title='Add new item', prompt='Add a new item to the list')
        self.listbox.insert('end', user_input)

    def delete(self):
        self.index = self.listbox.curselection()
        self.listbox.delete(self.index)

    def save(self):
        blocklist = list(self.listbox.get(first=0, last=len(self.list)))
        log.logger.debug('Movie Names are:\n {}'.format("' , '".join(self.list)))
        with open(os.path.join(main_dir, 'blocklist.txt'), 'w') as text_file:
            for item in blocklist:
                text_file.write(item)
                text_file.write('\n')
        self.destroy()

# Restore window
class Restore(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.geometry('500x350')
        self.title('Undo last operation')
        # Set the icon
        icon = os.path.join(main_dir, 'images', 'logo.png')
        self.iconphoto(False, tk.PhotoImage(file=icon))

        self.rowconfigure(0, weight=4)
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)
        
        # Text window
        self.text_wind = ScrolledText(self, height=12, wrap='word')
        self.text_wind.grid(row=0, column=0, sticky='nesw',columnspan=2, padx=5, pady=5)
        self.text_wind.bind('<<Modified>>', self.scrolldown)
        self.text_wind['state'] = 'disabled'

        # Close button
        img1 = ImageTk.PhotoImage(Image.open(os.path.join(main_dir, 'images/exit.png')))
        self.btn1 = ttk.Button(self, text='Close', image=img1, compound='left', command=self.destroy)
        self.btn1.image = img1
        self.btn1.grid(row=1, column=0, sticky='ew', padx=5, pady=5)

        if code_1.opened_dir == '':
            self.lower()
            showerror(title='File is not found!', message='The backup file is not found.\nChoose a folder that contains the backup file.')
            code_1.opened_dir = fd.askdirectory(title='Open a directry', initialdir='/')
            self.lift()
            if code_1.opened_dir == '' or code_1.opened_dir == ():
                self.lower()
                showerror(title='error!', message='The backup file is not found, exiting now.')
                self.destroy()
        self.btn1.state(['disabled'])
        self.title('Restoring...')
        # Load the text file
        self.after(500, self.load_text)
        # Start the restore function
        self.r_thread = Thread(target=self.restore)
        self.after(500, self.r_thread.start())

    def load_text(self):
        if self.r_thread.is_alive():
            text_file = open(os.path.join(main_dir, 'info.log'), 'r')
            self.text_wind['state'] = 'normal'
            if self.text_wind.get('1.0','end') != None:
                self.text_wind.delete(1.0, 'end')
            self.text_wind.insert('end', text_file.read())
            self.text_wind['state'] = 'disabled'
            text_file.close()
        self.after(100, self.load_text)

    def scrolldown(self, event):
        self.text_wind.yview('end')
        self.text_wind.edit_modified(False)

    def restore(self):
        # Move all moved files back to the main folder
        code_1.Run.move()
        # Restore filenames to their original names
        code_1.Run.restore_files()
        # Restore folder-names to their original names
        code_1.Run.restore_folders()
        # Activate the buttons after finishing
        self.btn1.state(['!disabled'])
        self.lower()
        showinfo(title='Information', message='The previously renamed files and folders are restored to their original names successfully.')
        self.lift()
        self.title("Done, you can close now.")

# About window
class About(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title('About IMDB Get')
        self.geometry('300x350')
        self.resizable(0, 1)
        # Set the icon
        icon = os.path.join(main_dir, 'images', 'logo.png')
        self.iconphoto(False, tk.PhotoImage(file=icon))

        self.columnconfigure(0, weight=3)
        self.columnconfigure(1, weight=1)

        # Image logo
        image = Image.open(os.path.join(main_dir, 'images/logo.png'))
        resize_image = image.resize((100, 100))
        img = ImageTk.PhotoImage(resize_image)

        # Heading
        heading = ttk.Label(self, text='IMDB Get', font=30, image=img, anchor='e', compound='left')
        heading.image = img
        heading.grid(row=0, column=0)

        # Label1
        ttk.Label(self, text='IMDB Get is a tool that uses the OMDB API to get info about movies.', wraplength=250).grid(row=1, column=0)
        # Label2
        ttk.Label(self, text='Author: Ahmed Elsayed').grid(row=2, column=0)
        # Label3
        ttk.Label(self, text='Copyright (c) 2023 by Ahmed Elsayed').grid(row=3, column=0)
        # Label4
        link = ttk.Label(self, text='https://github.com/Ahmed-E-86', foreground='blue', cursor='hand2')
        link.grid(row=4, column=0)
        link.bind("<Button-1>", lambda e: self.callback("https://github.com/Ahmed-E-86"))
        # Label5
        ttk.Label(self, text='Special thanks for:').grid(row=5, column=0)
        # Label6
        link = ttk.Label(self, text='https://icons8.com/icons', foreground='blue', cursor='hand2')
        link.grid(row=6, column=0)
        link.bind("<Button-1>", lambda e: self.callback("https://icons8.com/icons"))
        # Label7
        ttk.Label(self, text='for their amazing icons that I used with buttons and the logo of the application.', wraplength=250).grid(row=7, column=0)
    
    def callback(self, url):
        webbrowser.open_new(url)

if __name__ == "__main__":
    app = App()
    app.mainloop()