# IMDB-Get
IMDB-Get is a cross-platform desktop application that can be used to get information about movies from IMDB website using the OMDb API.

![main_window](https://user-images.githubusercontent.com/29783425/214784391-f5933d90-f7b8-4494-b352-79d6cbea3fd1.png)

## Features
1- Search a movie by the name and production year.

2- Search a list of movies, and view the result inside the application.

3- Search a local folder, list all the movies inside that folder, and view the result inside the application.

4- Organize local multimedia files based on IMDB rating, and age rating.

5- Save the data of the movies, so you can view them later without internet connection.

6- Translate the local multimedia files and the folders contains these files.

7- Restore any changes done by the application in case of errors.

## How to install
The application comes with an installer that can be used to install the application, follow these instruction to install the application:

1- Install Python and Tkinter.

2- Open `installer.py`, and click Install.

The installer will download the required python modules, and copy the files of the application to the installation folder, then create start menu and desktop shortcuts.

## How to use

### Search a movie
Write the name of the movie and press search or enter from the keyboard.

You can enter the year of the movie for precious result.

Tick `clear previous search` to delete downloaded data about the same name you searched before, and download new data.

![movie_viewer](https://user-images.githubusercontent.com/29783425/214784470-183794ab-02ce-45a6-a85b-629362b8d574.png)

### Import a list
1- Create a text file, and write all the names of the movies you want to search.

2- Click `import a list` and locate the text file.

You can add the production year of the movies to the name of the movies, and the application will use it for better results.

3- The application will start downloading info of the movies inside the text file.

The application stores these data to an excel file inside the folder of the application, and views them using `Excel Viewer`.

![import_a_list](https://user-images.githubusercontent.com/29783425/214784727-f2b41f4a-72d4-420d-8f0f-9c1acfe2bede.png)

### Open a folder
If you have a local folder contains multimedia files, the application offer many features that can help you organize these multimedia files.

1- Click `open a folder` and locate the folder contains all the movies in your machine.

2- The application will list all the multimedia files found in the main folder and all sub-folders under that folder.

3- The application will try to filter the filenames to extract the correct the name of the movies.

4- If there is any unwanted extra additions to the movie names, you can either add these extra additions to the blocklist and try again, or you can click the movie name, and press `edit selection`, and change the movie name. Furthermore, you can press `view original names` to view the filenames of the listed files.

![movie_names](https://user-images.githubusercontent.com/29783425/214784872-e3dd11a1-8b36-4537-b3a7-e33ffb23526b.png)

5- Press `start`, and the application will start downloading the data of the movies.

6- The application will create an excel contains all the downloaded data, and view them inside the application.

![excel_viewer](https://user-images.githubusercontent.com/29783425/214784966-eeb63b6f-2fa9-4053-b68a-311e5c0e4268.png)

You can go to `options`, and you will find a lot of options that can help you organize the files and folders opened using IMDB-Get.

### Excel viewer
After you import a list, or open a folder, the downloaded data are stored in an excel file inside the opened folder, or the application folder. You can view these excel file using `Excel viewer` without having to install any external applications.

Excel viewer opens that last created excel file automatically, but you can view any excel file created using IMDB-Get.

### Edit blocklist
Here you can add all the unwanted additions that you want to remove from the filenames of the multimedia files opened using IMDB-Get.

### Undo last operation
The application stores information about opened files and folders, and store these data in a file inside the folder you opened, the name of the file is `files.json`.
After pressing `undo last operation`, it will undo the last changes done to the last opened folder, but keep in mind that the files and folder you modify afterwards will not be restored.

### Options

![options](https://user-images.githubusercontent.com/29783425/214785092-a27a1162-da26-41fa-8be9-f53f14d7a164.png)

#### API key
The application uses OMDB API to get the information of the movies, but OMDB requires an API key, which you can easily get by following this link -> [https://www.omdbapi.com/apikey.aspx](https://www.omdbapi.com/apikey.aspx)

The application has its own API key, but each API key has limited requests by day, *so it is better to use your own API key*.

#### Movie description
Here you can choose how much info you want to download about the plot of the movies, it is either short or long. (Long is the default option)

#### Download poster
If you turn off this option, the application will not download any posters about the movies, and `Excel viewer` will not show any posters.

#### Move movies with no rating
After turning on this option, the application create a sub-folder under the main folder with the name `(no_rating)`, and move the movies with no rating to this folder.

#### Move movies with low IMDB rating
After turning on this option, the application create a sub-folder under the main folder with the name `(low_rating)`, and move the movies with low rating to this folder.

#### Move movies with high age rating
After turning on this option, the application create a sub-folder under the main folder with the name `(NSFW)`, and move the movies with hig age rating to this folder including `rated R`, these kind of rating could either include explicit sexual contents or violence.

#### Rename files
The application automatically clean filenames to extract the name of the movies from these files, so if you want to rename the filenames with the name of the movies, the application can help you with that, and you can restore original filenames later if you want.

#### Translate filenames
You can translate the name of the files if you want, and you can choose `source language` and `target language` from translate options, but you need to enable `rename files` first.

#### Rename folders
After turning on this option, the application will clean the names of the folders, and apply these changes to the folder names.

#### Translate folder names
You can translate the name of the folders if you want, and you can choose `source language` and `target language` from translate options, but you need to enable `rename folders` first.

### Special thanks to:
[https://icons8.com/icons](https://icons8.com/icons)
for the amazing icons that I used with the buttons of the application and the logo.
