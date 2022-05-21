from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import TemplateView

from moviemon.instance import Moviemon
import os
import random


class HomePageView(TemplateView):
    template_name = "home.html"

    def __init__(self):
        movmn = Moviemon()
        movmn.load_settings()
        movmn.save_tmp()

    def get_context_data(self, **kwargs):
        context = super(HomePageView, self).get_context_data()
        context['a_href'] = '/worldmap'
        context['b_href'] = '/options/load_game'
        context['a_title'] = 'New game'
        context['b_title'] = 'Load existing game'

        return context


def make_grid(width, height, position):
    grid = []
    for y in range(0, height):
        new = []
        for x in range(0, width):
            if (x == position['x']) and (y == position['y']):
                new.append('O')
            else:
                new.append('X')
        grid.append(new)
    return grid


def do_move(movmn, move):
    width = movmn.grid_size['width']
    height = movmn.grid_size['height']
    position = movmn.position

    if move == 'left':
        if position['x'] > 0:
            movmn.position['x'] -= 1
            return True
    elif move == 'right':
        if position['x'] < width - 1:
            movmn.position['x'] += 1
            return True
    elif move == 'up':
        if position['y'] > 0:
            movmn.position['y'] -= 1
            return True
    elif move == 'down':
        if position['y'] < height - 1:
            movmn.position['y'] += 1
            return True

    return False


def random_move_event(movmn):
    from random import randint
    rand = randint(0, 2)
    found_moviemon = ''
    if rand == 1:
        movmn.movieballs += 1
    elif rand == 2:
        if len(movmn.movies_detail) > 0:
            m = movmn.get_random_movie(movmn.movies_detail)
            found_moviemon = m['imdb_id']
        else:
            rand = 0
    return rand, found_moviemon


class Worldmap(View):
    pass


def worldmap(request):
    move = request.GET.get('move', '')
    old_id = request.GET.get('id', '')
    movmn = Moviemon()
    movmn = movmn.dump()
    if do_move(movmn, move):
        movmn.found, movmn.found_moviemon = random_move_event(movmn)
        movmn.save_tmp()
        return redirect("/worldmap")

    width = movmn.grid_size['width']
    height = movmn.grid_size['height']
    position = movmn.position

    controls_params = {
        'left_href': '/worldmap?move=left', 'left_title': 'Move left',
        'up_href': '/worldmap?move=up', 'up_title': 'Move up',
        'down_href': '/worldmap?move=down', 'down_title': 'Move down',
        'right_href': '/worldmap?move=right', 'right_title': 'Move right',

        'select_href': '/moviedex', 'start_href': '/options',
        'select_title': 'Moviedex', 'start_title': 'Options',
        'a_href': '', 'b_href': '/worldmap',
        'a_title': '', 'b_title': '',
    }

    if movmn.found == 2:
        if not old_id:
            controls_params['a_href'] = "/battle/" + movmn.found_moviemon
            controls_params['a_title'] = "Battle!"

    context = {
        **controls_params,
        'grid': make_grid(width, height, position),
        'found': movmn.found,
        'found_moviemon': movmn.found_moviemon,
        'numballs': movmn.movieballs
    }

    return render(request, "worldmap.html", context)


