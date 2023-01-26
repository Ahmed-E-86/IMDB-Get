import log
import subprocess
import os.path
import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showerror
import configparser
from tktooltip import ToolTip

# Get the directory of the current python file
main_dir = os.path.realpath(os.path.dirname(__file__))

config = configparser.ConfigParser()
## Check for config.ini file
config_file = os.path.join(main_dir, 'config.ini')
if os.path.isfile(config_file):
    log.logger.debug('Config file is found')
    log.logger.debug(config_file)
else:
    log.logger.error('Config file is not found')
    showerror(title='Error!', message='Config file is not found, \nthe application is exiting now.')
    exit()

config.read(config_file)

source_lang = config['translate']['source']
target_lang = config['translate']['target']

languages = {'af': 'afrikaans', 'sq': 'albanian', 'am': 'amharic', 'ar': 'arabic', 'hy': 'armenian', 'az': 'azerbaijani', 'eu': 'basque', 'be': 'belarusian', 'bn': 'bengali', 'bs': 'bosnian', 'bg': 'bulgarian', 'ca': 'catalan', 'ceb': 'cebuano', 'ny': 'chichewa', 'zh-cn': 'chinese (simplified)', 'zh-tw': 'chinese (traditional)', 'co': 'corsican', 'hr': 'croatian', 'cs': 'czech', 'da': 'danish', 'nl': 'dutch', 'en': 'english', 'eo': 'esperanto', 'et': 'estonian', 'tl': 'filipino', 'fi': 'finnish', 'fr': 'french', 'fy': 'frisian', 'gl': 'galician', 'ka': 'georgian', 'de': 'german', 'el': 'greek', 'gu': 'gujarati', 'ht': 'haitian creole', 'ha': 'hausa', 'haw': 'hawaiian', 'iw': 'hebrew', 'he': 'hebrew', 'hi': 'hindi', 'hmn': 'hmong', 'hu': 'hungarian', 'is': 'icelandic', 'ig': 'igbo', 'id': 'indonesian', 'ga': 'irish', 'it': 'italian', 'ja': 'japanese', 'jw': 'javanese', 'kn': 'kannada', 'kk': 'kazakh', 'km': 'khmer', 'ko': 'korean', 'ku': 'kurdish (kurmanji)', 'ky': 'kyrgyz', 'lo': 'lao', 'la': 'latin', 'lv': 'latvian', 'lt': 'lithuanian', 'lb': 'luxembourgish', 'mk': 'macedonian', 'mg': 'malagasy', 'ms': 'malay', 'ml': 'malayalam', 'mt': 'maltese', 'mi': 'maori', 'mr': 'marathi', 'mn': 'mongolian', 'my': 'myanmar (burmese)', 'ne': 'nepali', 'no': 'norwegian', 'or': 'odia', 'ps': 'pashto', 'fa': 'persian', 'pl': 'polish', 'pt': 'portuguese', 'pa': 'punjabi', 'ro': 'romanian', 'ru': 'russian', 'sm': 'samoan', 'gd': 'scots gaelic', 'sr': 'serbian', 'st': 'sesotho', 'sn': 'shona', 'sd': 'sindhi', 'si': 'sinhala', 'sk': 'slovak', 'sl': 'slovenian', 'so': 'somali', 'es': 'spanish', 'su': 'sundanese', 'sw': 'swahili', 'sv': 'swedish', 'tg': 'tajik', 'ta': 'tamil', 'te': 'telugu', 'th': 'thai', 'tr': 'turkish', 'uk': 'ukrainian', 'ur': 'urdu', 'ug': 'uyghur', 'uz': 'uzbek', 'vi': 'vietnamese', 'cy': 'welsh', 'xh': 'xhosa', 'yi': 'yiddish', 'yo': 'yoruba', 'zu': 'zulu'}

