import log
import configparser
from tkinter.messagebox import showerror, showinfo, askyesno
import os
import re
from datetime import date
import json
import shutil
import urllib.request

try:
    import googletrans
    log.logger.debug('Googletrans is installed.')
except ImportError:
    log.logger.debug('Googletrans is not installed.')
    ask1 = askyesno(title='Import failed!', message='Googletrans is not installed. \nDo you want to install it?')
    if ask1:
        process1 = subprocess.run(['pip', 'install', 'googletrans==3.1.0a0'])
    else:
        exit()
    if process1.returncode == 0:
        showinfo(title='Success!', message='Googletrans is installed successfully.')
        import googletrans
    else:
        showerror(title='Error!', message='Googletrans installation is failed.')
        log.logger.error('Googletrans installation is failed.')
        exit()

try:
    import pandas as pd
    log.logger.debug('Pandas is installed.')
except ImportError:
    log.logger.debug('Pandas is not installed.')
    ask2 = askyesno(title='Import failed!', message='Pandas is not installed. \nDo you want to install it?')
    if ask2:
        process2 = subprocess.run(['pip', 'install', 'pandas'])
    else:
        exit()
    if process2.returncode == 0:
        showinfo(title='Success!', message='Pandas is installed successfully.')
        import pandas as pd
    else:
        showerror(title='Error!', message='Pandas installation is failed.')
        log.logger.error('Pandas installation is failed.')
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

## Reserved for the open folder dialog by Tkinter
opened_dir = ''