def battle(request, id):
    movmn = Moviemon()
    game = movmn.dump()
    moviemonABattre = game.get_movie(id)
    moviemonballTry = request.GET.get('movieball')
    message = ""
    chance = 0
    try:
        forceJoueur = game.get_strength()
        forceMonstre = float(moviemonABattre['rating']) * 10
        chance = 50 - int(forceMonstre) + forceJoueur * 5
        if chance < 1:
            chance = 1
        if chance > 90:
            chance = 90
    except Exception as e:
        print(e)
    if (moviemonballTry):
        if (game.movieballs > 0 and moviemonABattre):
            game.movieballs = game.movieballs - 1
            rat = moviemonABattre['rating']
            forceMonstre = float(rat) if rat != 'N/A' else 1 * 10
            chance = 50 - int(forceMonstre) + forceJoueur * 5
            randomNumber = random.randint(1, 100)
            moviemonListAvecDetailClean = []
            if (chance >= randomNumber or moviemonballTry == 'cheat'):
                game.moviedex.append(moviemonABattre)
                for moviemon in game.movies_detail:
                    if (moviemon['title'] != moviemonABattre['title']):
                        moviemonListAvecDetailClean.append(moviemon)
                game.movies_detail = moviemonListAvecDetailClean
                game.save_tmp()
                message = "Tu as attrapé un moviemon !"
                moviemonballTry = False
            else:
                if (game.movieballs > 0):
                    message = "Retente ta chance !"
                else:
                    message = "Tu n'as plus de movieballs"
            game.save_tmp()
        else:
            message = "Tu n'as plus de movieballs"

    params = {
        'left_href': '', 'up_href': '', 'down_href': '', 'right_href': '',
        'left_title': '', 'up_title': '', 'down_title': '', 'right_title': '',
        'select_href': '', 'start_href': '',
        'select_title': '', 'start_title': '',
        'a_href': '/battle/' + id + '?movieball=true',
        'b_href': '/worldmap?id=' + id,
        'a_title': '', 'b_title': 'Retour au World Map',
        "message": message, "forceJoueur": forceJoueur,
        "movieballs": game.movieballs,
        "moviemonABattre": moviemonABattre, "id": id, "chance": chance
    }

    return render(request, "battle.html", params)


def do_move_moviedex(movmn, move, selected):
    did_move = False
    count = 0
    dict_selected = {'selected': '', 'left': '', 'right': '', 'up': '',
                     'down': ''}
    if move == 'left':
        did_move = True
    if move == 'right':
        did_move = True
    if move == 'up':
        did_move = True
    if move == 'down':
        did_move = True
    if did_move:
        for movie in movmn.moviedex:
            count += 1
        if count >= 0:
            if selected in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
                dict_selected['selected'] = selected
        if dict_selected['selected'] in ['0', '1', '2', '3', '4', '5', '6', '7',
                                         '8', '9']:
            if selected in ['5', '6', '7', '8', '9'] and move == 'up':
                if count > (int(selected) - 5):
                    dict_selected['up'] = str(int(selected) - 5)
            elif selected in ['0', '1', '2', '3', '4'] and move == 'down':
                if count > (int(selected) + 5):
                    dict_selected['down'] = str(int(selected) + 5)
            elif selected in ['1', '2', '3', '4', '6', '7', '8',
                              '9'] and move == 'left':
                if count > (int(selected) - 1):
                    dict_selected['left'] = str(int(selected) - 1)
            elif selected in ['0', '1', '2', '3', '5', '6', '7',
                              '8'] and move == 'right':
                if count > (int(selected) + 1):
                    dict_selected['right'] = str(int(selected) + 1)
            if not dict_selected['up']:
                dict_selected['up'] = selected
            if not dict_selected['down']:
                dict_selected['down'] = selected
            if not dict_selected['left']:
                dict_selected['left'] = selected
            if not dict_selected['right']:
                dict_selected['right'] = selected
    return dict_selected


def moviedex(request):
    selected = request.GET.get('selected', '')
    move = request.GET.get('move', '')
    movmn = Moviemon()
    movmn = movmn.dump()
    moviedex = movmn.moviedex
    count = 0
    if not selected:
        selected = '0'
    dict_selected = do_move_moviedex(movmn, move, selected)
    if dict_selected:
        movmn.save_tmp()
    for moviemon in moviedex:
        moviemon['id'] = str(count)
        count += 1
    a_href = dict_selected['selected']
    if a_href not in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
        a_href = '0'
    controls_params = {
        'left_href': '/moviedex?move=left&selected=' + dict_selected['left'],
        'up_href': '/moviedex?move=up&selected=' + dict_selected['up'],
        'down_href': '/moviedex?move=down&selected=' + dict_selected['down'],
        'right_href': '/moviedex?move=right&selected=' + dict_selected['right'],
        'left_title': 'Move left', 'up_title': 'Move up',
        'down_title': 'Move down', 'right_title': 'Move right',
        'select_href': '/worldmap', 'start_href': '',
        'select_title': 'World Map', 'start_title': '',
        'a_href': '/moviedex/' + a_href, 'b_href': '',
        'a_title': 'Moviemon Details', 'b_title': '',
        'moviedex': moviedex, 'selected': selected
    }

    return render(request, "moviedex.html", controls_params)