class Options(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Options')
        self.geometry('400x650')
        self.resizable(0, 1)
        self.protocol("WM_DELETE_WINDOW", self.close)
        # Change the theme
        self.tk.call("source", os.path.join(main_dir, "azure.tcl"))
        self.tk.call("set_theme", "light")
        # Set the icon
        icon = os.path.join(main_dir, 'images', 'logo.png')
        self.iconphoto(False, tk.PhotoImage(file=icon))
        # pack options
        options1 = {'padx':5, 'pady':5, 'fill':'x', 'expand':True}
        options2 = {'padx':5, 'fill':'x', 'expand':True}
        
        ## The main frame
        main_frame = ttk.LabelFrame(self, text='Options')
        main_frame.pack(**options1)
        
        ## The OMDB API frame
        omdb_frame = ttk.LabelFrame(main_frame, text='OMDB API')
        omdb_frame.pack(**options1)

        # api key
        self.apikey_var = tk.StringVar()
        ttk.Label(omdb_frame, text='API key').pack(**options2)
        api_key_entry = ttk.Entry(omdb_frame, textvariable=self.apikey_var)
        api_key_entry.pack(**options2)
        # Check config file to set the Entry properly
        self.apikey_var.set(config['omdb']['api_key'])      
        # Get the typed text and save it to the config file
        self.bind('<Any-KeyPress>', self.type_apikey)
        ToolTip(api_key_entry, msg="The API key is necessary to fetch the data of the movies using the OMDB API.\nAPI keys has limited request by day, so it is important to get your own API key.", delay=0.3)

        # Plot
        ttk.Label(omdb_frame, text='Movie description').pack(**options2)
        self.plot_combox_var = tk.StringVar()
        self.plot_list = ['short', 'long']
        plot_menu = ttk.Combobox(omdb_frame, textvariable=self.plot_combox_var)
        plot_menu['values'] = self.plot_list
        plot_menu.pack(**options2)
        ToolTip(plot_menu, msg="Choose if you want to get the short or long description of the movies.", delay=0.3)
        # Call the function
        plot_menu.bind('<<ComboboxSelected>>', self.plot_changed)
        # Check config file to set the combobox properly
        if config['omdb']['plot'] == 'short':
            self.plot_combox_var.set('short')
        if config['omdb']['plot'] == 'long':
            self.plot_combox_var.set('long')
        
        # Posters checkbutton
        self.posters_var = tk.IntVar()
        poster_chkbtn = ttk.Checkbutton(omdb_frame, text='Download posters', style='Switch.TCheckbutton', command=self.posters_chkbtn_toggle, variable=self.posters_var, onvalue=1, offvalue=0)
        poster_chkbtn.pack(padx=10, fill='x', expand= True)
        ToolTip(poster_chkbtn, msg="Downloading the posters of the movies is a necessary if you want to view them later using the Excel Viewer.", delay=0.3)
        if config['omdb']['posters'] == 'True':
            self.posters_var.set(1)
        if config['omdb']['posters'] == 'False':
            self.posters_var.set(0)

        ## The files frame
        files_frame = ttk.LabelFrame(main_frame, text='Files')
        files_frame.pack(**options1)

        # Files checkbutton5
        self.fi_chkbtn_var5 = tk.IntVar()
        fi_chkbtn5 = ttk.Checkbutton(files_frame, text='Move movies with no rating', style='Switch.TCheckbutton', command=self.fi_chkbtn5_toggle, variable=self.fi_chkbtn_var5, onvalue=1, offvalue=0)
        fi_chkbtn5.pack(**options2)
        ToolTip(fi_chkbtn5, msg="Move movies with no rating to a separate folder inside the main folder.", delay=0.3)
        if config['files']['no_rating'] == 'True':
            self.fi_chkbtn_var5.set(1)
        if config['files']['no_rating'] == 'False':
            self.fi_chkbtn_var5.set(0)

        # Files checkbutton4
        self.fi_chkbtn_var4 = tk.IntVar()
        fi_chkbtn4 = ttk.Checkbutton(files_frame, text='Move movies with low IMDB rating', style='Switch.TCheckbutton', command=self.fi_chkbtn4_toggle, variable=self.fi_chkbtn_var4, onvalue=1, offvalue=0)
        fi_chkbtn4.pack(**options2)
        ToolTip(fi_chkbtn4, msg="Move movies with low imdb rating to a separate folder inside the main folder.", delay=0.3)
        if config['files']['low_imdb_rating'] == 'True':
            self.fi_chkbtn_var4.set(1)
        if config['files']['low_imdb_rating'] == 'False':
            self.fi_chkbtn_var4.set(0)

        # Files checkbutton3
        self.fi_chkbtn_var3 = tk.IntVar()
        fi_chkbtn3 = ttk.Checkbutton(files_frame, text='Move movies with high age rating', style='Switch.TCheckbutton', command=self.fi_chkbtn3_toggle, variable=self.fi_chkbtn_var3, onvalue=1, offvalue=0)
        fi_chkbtn3.pack(**options2)
        ToolTip(fi_chkbtn3, msg="Move movies with high age rating to a separate folder inside the main folder.\nMoved files are not included.", delay=0.3)
        if config['files']['adult_age_rating'] == 'True':
            self.fi_chkbtn_var3.set(1)
        if config['files']['adult_age_rating'] == 'False':
            self.fi_chkbtn_var3.set(0)

        # Files checkbutton1
        self.fi_chkbtn_var1 = tk.IntVar()
        fi_chkbtn1 = ttk.Checkbutton(files_frame, text='Rename files', style='Switch.TCheckbutton', command=self.fi_chkbtn1_toggle, variable=self.fi_chkbtn_var1, onvalue=1, offvalue=0)
        fi_chkbtn1.pack(**options2)
        ToolTip(fi_chkbtn1, msg="Rename files after cleaning their names from unwanted saved patterns.", delay=0.3)
        if config['files']['rename'] == 'True':
            self.fi_chkbtn_var1.set(1)
        if config['files']['rename'] == 'False':
            self.fi_chkbtn_var1.set(0)

        # Files checkbutton2
        self.fi_chkbtn_var2 = tk.IntVar()
        self.fi_chkbtn2 = ttk.Checkbutton(files_frame, text='Translate filenames', style='Switch.TCheckbutton', command=self.fi_chkbtn2_toggle, variable=self.fi_chkbtn_var2, onvalue=1, offvalue=0)
        self.fi_chkbtn2.pack(padx=25, fill='x', expand=True)
        ToolTip(self.fi_chkbtn2, msg="Translate filenames after cleaning their names from unwanted saved patterns.", delay=0.3)
        if config['files']['translate'] == 'True':
            self.fi_chkbtn_var2.set(1)
        if config['files']['translate'] == 'False':
            self.fi_chkbtn_var2.set(0)
        if config['files']['rename'] == 'False':
            self.fi_chkbtn2['state'] = 'disabled'

        ## The folders frame
        folder_frame = ttk.LabelFrame(main_frame, text='Folders')
        folder_frame.pack(**options1)

        # Folders checkbutton1
        self.fo_chkbtn_var1 = tk.IntVar()
        fo_chkbtn1 = ttk.Checkbutton(folder_frame, text='Rename folders', style='Switch.TCheckbutton', command=self.fo_chkbtn1_toggle, variable=self.fo_chkbtn_var1, onvalue=1, offvalue=0)
        fo_chkbtn1.pack(**options2)
        ToolTip(fo_chkbtn1, msg="Rename folders after cleaning their names from unwanted saved patterns.", delay=0.3)
        if config['folders']['rename'] == 'True':
            self.fo_chkbtn_var1.set(1)
        if config['folders']['rename'] == 'False':
            self.fo_chkbtn_var1.set(0)
        
        # Folders checkbutton2
        self.fo_chkbtn_var2 = tk.IntVar()
        self.fo_chkbtn2 = ttk.Checkbutton(folder_frame, text='Translate folder names', style='Switch.TCheckbutton', command=self.fo_chkbtn2_toggle, variable=self.fo_chkbtn_var2, onvalue=1, offvalue=0)
        self.fo_chkbtn2.pack(padx=25, fill='x', expand=True)
        ToolTip(self.fo_chkbtn2, msg="Translate folder names after cleaning their names from unwanted saved patterns.", delay=0.3)
        if config['folders']['translate'] == 'True':
            self.fo_chkbtn_var2.set(1)
        if config['folders']['translate'] == 'False':
            self.fo_chkbtn_var2.set(0)
        if config['folders']['rename'] == 'False':
            self.fo_chkbtn2['state'] = 'disabled'
        
        
        ## Translate frame
        translate_frame = ttk.LabelFrame(main_frame, text='Translate')
        translate_frame.pack(**options1)        
            
        # Source language
        ttk.Label(translate_frame, text='Source language').pack(**options2)
        self.src_lang_var = tk.StringVar()
        self.src_lang_list = [lang for lang in languages.values()]
        src_lang_menu = ttk.Combobox(translate_frame, textvariable=self.src_lang_var)
        src_lang_menu['values'] = self.src_lang_list
        # Call the function
        src_lang_menu.bind('<<ComboboxSelected>>', self.src_lang_changed)
        src_lang_keys = [lang for lang in languages.keys()]
        src_lang_index = src_lang_keys.index(source_lang)
        src_lang = self.src_lang_list[src_lang_index]
        self.src_lang_var.set(src_lang)
        src_lang_menu.pack(**options1)

        # Target language
        ttk.Label(translate_frame, text='Target language').pack(**options2)
        self.option_var2 = tk.StringVar()
        self.target_lang_list = [lang for lang in languages.values()]
        target_lang_menu = ttk.Combobox(translate_frame, textvariable=self.option_var2)
        target_lang_menu['values'] = self.target_lang_list
        # Call the function
        target_lang_menu.bind('<<ComboboxSelected>>', self.target_lang_changed)
        target_lang_keys = [lang for lang in languages.keys()]
        target_lang_index = target_lang_keys.index(target_lang)
        dest_lang = self.target_lang_list[target_lang_index]
        self.option_var2.set(dest_lang)
        target_lang_menu.pack(**options1)
    
    def close(self):
        self.destroy()
        subprocess.run(['python3', os.path.join(main_dir, 'main-tk.py')])
    
    # apikey function
    def type_apikey(self, event):
        with open(config_file, 'w') as configfile:
            config['omdb']['api_key'] = self.apikey_var.get()
            config.write(configfile)
    
    # Plot function
    def plot_changed(self, event):
        with open(config_file, 'w') as configfile:
            if self.plot_combox_var.get() == 'short':
                config['omdb']['plot'] = 'short'
            if self.plot_combox_var.get() == 'long':
                config['omdb']['plot'] = 'long'
            config.write(configfile)
    
    # Posters checkbutton function
    def posters_chkbtn_toggle(self):
        with open(config_file, 'w') as configfile:
            if self.posters_var.get() == 1:
                config['omdb']['posters'] = 'True'
            if self.posters_var.get() == 0:
                config['omdb']['posters'] = 'False'
            config.write(configfile)

    # Source language function
    def src_lang_changed(self, event):
        src_lang_index = self.src_lang_list.index(self.src_lang_var.get())
        src_lang_keys = [lang for lang in languages.keys()]
        src_lang = src_lang_keys[src_lang_index]
        with open(config_file, 'w') as configfile:
            config['translate']['source'] = src_lang
            config.write(configfile)

    # Target language function
    def target_lang_changed(self, event):
        target_lang_index = self.target_lang_list.index(self.option_var2.get())
        target_lang_keys = [lang for lang in languages.keys()]
        target_lang = target_lang_keys[target_lang_index]
        with open(config_file, 'w') as configfile:
            config['translate']['target'] = target_lang
            config.write(configfile)

    # Files checkbutton1 function
    def fi_chkbtn1_toggle(self):
        with open(config_file, 'w') as configfile:
            if self.fi_chkbtn_var1.get() == 1:
                config['files']['rename'] = 'True'
                self.fi_chkbtn2['state'] = '!disabled'
            if self.fi_chkbtn_var1.get() == 0:
                config['files']['rename'] = 'False'
                self.fi_chkbtn2['state'] = 'disabled'
            config.write(configfile)
    
    # Files checkbutton2 function
    def fi_chkbtn2_toggle(self):
        with open(config_file, 'w') as configfile:
            if self.fi_chkbtn_var2.get() == 1:
                config['files']['translate'] = 'True'
            if self.fi_chkbtn_var2.get() == 0:
                config['files']['translate'] = 'False'
            config.write(configfile)
    
    # Files checkbutton3 function
    def fi_chkbtn3_toggle(self):
        with open(config_file, 'w') as configfile:
            if self.fi_chkbtn_var3.get() == 1:
                config['files']['adult_age_rating'] = 'True'
            if self.fi_chkbtn_var3.get() == 0:
                config['files']['adult_age_rating'] = 'False'
            config.write(configfile)

    # Files checkbutton4 function
    def fi_chkbtn4_toggle(self):
        with open(config_file, 'w') as configfile:
            if self.fi_chkbtn_var4.get() == 1:
                config['files']['low_imdb_rating'] = 'True'
            if self.fi_chkbtn_var4.get() == 0:
                config['files']['low_imdb_rating'] = 'False'
            config.write(configfile)
    
    # Files checkbutton5 function
    def fi_chkbtn5_toggle(self):
        with open(config_file, 'w') as configfile:
            if self.fi_chkbtn_var5.get() == 1:
                config['files']['no_rating'] = 'True'
            if self.fi_chkbtn_var5.get() == 0:
                config['files']['no_rating'] = 'False'
            config.write(configfile)

    # Folder checkbutton1 function
    def fo_chkbtn1_toggle(self):
        with open(config_file, 'w') as configfile:
            if self.fo_chkbtn_var1.get() == 1:
                config['folders']['rename'] = 'True'
                self.fo_chkbtn2['state'] = '!disabled'
            if self.fo_chkbtn_var1.get() == 0:
                config['folders']['rename'] = 'False'
                self.fo_chkbtn2['state'] = 'disabled'
            config.write(configfile)

    # Folder checkbutton2 function
    def fo_chkbtn2_toggle(self):
        with open(config_file, 'w') as configfile:
            if self.fo_chkbtn_var2.get() == 1:
                config['folders']['translate'] = 'True'
            if self.fo_chkbtn_var2.get() == 0:
                config['folders']['translate'] = 'False'
            config.write(configfile)

if __name__ == "__main__":
    opt = Options()
    opt.mainloop()