class Run:
    def clean_movie_name(name):
        ## Remove unwanted numbers from the end of the string
        name = re.sub('[_][0-9]{1}$', '', name)
        name = re.sub('[0-9_]{5,9}$', '', name)
        
        ## Remove the year from the string and store it to be used later
        year = ''
        for y in range(1900, int(date.today().year)+1):
            if str(y) in name:
                year = str(y)
                name = name.replace(str(y), '')

        ## Import the blocklisted words from the text file
        if os.path.isfile(os.path.join(main_dir, 'blocklist.txt')):
            text_file = open(os.path.join(main_dir, 'blocklist.txt'), 'r')
        else:
            with open(os.path.join(main_dir, 'blocklist.txt'), 'w') as text_file:
                text_file.write('')
            text_file = open(os.path.join(main_dir, 'blocklist.txt'), 'r')
        ## Extract words from the text file
        blocklist = [line.strip() for line in text_file]
        ## Change all characters to lowercase
        blocklist = [word.lower() for word in blocklist]
        text_file.close()

        ## remove all the blocklisted words imported from the text file from the name
        name = name.lower()
        for word in blocklist:
            if word in name:
                name = name.replace(word, '')
        
        ## Remove special characters from the beginning of the names
        name = re.sub('^[^a-zA-Z0-9]{1,3}', '', name)
        ## Remove special characters from the ending of the names
        name = re.sub('[^a-zA-Z0-9]{1,7}$', '', name)
        ## Replace special characters in the middle of the name with spaces
        name = re.sub('[^a-zA-Z0-9]', ' ', name)

        ## Remove all the unwanted words from a predefined Python list
        # A list with all unwanted words
        unwanted_words = ['240p', '360p', '480p', '576p', '720p', '1080i', '1080p', '1440p', '2160p', '240', '360', '480', '576', '720', '1080', '1440', '2160', 'x264', 'x265', 'hdtv', ' hd tv', 'webrip', ' web rip', 'dvdrip', ' dvd rip', '1cdrip', ' bdrip', ' brrip', ' dvdscr', ' dvd scr', ' web dl', ' web hd', ' web cam', ' hdcam', ' hd cam', 'bluray', 'xvid', 'divx', ' aac', ' ac3', ' mp3', 'subtitles', ' esub', ' e sub', ' nl', ' dts', ' ts', ' dub', ' cam']
        # Adding a space before some words inside the list avoids removing matched letters in the middle of a movie name.
        for word in unwanted_words:
            if word in name:
                name = name.replace(word, '')

        # Finally, remove the spaces in the name
        name = name.strip()
        return name, year
    
    def check_conn():
        try:
            url = 'https://www.google.com'
            urllib.request.urlopen(url, timeout=3)
            return True
        except Exception as error:
            log.logger.error("Connection is offline.")
            log.logger.error(str(error))
            return False
    
    def translate(word):
        source_lang = config['translate']['source']
        target_lang = config['translate']['target']
        translator = googletrans.Translator()
        ## Check connection before starting
        if Run.check_conn() is True:
            translation = translator.translate(word, src=source_lang, dest=target_lang)
            log.logger.info("%s (%s) -> Translation (%s): %s" %(word, source_lang, target_lang, translation.text))
        else:
            return
        return translation.text
    
    def create_json_file():
        # list of all the formats of video files
        video_extensions = ['.webm', '.mkv', '.flv', '.vob', '.ogv', '.ogg', '.avi', '.MTS', '.M2TS', '.TS', '.mov', '.qt', '.wmv', '.yuv', '.rm', '.rmvb', '.viv', '.asf', '.amv', '.mp4', '.m4p', '.m4v', '.mpg', '.mp2', '.mpeg', '.mpe', '.mpv', '.m2v', '.svi', '.3gp', '.3g2', '.flv', '.f4v', '.f4p', '.f4a', '.f4b']

        # Create the json file
        json_file = open(os.path.join(opened_dir, 'files.json'), 'w', encoding="utf-8")
        data = {}
        data['files'] = []
        # Get the data of the video files and add them to the created json file
        for root, dirs, files in os.walk(opened_dir):
            for file in files:
                if os.path.splitext(file)[1] in video_extensions:
                    json_file = open(os.path.join(opened_dir, 'files.json'), 'w', encoding="utf-8")
                    # Files
                    filename = file.replace(os.path.splitext(file)[1], '')
                    extension = os.path.splitext(file)[1]
                    file_path = os.path.join(root, file)
                    # Folders
                    folder_path = os.path.dirname(file_path)
                    folder_parent = os.path.dirname(folder_path)
                    folder_name = os.path.basename(folder_path)
                    renamed_filename, year = Run.clean_movie_name(filename)
                    
                    # Add data to the dictionary
                    data['files'].append({'File': file, 'Renamed filename': renamed_filename, 'Year': year, 'Original Filename': filename, 'File extension': extension, 'File path': file_path, 'Original foldername': folder_name, 'Folder path': folder_path, 'Folder parent': folder_parent})
                    # Write the dictionary to the json file
                    json.dump(data, json_file, ensure_ascii=False, indent=4)
        json_file.close()

    def get_from_json():
        # Open json file
        json_file = open(os.path.join(opened_dir, 'files.json'), 'r', encoding="utf-8")
        data = json.load(json_file)
        # Get movieNames from the json file
        n = 0
        movie_names = []
        for loop in range(0, len(data['files'])):
            movie_names.append(data['files'][n]['Renamed filename'])
            n+=1
        # Get years from the json file
        n = 0
        years = []
        for loop in range(0, len(data['files'])):
            years.append(data['files'][n]['Year'])
            n+=1
        return movie_names, years
    
    def fetch_data(movie_names, years):
        ## omdb configuarations
        api_key = config['omdb']['api_key']
        plot = config['omdb']['plot']
        log.logger.info('The plot for omdb is: %s' %plot)
        # Check for the api_key
        if api_key == '0':
            log.logger.error('The API key is not set, using the default API key.')
            api_key = '9b925aaa'
        else:
            log.logger.debug('The API key for omdb is: %s' %api_key)

        # Initialize 11 lists that will be used to save the fetched data from JSON files
        global Poster
        Title, Year, Rating, AgeRating, Genre, Actors, Plot, Language, Awards, Poster, Url = ([] for list in range(11))
        # List of ratings suitable for adults (18+)
        Adult_rating = ['NC-17', '18A', 'R', 'TV-MA']
        global NSFW
        NSFW = []
        global low_imdb_rating
        low_imdb_rating = []
        global NotRated
        NotRated = []
        # Create JSON folder if it does not exist
        json_dir = os.path.join(opened_dir, "(JSON)")
        if os.path.isdir(json_dir) == False:
            os.mkdir(json_dir)
        num = 0
        for loop in range(0, len(movie_names)):
            movieName = movie_names[num]
            log.logger.info("\nMovie number%i: (%s)" %(num+1, movieName.title()))
            # Check for cashed json file first
            json_path = os.path.join(json_dir, movieName+".json")
            if os.path.isfile(json_path) == True:
                log.logger.info('The data for the movie is downloaded before.')
                log.logger.debug(json_path)
                # Load data from the stored json file
                json_file = open(json_path, "r", encoding="utf-8")
                json_data = json.load(json_file)
                # Store the required data for the movie
                title = movieName.replace("+", " ")
                imdb_year = json_data['Year']
                imdb_rating = json_data['imdbRating']
                imdb_age_rating = json_data['Rated']
                imdb_genre = json_data['Genre']
                imdb_actors = json_data['Actors']
                imdb_plot = json_data['Plot']
                imdb_language = json_data['Language']
                imdb_awards = json_data['Awards']
                imdb_poster = json_data['Poster']
                imdb_url = "https://www.imdb.com/title/" + json_data['imdbID']
                # Close the opened json file
                json_file.close()
            else:
                # Fix the movie name to be suitable for the url
                movieName = movieName.replace(" ", "+")
                # Bring the year of the movie from the previous stored list
                if years[num] == '':
                    log.logger.info('Year is not found in the filename, this may lead to the wrong result.')
                    url = "https://www.omdbapi.com/?t=" + movieName + "&plot=" + plot + "&apikey=" + api_key
                    log.logger.debug(url)
                else:
                    log.logger.info('Year is found in the filename.')
                    y = years[num]
                    log.logger.info('Year found: %s' %y)
                    url = "https://www.omdbapi.com/?t=" + movieName + "&y=" + y + "&plot=" + plot + "&apikey=" + api_key
                    log.logger.debug(url)
                if Run.check_conn() is True:
                    log.logger.debug('Connection to the internet is online.')
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
                        title = movieName.replace("+", " ")
                        imdb_year = json_data['Year']
                        imdb_rating = json_data['imdbRating']
                        imdb_age_rating = json_data['Rated']
                        imdb_genre = json_data['Genre']
                        imdb_actors = json_data['Actors']
                        imdb_plot = json_data['Plot']
                        imdb_language = json_data['Language']
                        imdb_awards = json_data['Awards']
                        imdb_poster = json_data['Poster']
                        imdb_url = "https://www.imdb.com/title/" + json_data['imdbID']
                    elif json_data['Response'] == "False":
                        log.logger.info('Did not recieve a response from the website (attempt1), trying again..')
                        # Search for the movie without the year to see if it will solve the issue
                        url = "https://www.omdbapi.com/?t=" + movieName + "&plot=" + plot + "&apikey=" + api_key
                        response = urllib.request.urlopen(url)
                        json_data = json.load(response)
                        if json_data['Response'] == "True":
                            log.logger.info('Got a response after removing the year from the url.')
                            # Create a json file with the name of the movie
                            json_file = open(json_path, "w", encoding="utf-8")
                            json.dump(json_data, json_file, ensure_ascii=False, indent=4)
                            json_file.close()
                            # Store the required data for the movie
                            title = movieName.replace("+", " ")
                            imdb_year = json_data['Year']
                            imdb_rating = json_data['imdbRating']
                            imdb_age_rating = json_data['Rated']
                            imdb_genre = json_data['Genre']
                            imdb_actors = json_data['Actors']
                            imdb_plot = json_data['Plot']
                            imdb_language = json_data['Language']
                            imdb_awards = json_data['Awards']
                            imdb_poster = json_data['Poster']
                            imdb_url = "https://www.imdb.com/title/" + json_data['imdbID']
                        else:
                            log.logger.info('Did not recieve a response from the website (attempt2)')
                            # Add null values if nothing of the above worked
                            title = movieName.replace("+", " ")
                            log.logger.info('Skipping this movie...')
                            imdb_year = "NA"
                            imdb_rating = "NA"
                            imdb_age_rating = "NA"
                            imdb_genre = "NA"
                            imdb_actors = "NA"
                            imdb_plot = "NA"
                            imdb_language = "NA"
                            imdb_awards = "NA"
                            imdb_poster = "NA"
                            imdb_url = "NA"
                else:
                    log.logger.error('The internet connection is offline')
                    showerror(title='Error', message='The internet connection is offline, please try again later.')
                    return
            num +=1
            # Store all the fetched data from omdbapi
            log.logger.debug('Storing the downloaded data....')
            Title.append(title)
            Year.append(imdb_year)
            Rating.append(imdb_rating)
            AgeRating.append(imdb_age_rating)
            Genre.append(imdb_genre)
            Actors.append(imdb_actors)
            Plot.append(imdb_plot)
            Language.append(imdb_language)
            Awards.append(imdb_awards)
            Poster.append(imdb_poster)
            Url.append(imdb_url)
            # Store the name of the movie if its rating is not available
            if config['files']['no_rating'] == 'True':
                if imdb_rating == 'NA' or imdb_rating == 'N/A':
                    try:
                        log.logger.info('The movie %s has no rating' %title)
                        NotRated.append(title)
                    except Exception:
                        continue
            # Store the name of the movie if its rating is low
            if config['files']['low_imdb_rating'] == 'True':
                # Avoid errors in case imdb_rating == 'N/A' or 'NA'
                try:
                    # Check if the rating of the movie is low
                    if float(imdb_rating) < 5.0:
                        log.logger.info('The rating of (%s) is low.' %title)
                        low_imdb_rating.append(title)
                except ValueError:
                    continue
            # Store the name of the movie that contains high age rating
            if config['files']['adult_age_rating'] == 'True':
                if imdb_age_rating in Adult_rating:
                    log.logger.info('The age rating of (%s) is high.' %title)
                    NSFW.append(title)
        ## Create the excel file
        # Merge all the required list for pandas
        data_list = list(zip(Title, Year, Rating, AgeRating, Genre, Actors, Plot, Language, Awards, Poster, Url))
        # Initiate Pandas' DataFrame
        movie_data = pd.DataFrame(data_list, columns = ['Title', 'Year', 'Rating', 'AgeRating', 'Genre', 'Actors', 'Plot', 'Language', 'Awards', 'Poster', 'URL'])
        excel_file = os.path.join(opened_dir, "movies.xlsx")
        # Remove the excel file if it is already exists
        if os.path.isfile(excel_file):
            os.remove(excel_file)
        # Save the excel file using Pandas
        log.logger.debug('Storing downloaded data to the excel file...')
        movie_data.to_excel(excel_file)
        # Check for the excel file
        if os.path.isfile(excel_file):
            log.logger.info('The excel file is created successfully.')
    
    def process_text(movie_names, years):
        ## omdb configuarations
        api_key = config['omdb']['api_key']
        plot = config['omdb']['plot']
        log.logger.info('The plot for omdb is: %s' %plot)
        # Check for the api_key
        if api_key == '0':
            log.logger.error('The API key is not set, using the default API key.')
            api_key = '9b925aaa'
        else:
            log.logger.debug('The API key for omdb is: %s' %api_key)

        # Initialize 11 lists that will be used to save the fetched data from JSON files
        global Poster
        Title, Year, Rating, AgeRating, Genre, Actors, Plot, Language, Awards, Poster, Url = ([] for list in range(11))
        # Create JSON folder if it does not exist
        json_dir = os.path.join(main_dir, "(JSON)")
        if os.path.isdir(json_dir) == False:
            os.mkdir(json_dir)
        num = 0
        for loop in range(0, len(movie_names)):
            movieName = movie_names[num]
            log.logger.info("\nMovie number%i: (%s)" %(num+1, movieName.title()))
            # Check for cashed json file first
            json_path = os.path.join(json_dir, movieName+".json")
            if os.path.isfile(json_path) == True:
                log.logger.info('The data for the movie is downloaded before.')
                log.logger.debug(json_path)
                # Load data from the stored json file
                json_file = open(json_path, "r", encoding="utf-8")
                json_data = json.load(json_file)
                # Store the required data for the movie
                title = movieName.replace("+", " ")
                imdb_year = json_data['Year']
                imdb_rating = json_data['imdbRating']
                imdb_age_rating = json_data['Rated']
                imdb_genre = json_data['Genre']
                imdb_actors = json_data['Actors']
                imdb_plot = json_data['Plot']
                imdb_language = json_data['Language']
                imdb_awards = json_data['Awards']
                imdb_poster = json_data['Poster']
                imdb_url = "https://www.imdb.com/title/" + json_data['imdbID']
                # Close the opened json file
                json_file.close()
            else:
                # Fix the movie name to be suitable for the url
                movieName = movieName.replace(" ", "+")
                # Bring the year of the movie from the previous stored list
                if years[num] == '':
                    log.logger.info('Year is not found in the filename, this may lead to the wrong result.')
                    url = "https://www.omdbapi.com/?t=" + movieName + "&plot=" + plot + "&apikey=" + api_key
                    log.logger.debug(url)
                else:
                    log.logger.info('Year is found in the filename.')
                    y = years[num]
                    log.logger.info('Year found: %s' %y)
                    url = "https://www.omdbapi.com/?t=" + movieName + "&y=" + y + "&plot=" + plot + "&apikey=" + api_key
                    log.logger.debug(url)
                if Run.check_conn() is True:
                    log.logger.debug('Connection to the internet is online.')
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
                        title = movieName.replace("+", " ")
                        imdb_year = json_data['Year']
                        imdb_rating = json_data['imdbRating']
                        imdb_age_rating = json_data['Rated']
                        imdb_genre = json_data['Genre']
                        imdb_actors = json_data['Actors']
                        imdb_plot = json_data['Plot']
                        imdb_language = json_data['Language']
                        imdb_awards = json_data['Awards']
                        imdb_poster = json_data['Poster']
                        imdb_url = "https://www.imdb.com/title/" + json_data['imdbID']
                    elif json_data['Response'] == "False":
                        log.logger.info('Did not recieve a response from the website (attempt1), trying again..')
                        # Search for the movie without the year to see if it will solve the issue
                        url = "https://www.omdbapi.com/?t=" + movieName + "&plot=" + plot + "&apikey=" + api_key
                        response = urllib.request.urlopen(url)
                        json_data = json.load(response)
                        if json_data['Response'] == "True":
                            log.logger.info('Got a response after removing the year from the url.')
                            # Create a json file with the name of the movie
                            json_file = open(json_path, "w", encoding="utf-8")
                            json.dump(json_data, json_file, ensure_ascii=False, indent=4)
                            json_file.close()
                            # Store the required data for the movie
                            title = movieName.replace("+", " ")
                            imdb_year = json_data['Year']
                            imdb_rating = json_data['imdbRating']
                            imdb_age_rating = json_data['Rated']
                            imdb_genre = json_data['Genre']
                            imdb_actors = json_data['Actors']
                            imdb_plot = json_data['Plot']
                            imdb_language = json_data['Language']
                            imdb_awards = json_data['Awards']
                            imdb_poster = json_data['Poster']
                            imdb_url = "https://www.imdb.com/title/" + json_data['imdbID']
                        else:
                            log.logger.info('Did not recieve a response from the website (attempt2)')
                            # Add null values if nothing of the above worked
                            title = movieName.replace("+", " ")
                            log.logger.info('Skipping this movie...')
                            imdb_year = "NA"
                            imdb_rating = "NA"
                            imdb_age_rating = "NA"
                            imdb_genre = "NA"
                            imdb_actors = "NA"
                            imdb_plot = "NA"
                            imdb_language = "NA"
                            imdb_awards = "NA"
                            imdb_poster = "NA"
                            imdb_url = "NA"
                else:
                    log.logger.error('The internet connection is offline')
                    showerror(title='Error', message='The internet connection is offline, please try again later.')
                    return
            num +=1
            # Store all the fetched data from omdbapi
            log.logger.debug('Storing the downloaded data....')
            Title.append(title)
            Year.append(imdb_year)
            Rating.append(imdb_rating)
            AgeRating.append(imdb_age_rating)
            Genre.append(imdb_genre)
            Actors.append(imdb_actors)
            Plot.append(imdb_plot)
            Language.append(imdb_language)
            Awards.append(imdb_awards)
            Poster.append(imdb_poster)
            Url.append(imdb_url)

        ## Create the excel file
        # Merge all the required list for pandas
        data_list = list(zip(Title, Year, Rating, AgeRating, Genre, Actors, Plot, Language, Awards, Poster, Url))
        # Initiate Pandas' DataFrame
        movie_data = pd.DataFrame(data_list, columns = ['Title', 'Year', 'Rating', 'AgeRating', 'Genre', 'Actors', 'Plot', 'Language', 'Awards', 'Poster', 'URL'])
        excel_file = os.path.join(main_dir, "movies.xlsx")
        # Remove the excel file if it is already exists
        if os.path.isfile(excel_file):
            os.remove(excel_file)
        # Save the excel file using Pandas
        log.logger.debug('Storing downloaded data to the excel file...')
        movie_data.to_excel(excel_file)
        # Check for the excel file
        if os.path.isfile(excel_file):
            log.logger.info('The excel file is created successfully.')
    
    def download_posters(urls, path=None):
        # Create the folder if it does not exist
        log.logger.info('\nDownloading posters...')
        if path == 1:
            file_path = os.path.join(main_dir, "(posters)")
        if path == 2:
            file_path = os.path.join(opened_dir, "(posters)")
        if os.path.isdir(file_path) == False:
            os.mkdir(file_path)
        n = 1
        for url in urls:
            filename = url.split('/')[-1]
            full_path = os.path.join(file_path, filename)
            # Skip the file if it is already downloaded
            if os.path.isfile(full_path):
                log.logger.debug('The file is already downloaded -> %s' %full_path)
                n +=1
            else:
                ## Check connection before starting
                if Run.check_conn() is True:
                    try:
                        response = urllib.request.urlopen(url)
                        ## Check response before downloading
                        if response.code == 200:
                            log.logger.info('Downloading Poster %i...' %n)
                            log.logger.debug('Poster(%i) url: %s' %(n, url))
                            urllib.request.urlretrieve(url, full_path)
                            n +=1
                        else:
                            log.logger.error('Downloading failed for Poster %i' %n)
                            log.logger.debug('Poster(%i) url: %s' %(n, url))
                            n +=1
                    # Avoid null urls
                    except ValueError:
                        log.logger.error('The URL is invalid, skipping it...')
                        n +=1
                        continue
                else:
                    log.logger.error('Internet connection is offline.')
                    showerror(title='Error!', message='Internet connection is offline.')
                    return
            
        log.logger.info('Downloading posters is finished.')
    
    def rename_files():
        log.logger.info('\nRenaming files...')
        # Open json file
        json_file = open(os.path.join(opened_dir, 'files.json'), 'r', encoding="utf-8")
        data = json.load(json_file)
        # Get file paths
        num = 0
        file_paths = []
        for loop in range(0, len(data['files'])):
            file_paths.append(data['files'][num]['File path'])
            num +=1
        # Get new file paths
        num = 0
        new_file_paths = []
        for loop in range(0, len(data['files'])):
            new_file_paths.append(data['files'][num]['New file path'])
            num +=1
        ## Rename the files
        num = 0
        for loop in range(0, len(file_paths)):
            source = file_paths[num]
            destination = new_file_paths[num]
            try:
                os.rename(source, destination)
            except Exception as err:
                log.logger.error('%s is not found' %source)
            num +=1
            log.logger.info("File(%i): %s is renamed to -> %s" % (num, source, destination))
        json_file.close()
        log.logger.info('Renaming files is finished.')
    
    def update_json_file():
        # Open json file
        n = 0
        json_file = open(os.path.join(opened_dir, 'files.json'), 'r', encoding="utf-8")
        data = json.load(json_file)
        for loop in range(0, len(data['files'])):
            folder_name = data['files'][n]['Original foldername']
            renamed_foldername, null = Run.clean_movie_name(folder_name)
            folder_parent = data['files'][n]['Folder parent']
            folder_path = data['files'][n]['Folder path']

            # Prepare new folder path
            if config['folders']['translate'] == 'False' and config['folders']['rename'] == 'True':
                new_folder_path = os.path.join(folder_parent, renamed_foldername)
            if config['folders']['translate'] == 'True' and config['folders']['rename'] == 'True':
                tr_foldername = Run.translate(renamed_foldername)
                if renamed_foldername.lower() == tr_foldername.lower():
                    translated_foldername = tr_foldername
                else:
                    translated_foldername = renamed_foldername+' - '+tr_foldername
                new_folder_path = os.path.join(folder_parent, translated_foldername)
            if config['folders']['translate'] == 'False' and config['folders']['rename'] == 'False':
                new_folder_path = folder_path

            # Prepare new file path
            renamed_filename = data['files'][n]['Renamed filename']
            file = data['files'][n]['File']
            extension = data['files'][n]['File extension']
            file_path = data['files'][n]['File path']

            if config['files']['translate'] == 'False' and config['files']['rename'] == 'True':
                new_file_path = os.path.join(new_folder_path, renamed_filename+extension)
            if config['files']['translate'] == 'True' and config['files']['rename'] == 'True':
                tr_filename = Run.translate(renamed_filename)
                if renamed_filename.lower() == tr_filename.lower():
                    translated_filename = tr_filename
                else:
                    translated_filename = renamed_filename+' - '+tr_filename
                new_file_path = os.path.join(new_folder_path, translated_filename+extension)
            if config['folders']['rename'] == 'False' and config['files']['rename'] == 'False':
                new_file_path = file_path
            # Fix issue that would happen after renaming folders
            if config['folders']['translate'] == 'False' and config['folders']['rename'] == 'True':
                file_path = os.path.join(new_folder_path, file)
            if config['folders']['translate'] == 'True' and config['folders']['rename'] == 'True':
                file_path = os.path.join(new_folder_path, file)

            # Add the new data to the dictionary
            data['files'][n].update({'New foldername': renamed_foldername, 'New folder path': new_folder_path, 'File path': file_path, 'New file path': new_file_path})

            # Save the data to json file
            with open(os.path.join(opened_dir, 'files.json'), 'w', encoding="utf-8") as json_file:
                json.dump(data, json_file, ensure_ascii=False, indent=4)
            n+=1
        json_file.close()
    
    def rename_folders():
        log.logger.info('\nRenaming folders...')
        # Get folder paths
        num = 0
        folder_paths = []
        json_file = open(os.path.join(opened_dir, 'files.json'), 'r', encoding="utf-8")
        data = json.load(json_file)
        for loop in range(0, len(data['files'])):
            folder_paths.append(data['files'][num]['Folder path'])
            num +=1
        # Get new folder paths
        num = 0
        new_folder_paths = []
        for loop in range(0, len(data['files'])):
            new_folder_paths.append(data['files'][num]['New folder path'])
            num +=1
        ## Rename the folders
        num = 0
        for loop in range(0, len(folder_paths)):
            source = folder_paths[num]
            destination = new_folder_paths[num]
            try:
                os.rename(source, destination)
            except Exception as err:
                log.logger.error('%s is not found' %source)
            num +=1
            log.logger.info("Folder(%i): %s is renamed to -> %s" % (num, source, destination))
        json_file.close()
        log.logger.info('Renaming folders is finished.')
    
    def no_rating():
        # Create a sub-folder to move the files to
        new_subfolder = os.path.join(opened_dir, "(no_rating)")
        if os.path.isdir(new_subfolder) == False:
            os.mkdir(new_subfolder)
        
        # Open json file
        json_file = open(os.path.join(opened_dir, 'files.json'), 'r', encoding="utf-8")
        data = json.load(json_file)

        # Get file paths
        num = 0
        file_paths = []
        for loop in range(0, len(data['files'])):
            for name in NotRated:
                if name in data['files'][num]['Renamed filename']:
                    file_paths.append(data['files'][num]['New file path'])
            num +=1
        
        # Move the files to a separate directory
        if NotRated != []:
            log.logger.info('\nMoving movies that have no rating to a separate folder...')
            for file in file_paths:
                if os.path.isfile(file):
                    # Get the name of the folder that contains the file
                    sub_folder = os.path.dirname(file)
                    # check if it is not in the main directory and it does not contain another file
                    if sub_folder != opened_dir and len(os.listdir(sub_folder)) == 1:
                        file = sub_folder
                    try:
                        shutil.move(file, new_subfolder)
                        log.logger.debug('The file/folder %s is moved to %s.' %(file, new_subfolder))
                    except Exception:
                        log.logger.debug('The file/folder already exists.')
                        continue
            log.logger.info('Moving files is finished.')

    def low_imdb_rating():
        # Create a sub-folder to move the files to
        new_subfolder = os.path.join(opened_dir, "(low_rating)")
        if os.path.isdir(new_subfolder) == False:
            os.mkdir(new_subfolder)
        
        # Open json file
        json_file = open(os.path.join(opened_dir, 'files.json'), 'r', encoding="utf-8")
        data = json.load(json_file)

        # Get file paths
        num = 0
        file_paths = []
        for loop in range(0, len(data['files'])):
            for name in low_imdb_rating:
                if name in data['files'][num]['Renamed filename']:
                    file_paths.append(data['files'][num]['New file path'])
            num +=1
        
        # Move the files to a separate directory
        if low_imdb_rating != []:
            log.logger.info('\nMoving movies that have low IMDB rating to a separate folder...')
            for file in file_paths:
                if os.path.isfile(file):
                    # Get the name of the folder that contains the file
                    sub_folder = os.path.dirname(file)
                    # check if it is not in the main directory and it does not contain another file
                    if sub_folder != opened_dir and len(os.listdir(sub_folder)) == 1:
                        file = sub_folder
                    try:
                        shutil.move(file, new_subfolder)
                        log.logger.debug('The file/folder %s is moved to %s.' %(file, new_subfolder))
                    except Exception:
                        log.logger.debug('The file/folder already exists.')
                        continue
            log.logger.info('Moving files is finished.')
    
    def adult_age_rating():
        # Create a sub-folder to move the files to
        new_subfolder = os.path.join(opened_dir, "(NSFW)")
        if os.path.isdir(new_subfolder) == False:
            os.mkdir(new_subfolder)
        
        # Open json file
        json_file = open(os.path.join(opened_dir, 'files.json'), 'r', encoding="utf-8")
        data = json.load(json_file)

        # Get file paths
        num = 0
        file_paths = []
        for loop in range(0, len(data['files'])):
            for name in NSFW:
                if name in data['files'][num]['Renamed filename']:
                    file_paths.append(data['files'][num]['New file path'])
            num +=1
        
        # Move the files to a separate directory
        if low_imdb_rating != []:
            log.logger.info('\nMoving movies that have high age rating to a separate folder...')
            for file in file_paths:
                if os.path.isfile(file):
                    # Get the name of the folder that contains the file
                    sub_folder = os.path.dirname(file)
                    # check if it is not in the main directory and it does not contain another file
                    if sub_folder != opened_dir and len(os.listdir(sub_folder)) == 1:
                        file = sub_folder
                    try:
                        shutil.move(file, new_subfolder)
                        log.logger.debug('The file/folder %s is moved to %s.' %(file, new_subfolder))
                    except Exception:
                        log.logger.debug('The file/folder already exists.')
                        continue
            log.logger.info('Moving files is finished.')
    
    def restore_files():
        log.logger.info('\nRestoring original filenames...')
        # Open json file
        json_file = open(os.path.join(opened_dir, 'files.json'), 'r', encoding="utf-8")
        data = json.load(json_file)
        # Get new file paths
        num = 0
        new_file_paths = []
        for loop in range(0, len(data['files'])):
            new_file_paths.append(data['files'][num]['New file path'])
            num +=1
        # Get file paths
        num = 0
        file_paths = []
        for loop in range(0, len(data['files'])):
            file_paths.append(data['files'][num]['File path'])
            num +=1
        ## Rename the files to their previous names
        num = 0
        for loop in range(0, len(file_paths)):
            source = new_file_paths[num]
            destination = file_paths[num]
            try:
                os.rename(source, destination)
            except Exception as err:
                log.logger.error('%s is not found' %source)
            num +=1
            log.logger.info("File(%i): %s is renamed to -> %s" % (num, source, destination))
        json_file.close()
        log.logger.info('Restoring original filenames is finished.')
    
    def restore_folders():
        log.logger.info('\nRestoring original folder names...')
        # Open json file
        json_file = open(os.path.join(opened_dir, 'files.json'), 'r', encoding="utf-8")
        data = json.load(json_file)
        # Get new folder paths
        num = 0
        new_folder_paths = []
        for loop in range(0, len(data['files'])):
            new_folder_paths.append(data['files'][num]['New folder path'])
            num +=1
        # Get folder paths
        num = 0
        folder_paths = []
        for loop in range(0, len(data['files'])):
            folder_paths.append(data['files'][num]['Folder path'])
            num +=1
        ## Rename the folders to their original names
        num = 0
        for loop in range(0, len(folder_paths)):
            source = new_folder_paths[num]
            destination = folder_paths[num]
            try:
                os.rename(source, destination)
            except Exception as err:
                log.logger.error('%s is not found' %source)
            num +=1
            log.logger.info("Folder(%i): %s is renamed to -> %s" % (num, source, destination))
        json_file.close()
        log.logger.info('Restoring original folder names is finished.')

    def move():
        # Move files and folders to their original location
        with open(os.path.join(main_dir, 'last_location'), 'r') as text_file:
            last_location = text_file.read()
        
        no_rating = os.path.join(last_location, '(no_rating)')
        if os.path.isdir(no_rating):
            log.logger.info('Moving movies with no rating to their previous location...')
            no_rating_list = os.listdir(no_rating)
            no_rating_new_list = [os.path.join(no_rating, item) for item in no_rating_list]
            for item in no_rating_new_list:
                if os.path.isfile(item) or os.path.isdir(item):
                    shutil.move(item, last_location)

        low_rating = os.path.join(last_location, '(low_rating)')
        if os.path.isdir(low_rating):
            log.logger.info('Moving movies with low rating to their previous location...')
            low_rating_list = os.listdir(low_rating)
            low_rating_new_list = [os.path.join(low_rating, item) for item in low_rating_list]
            for item in low_rating_new_list:
                if os.path.isfile(item) or os.path.isdir(item):
                    shutil.move(item, last_location)

        nsfw = os.path.join(last_location, '(NSFW)')
        if os.path.isdir(nsfw):
            log.logger.info('Moving movies with high-age rating to their previous location...')
            nsfw_list = os.listdir(nsfw)
            nsfw_new_list = [os.path.join(nsfw, item) for item in nsfw_list]
            for item in nsfw_new_list:
                if os.path.isfile(item) or os.path.isdir(item):
                    shutil.move(item, last_location)
        
        log.logger.info('Moving files and folders to their original location is finished.')
    
    def run():
        # load data of the files from json
        movie_names, years = Run.get_from_json()

        # Fetch data from OMDB
        Run.fetch_data(movie_names, years)

        # Download posters
        if config['omdb']['posters'] == 'True':
            Run.download_posters(Poster, path=2)
        
        # Rename the folders
        if config['folders']['translate'] == 'False' and config['folders']['rename'] == 'True':
            Run.rename_folders()
        if config['folders']['translate'] == 'True' and config['folders']['rename'] == 'True':
            Run.rename_folders()
        
        # Rename the files
        if config['files']['translate'] == 'False' and config['files']['rename'] == 'True':
            Run.rename_files()
        if config['files']['translate'] == 'True' and config['files']['rename'] == 'True':
            Run.rename_files()
        
        # Move movies with low imdb-rating
        if config['files']['no_rating'] == 'True':
            Run.no_rating()
        
        # Move movies with low imdb-rating
        if config['files']['low_imdb_rating'] == 'True':
            Run.low_imdb_rating()
        
        # Move movies with high age-rating
        if config['files']['adult_age_rating'] == 'True':
            Run.adult_age_rating()