def moviedexDetail(request, id):
    movmn = Moviemon()
    game = movmn.dump()
    moviedex = game.moviedex
    controls_params = {
        'left_href': '', 'up_href': '', 'down_href': '', 'right_href': '',
        'left_title': '', 'up_title': '', 'down_title': '', 'right_title': '',
        'select_href': '', 'start_href': '',
        'select_title': '', 'start_title': '',
        'a_href': '', 'b_href': '/moviedex',
        'a_title': '', 'b_title': 'Moviedex',
        "moviemonDetail": moviedex[int(id)]
    }
    return render(request, "moviedex_detail.html", controls_params)


def options(request):
    movmn = Moviemon()
    movmn.load_settings()
    movmn.save_tmp()
    controls_params = {
        'left_href': '', 'up_href': '', 'down_href': '', 'right_href': '',
        'left_title': '', 'up_title': '', 'down_title': '', 'right_title': '',
        'select_href': '', 'start_href': '/worldmap',
        'select_title': '', 'start_title': 'Back to World Map',
        'a_href': '/options/save_game', 'b_href': '/',
        'a_title': 'Save', 'b_title': 'Quit',
    }
    return render(request, "options.html", controls_params)


def options_load_game(request):
    movmn = Moviemon()
    listeFichiers = os.listdir("saved_files/")
    listeGame = []
    for fichiers in listeFichiers:
        if (fichiers != "session.txt"):
            listeGame.append(fichiers)
    selectionne = request.GET.get('selectionne')
    if (selectionne != None):
        for fichier in listeGame:
            if selectionne in fichier:
                game = movmn.load(fichier)
                game.save_tmp()
            # return(redirect("/worldmap"))
    slota = False
    slotb = False
    slotc = False
    gameSplitA = 0
    gameSplitB = 0
    gameSplitC = 0
    for game in listeGame:
        if ("slota" in game):
            slota = True
            gameSplit = game.split("_")
            gameSplitA = gameSplit[1]
        if ("slotb" in game):
            slotb = True
            gameSplit = game.split("_")
            gameSplitB = gameSplit[1]
        if ("slotc" in game):
            slotc = True
            gameSplit = game.split("_")
            gameSplitC = gameSplit[1]
    return render(request, "options_load_game.html",
                  {"slota": slota, "slotb": slotb, "slotc": slotc,
                   "slotaNiveau": gameSplitA, "slotbNiveau": gameSplitB,
                   "slotcNiveau": gameSplitC, "b_href": "/", "b_title": "menu",
                   "a_href": "/worldmap/", "a_title": "load"})


def options_save_game(request):
    movmn = Moviemon()
    tmp = movmn.dump()
    listeFichiers = os.listdir("saved_files/")
    listeGame = []
    for fichiers in listeFichiers:
        if (fichiers != "session.txt"):
            listeGame.append(fichiers)
    slota = False
    slotb = False
    slotc = False
    gameSplitA = 0
    gameSplitB = 0
    gameSplitC = 0
    for game in listeGame:
        if ("slota" in game):
            slota = True
            gameSplit = game.split("_")
            gameSplitA = gameSplit[1]
        if ("slotb" in game):
            slotb = True
            gameSplit = game.split("_")
            gameSplitB = gameSplit[1]
        if ("slotc" in game):
            slotc = True
            gameSplit = game.split("_")
            gameSplitC = gameSplit[1]
    nomSlot = request.GET.get('slot')
    NiveauMax = 10
    NiveauActuel = len(tmp.moviedex)
    if (nomSlot):
        saveName = "slot" + nomSlot.lower() + "_" + str(
            NiveauActuel) + "_10.mmg"
        if ("slota" in saveName):
            commandeEffacer = os.system("rm -f saved_files/slota*")
            tmp.save(fileName=saveName)
        if ("slotb" in saveName):
            commandeEffacer = os.system("rm -f saved_files/slotb*")
            tmp.save(fileName=saveName)
        if ("slotc" in saveName):
            commandeEffacer = os.system("rm -f saved_files/slotc*")
            tmp.save(fileName=saveName)
    tmp.dump()
    return render(request, "options_save_game.html",
                  {"slota": slota, "slotb": slotb, "slotc": slotc,
                   "slotaNiveau": gameSplitA, "slotbNiveau": gameSplitB,
                   "slotcNiveau": gameSplitC, "b_href": "/options/",
                   "b_title": "retour"})
