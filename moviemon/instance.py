import omdb
from django.conf import settings
import pickle
import os
import random


class Moviemon:
    def __init__(self):
        self.save_dir = 'saved_files/'
        self.movies_detail = []
        self.position = None
        self.grid_size = None
        self.movieballs = 3
        self.found = 0
        self.found_moviemon = ''
        self.moviedex = []

    def load(self, file_name):
        path_to_file = self.save_dir + file_name
        return pickle.load(open(path_to_file, 'rb'))

    def load_settings(self):
        key = "9fcf16b8"
        moviews = settings.MOVIEMON[0]['IMDB_title']
        self.position = settings.MOVIEMON[0]['position']
        self.grid_size = settings.MOVIEMON[0]['grid_size']
        omdb.set_default('apikey', key)
        for index in moviews:
            if res := omdb.get(title=moviews[index]):
                self.movies_detail.append(res)

    def get_strength(self):
        return len(self.moviedex)

    def get_movie(self, mov_id):
        for moviemon in self.movies_detail:
            if moviemon['imdb_id'] == mov_id:
                return {
                    'id': moviemon['imdb_id'],
                    'title': moviemon['title'],
                    'poster': moviemon['poster'],
                    'director': moviemon['director'],
                    'year': moviemon['year'],
                    'rating': moviemon['imdb_rating'],
                    'plot': moviemon['plot'],
                    'actors': moviemon['actors'],
                }
        return ''

    def save(self, file_name):
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)
        file = self.save_dir + file_name
        os.system("touch " + file)
        pickle.dump(self, open(file, 'wb'))

    def save_tmp(self):
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)
        pickle.dump(self, open(self.save_dir + "session.txt", 'wb'))

    def dump(self):
        return pickle.load(open(self.save_dir + 'session.txt', 'rb'))

    @staticmethod
    def get_random_movie(movies):
        if len(movies) > 1:
            number = random.randint(0, len(movies) - 1)
        else:
            number = 0
        return movies[number]
