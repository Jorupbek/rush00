# OMDB API KEY : http://www.omdbapi.com/?i=tt3896198&apikey=87ac0cb0

import sys
import requests
import omdb
from django.conf import settings
import pickle
import os
import random


class Moviemon:

    def __init__(self):
        "Ok on a initialise la classe moviemon"

    def load(self, fileName):
        nomdossiersauvegarde = "saved_game/"
        nomfichier = fileName
        nomSauvegarde = nomdossiersauvegarde + nomfichier
        self = pickle.load(open(nomSauvegarde, 'rb'))
        return self

    def get_random_movie(self, moviemonListAvecDetailClean):
        print('HELLO', moviemonListAvecDetailClean)
        if len(moviemonListAvecDetailClean) > 1:
            randomNumber = random.randint(0,
                                          len(moviemonListAvecDetailClean) - 1)
        else:
            randomNumber = 0
        return moviemonListAvecDetailClean[randomNumber]

    def load_default_settings(self):
        API_KEY = "87ac0cb0"
        moviemonList = settings.MOVIEMON_SETTINGS[0]['IMDB_title']
        try:
            self.position = settings.MOVIEMON_SETTINGS[0]['position_start']
            self.grid_size = settings.MOVIEMON_SETTINGS[0]['grid_size']
            omdb.set_default('apikey', API_KEY)
            self.moviemonListAvecDetail = []
            for index in moviemonList:
                res = omdb.get(title=moviemonList[index])
                if (res):
                    self.moviemonListAvecDetail.append(res)
            self.nombreMovieballs = 3
            self.found = 0
            self.found_moviemon = ''
            self.moviedex = []

        except Exception as e:
            print(e)
        return self

    def get_strength(self):
        return len(self.moviedex)

    def get_movie(self, moviemonId):
        for moviemon in self.moviemonListAvecDetail:
            if (moviemon['imdb_id'] == moviemonId):
                moviemonDetail = {
                    'id': moviemon['imdb_id'],
                    'nom': moviemon['title'],
                    'poster': moviemon['poster'],
                    'realisateur': moviemon['director'],
                    'annee': moviemon['year'],
                    'rating': moviemon['imdb_rating'],
                    'synopsis': moviemon['plot'],
                    'acteurs': moviemon['actors'],
                }
                return moviemonDetail
        return ""

    def save(self, fileName):
        nomdossiersauvegarde = "saved_game/"
        if not os.path.exists(nomdossiersauvegarde):
            os.makedirs(nomdossiersauvegarde)
        nomfichier = fileName
        nomSauvegarde = nomdossiersauvegarde + nomfichier
        os.system("touch " + nomSauvegarde)
        pickle.dump(self, open(nomSauvegarde, 'wb'))
        return self

    def saveTMP(self):
        nomdossiersauvegarde = "saved_game/"
        if not os.path.exists(nomdossiersauvegarde):
            os.makedirs(nomdossiersauvegarde)
        pickle.dump(self, open(nomdossiersauvegarde + "mypicklefile.txt", 'wb'))
        return self

    def dump(self):
        nomdossiersauvegarde = "saved_game/"
        moviemongame = pickle.load(
            open(nomdossiersauvegarde + 'mypicklefile.txt', 'rb'))
        return moviemongame
