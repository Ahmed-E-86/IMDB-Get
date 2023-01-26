import log
import configparser
import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showerror
from tkinter.scrolledtext import ScrolledText
import os
import json
import urllib.request
import webbrowser
from PIL import Image, ImageTk

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
        self.geometry('1000x650')
        self.title("Movie viewer")
        # Change the theme
        self.tk.call("source", os.path.join(main_dir, "azure.tcl"))
        self.tk.call("set_theme", "light")
        # Set the icon
        icon = os.path.join(main_dir, 'images', 'logo.png')
        self.iconphoto(False, tk.PhotoImage(file=icon))

        ## Search textbox
        self.txt_var1 = tk.StringVar()
        search_txt = ttk.Entry(self, textvariable=self.txt_var1, font=14)
        search_txt.grid(row=0, column=1, sticky='ew', padx=5, pady=5)
        search_txt.focus()
        search_txt.bind('<Return>', self.search)

        ## Search button
        img2 = ImageTk.PhotoImage(Image.open(os.path.join(main_dir, 'images/search.png')))
        self.btn2 = ttk.Button(self, text='Search', image=img2, compound='right', command=self.search)
        self.btn2.image = img2
        self.btn2.grid(row=0, column=2, sticky='w', padx=5, pady=5)

        # Clear previous search
        self.chkbtn_var1 = tk.IntVar()
        chkbtn1 = ttk.Checkbutton(self, text='Clear previous search', style='Switch.TCheckbutton', variable=self.chkbtn_var1, onvalue=1, offvalue=0)
        chkbtn1.grid(row=0, column=3, sticky='w', padx=5, pady=5)

        ## Year textbox
        self.txt_var2 = tk.StringVar()
        search_txt = ttk.Entry(self, textvariable=self.txt_var2, font=14)
        search_txt.grid(row=1, column=1, sticky='ew', padx=5, pady=5)
        ttk.Label(self, text='<== Year').grid(row=1, column=2, sticky='w', padx=5, pady=5)

        ## Poster
        img = None
        # Image label
        self.image_lbl = ttk.Label(self, text='Image is not loaded', image=img)
        self.image_lbl.grid(row=2, column=3, rowspan=10, padx=(20,0))
        self.image_lbl.image = img

        ## Title
        ttk.Label(self, text='Movie Name:', font=14).grid(row=2, column=0, sticky='w', padx=20, pady=5)
        self.title_lbl = ttk.Label(text='                    ', font=14, background='grey')
        self.title_lbl.grid(row=2, column=1, sticky='w', padx=5, pady=5)

        ## Year
        ttk.Label(self, text='Release Year:', font=14).grid(row=3, column=0, sticky='w', padx=20, pady=5)
        self.year_lbl = ttk.Label(text='                    ', font=14, background='grey')
        self.year_lbl.grid(row=3, column=1, sticky='w', padx=5, pady=5)

        ## Rating
        ttk.Label(self, text='IMDB Rating:', font=14).grid(row=4, column=0, sticky='w', padx=20, pady=5)
        self.rating_lbl = ttk.Label(text='                    ', font=14, background='grey')
        self.rating_lbl.grid(row=4, column=1, sticky='w', padx=5, pady=5)

        ## Age Rating
        ttk.Label(self, text='Age Rating:', font=14).grid(row=5, column=0, sticky='w', padx=20, pady=5)
        self.age_lbl = ttk.Label(text='                    ', font=14, background='grey')
        self.age_lbl.grid(row=5, column=1, sticky='w', padx=5, pady=5)

        ## Genre
        ttk.Label(self, text='Genre:', font=14).grid(row=6, column=0, sticky='w', padx=20, pady=5)
        self.genre_lbl = ttk.Label(text='                    ', font=14, background='grey')
        self.genre_lbl.grid(row=6, column=1, sticky='w', padx=5, pady=5)

        ## Language
        ttk.Label(self, text='Language:', font=14).grid(row=7, column=0, sticky='w', padx=20, pady=5)
        self.lang_lbl = ttk.Label(text='                    ', font=14, background='grey')
        self.lang_lbl.grid(row=7, column=1, sticky='w', padx=5, pady=5)

        ## Actors
        ttk.Label(self, text='Actors:', font=14).grid(row=8, column=0, sticky='w', padx=20, pady=5)
        self.actors_lbl = ttk.Label(text='                    ', font=14, wraplength=350, background='grey')
        self.actors_lbl.grid(row=8, column=1, sticky='w', padx=5, pady=5)

        ## Awards
        ttk.Label(self, text='Awards:', font=14).grid(row=9, column=0, sticky='w', padx=20, pady=5)
        self.awards_lbl = ttk.Label(text='                    ', font=14, background='grey')
        self.awards_lbl.grid(row=9, column=1, sticky='w', padx=5, pady=5)

        ## Plot
        ttk.Label(self, text='Plot:', font=14).grid(row=10, column=0, sticky='enw', padx=20, pady=5)
        self.plot_txt = ScrolledText(self, height=6, font=14, wrap='word', width=50)
        self.plot_txt['state'] = 'disabled'
        self.plot_txt.grid(row=10, column=1, sticky='w', padx=5, pady=5, columnspan=2)

        ## IMDB url
        ttk.Label(self, text='IMDB url:', font=14).grid(row=11, column=0, sticky='w', padx=20, pady=5)
        self.url_lbl = ttk.Label(text='                    ', font=14, foreground='blue', cursor='hand2')
        self.url_lbl.grid(row=11, column=1, sticky='w', padx=5, pady=5)
        self.url_lbl.bind("<Button-1>", lambda e: self.callback(self.url_lbl['text']))
    
    def search(self, event=None):
        movie_name = self.txt_var1.get()
        year = self.txt_var2.get()
        self.fetch_data(movie_name, year)

    def fetch_data(self, movie_name, year):
        ## omdb configuarations
        api_key = config['omdb']['api_key']
        plot = config['omdb']['plot']
        log.logger.info('The plot for imdb is: %s' %plot)
        # Check for the api_key
        if api_key == '0':
            log.logger.error('The API key is not set, using the default API key.')
            api_key = '9b925aaa'
        else:
            log.logger.debug('The API key for imdb is: %s' %api_key)

        # Create JSON folder if it does not exist
        json_dir = os.path.join(main_dir, "(JSON)")
        if os.path.isdir(json_dir) == False:
            os.mkdir(json_dir)

        # Check for cashed json file first
        json_path = os.path.join(json_dir, movie_name+".json")
        if os.path.isfile(json_path) == True and self.chkbtn_var1.get() == 0:
            log.logger.info('The data for the movie is downloaded before.')
            log.logger.debug(json_path)
            # Load data from the stored json file
            json_file = open(json_path, "r", encoding="utf-8")
            json_data = json.load(json_file)
            # Store the required data for the movie
            title = movie_name.replace("+", " ")
            Year = json_data['Year']
            Rating = json_data['imdbRating']
            AgeRating = json_data['Rated']
            Genre = json_data['Genre']
            Actors = json_data['Actors']
            Plot = json_data['Plot']
            Language = json_data['Language']
            Awards = json_data['Awards']
            Poster = json_data['Poster']
            Url = "https://www.imdb.com/title/" + json_data['imdbID']
            # Close the opened json file
            json_file.close()
        else:
            # Fix the movie name to be suitable for the url
            movie_name = movie_name.replace(" ", "+")
            # Bring the year of the movie from the previous stored list
            if year == '':
                log.logger.info('Year is not found in the filename, this may lead to the wrong result.')
                url = "https://www.omdbapi.com/?t=" + movie_name + "&plot=" + plot + "&apikey=" + api_key
                log.logger.debug(url)
            else:
                log.logger.info('Year is found in the filename.')
                y = year
                log.logger.info('Year found: %s' %y)
                url = "https://www.omdbapi.com/?t=" + movie_name + "&y=" + y + "&plot=" + plot + "&apikey=" + api_key
                log.logger.debug(url)
            if self.check_conn() is True:
                log.logger.info('Connection to the internet is online.')
                # Open the url using the internal urllib module
                response = urllib.request.urlopen(url)
                # Open the JSON file brought from omdbapi
                json_data = json.load(response)
                # Respons will be True if the name and year are correct
                if json_data['Response'] == "True":
                    log.logger.info('Got a response from the website.')
                    # Create a json file with the name of the movie
                    json_file = open(json_path, "w", encoding="utf-8")
                    json.dump(json_data, json_file, ensure_ascii=False, indent=4)
                    json_file.close()
                    # Store the required data for the movie
                    title = movie_name.replace("+", " ")
                    Year = json_data['Year']
                    Rating = json_data['imdbRating']
                    AgeRating = json_data['Rated']
                    Genre = json_data['Genre']
                    Actors = json_data['Actors']
                    Plot = json_data['Plot']
                    Language = json_data['Language']
                    Awards = json_data['Awards']
                    Poster = json_data['Poster']
                    Url = "https://www.imdb.com/title/" + json_data['imdbID']
                elif json_data['Response'] == "False":
                    log.logger.info('Did not recieve a response from the website (attempt1), trying again..')
                    # Search for the movie without the year to see if it will solve the issue
                    url = "https://www.omdbapi.com/?t=" + movie_name + "&plot=" + plot + "&apikey=" + api_key
                    response = urllib.request.urlopen(url)
                    json_data = json.load(response)
                    if json_data['Response'] == "True":
                        log.logger.info('Got a response after removing the year from the url.')
                        # Create a json file with the name of the movie
                        json_file = open(json_path, "w", encoding="utf-8")
                        json.dump(json_data, json_file, ensure_ascii=False, indent=4)
                        json_file.close()
                        # Store the required data for the movie
                        title = movie_name.replace("+", " ")
                        Year = json_data['Year']
                        Rating = json_data['imdbRating']
                        AgeRating = json_data['Rated']
                        Genre = json_data['Genre']
                        Actors = json_data['Actors']
                        Plot = json_data['Plot']
                        Language = json_data['Language']
                        Awards = json_data['Awards']
                        Poster = json_data['Poster']
                        Url = "https://www.imdb.com/title/" + json_data['imdbID']
                    else:
                        log.logger.info('Did not recieve a response from the website (attempt2)')
                        # Add null values if nothing of the above worked
                        title = movie_name.replace("+", " ")
                        log.logger.info('Skipping this movie...')
                        Year = "NA"
                        Rating = "NA"
                        AgeRating = "NA"
                        Genre = "NA"
                        Actors = "NA"
                        Plot = "NA"
                        Language = "NA"
                        Awards = "NA"
                        Poster = "NA"
                        Url = "NA"
                        showerror(title='Not found!', message='The requested movie is not found in the database, please try a different name.')
            else:
                log.logger.error('The internet connection is offline')
                showerror(title='Error', message='The internet connection is offline, please try again later.')
                return
        
        # Download the poster
        file_path = os.path.join(main_dir, "(posters)")
        if os.path.isdir(file_path) == False:
            os.mkdir(file_path)
        filename = Poster.split('/')[-1]
        full_path = os.path.join(file_path, filename)
        # Skip the file if it is already downloaded
        if os.path.isfile(full_path):
            log.logger.debug('The file is already downloaded -> %s' %full_path)
        else:
            # Check internet connection
            if self.check_conn() is True:
                try:
                    response = urllib.request.urlopen(Poster)
                    ## Check response before downloading
                    if response.code == 200:
                        log.logger.debug('Downloading Poster %s...' %Poster)
                        try:
                            urllib.request.urlretrieve(Poster, full_path)
                        except Exception:
                            log.logger.error('Saving the poster is failed.')
                            return
                    else:
                        log.logger.error('Downloading failed for Poster %s' %Poster)
                        showerror(title='Error!', message='Downloading failed for the poster.')
                        return
                # Avoid null urls
                except ValueError:
                    log.logger.error('The URL is invalid, skipping it...')
                    return
            else:
                log.logger.error('The internet connection is offline.')
                showerror(title='Error', message='The internet connection is offline, please try again later.')
                return
        
        # Display the downloaded data
        self.title_lbl['text'] = title.capitalize()
        self.year_lbl['text'] = Year
        self.rating_lbl['text'] = Rating
        self.age_lbl['text'] = AgeRating
        self.genre_lbl['text'] = Genre
        self.lang_lbl['text'] = Language
        self.actors_lbl['text'] = Actors
        self.awards_lbl['text'] = Awards
        self.plot_txt['state'] = 'normal'
        self.plot_txt.delete(1.0, 'end')
        self.plot_txt.insert('end', Plot)
        self.plot_txt['state'] = 'disabled'
        self.url_lbl['text'] = Url
        if Poster.endswith('A'):
            self.image_lbl['image'] = None
            self.image_lbl.image = None
        else:
            try:
                image = Image.open(full_path)
                img = ImageTk.PhotoImage(image)
                self.image_lbl['image'] = img
                self.image_lbl.image = img
            except FileNotFoundError:
                log.logger.error('The image file is not found.')
                self.image_lbl['image'] = None
                self.image_lbl.image = None
    
    def check_conn(self):
        try:
            Url = 'https://www.google.com'
            urllib.request.urlopen(Url, timeout=3)
            return True
        except Exception as error:
            log.logger.error("Connection is offline.")
            log.logger.error(str(error))
            return False
    
    def callback(self, url):
        webbrowser.open_new(url)

if __name__ == "__main__":
    m_viewer = App()
    m_viewer.mainloop()