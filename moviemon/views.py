from django.shortcuts import render, redirect
from django.http import HttpResponse
from moviemon.getinfo import Moviemon
import os
import random

# Create your views here.

empty_controls_params = {
    'left_href': '', 'up_href': '', 'down_href': '', 'right_href': '',
    'left_title': '', 'up_title': '', 'down_title': '', 'right_title': '',
    'select_href': '', 'start_href': '',
    'select_title': '', 'start_title': '',
    'a_href': '', 'b_href': '',
    'a_title': '', 'b_title': '',
}


def accueil(request):
    settings = Moviemon()
    settings.load_default_settings()
    settings.saveTMP()
    controls_params = {
        'left_href': '', 'up_href': '', 'down_href': '', 'right_href': '',
        'left_title': '', 'up_title': '', 'down_title': '', 'right_title': '',
        'select_href': '', 'start_href': '',
        'select_title': '', 'start_title': '',
        'a_href': '/worldmap', 'b_href': '/options/load_game',
        'a_title': 'New game', 'b_title': 'Load existing game',
    }
    return render(request, "ex00/accueil.html", controls_params)


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


def displayObject(o):
    # print(str(o.__class__) + ": " + str(o.__dict__))
    print(o.position)


def do_move(settings, move):
    did_move = False
    width = settings.grid_size['width']
    height = settings.grid_size['height']
    position = settings.position
    if (move == 'left'):
        if position['x'] > 0:
            settings.position['x'] = position['x'] - 1
            did_move = True
    if (move == 'right'):
        if position['x'] < width - 1:
            settings.position['x'] = position['x'] + 1
            did_move = True
    if (move == 'up'):
        if position['y'] > 0:
            settings.position['y'] = position['y'] - 1
            did_move = True
    if (move == 'down'):
        if position['y'] < height - 1:
            settings.position['y'] = position['y'] + 1
            did_move = True
    return did_move


def random_move_event(settings):
    from random import randint
    rand = randint(0, 2)
    found_Moviemon = ''
    if rand == 1:
        settings.nombreMovieballs += 1
    elif rand == 2:
        if len(settings.MoviemonListAvecDetail) > 0:
            m = settings.get_random_movie(settings.MoviemonListAvecDetail)
            found_Moviemon = m['imdb_id']
        else:
            rand = 0
    return rand, found_Moviemon


def worldmap(request):
    move = request.GET.get('move', '')
    old_id = request.GET.get('id', '')
    settings = Moviemon()
    settings = settings.dump()
    if do_move(settings, move):
        from random import randint
        settings.found, settings.found_Moviemon = random_move_event(settings)
        print("found2!", settings.found_Moviemon)
        settings.saveTMP()
        return (redirect("/worldmap"))
    width = settings.grid_size['width']
    height = settings.grid_size['height']
    position = settings.position
    controls_params = {
        'left_href': '/worldmap?move=left', 'up_href': '/worldmap?move=up',
        'down_href': '/worldmap?move=down',
        'right_href': '/worldmap?move=right',
        'left_title': 'Move left', 'up_title': 'Move up',
        'down_title': 'Move down', 'right_title': 'Move right',
        'select_href': '/moviedex', 'start_href': '/options',
        'select_title': 'Moviedex', 'start_title': 'Options',
        'a_href': '', 'b_href': '/worldmap',
        'a_title': '', 'b_title': '',
    }
    if settings.found == 2:
        if not old_id:
            controls_params['a_href'] = "/battle/" + settings.found_Moviemon
            controls_params['a_title'] == "Battle!"
    other_params = {'grid': make_grid(width, height, position),
                    'found': settings.found,
                    'found_Moviemon': settings.found_Moviemon,
                    'numballs': settings.nombreMovieballs}
    all_params = {**controls_params, **other_params}
    return render(request, "ex00/worldmap.html", all_params)


def battle(request, id):
    settings = Moviemon()
    game = settings.dump()
    game.nombreMovieballs
    MoviemonABattre = game.get_movie(id)
    MoviemonballTry = request.GET.get('movieball')
    message = ""
    chance = 0
    try:
        forceJoueur = game.get_strength()
        forceMonstre = float(MoviemonABattre['rating']) * 10
        chance = 50 - int(forceMonstre) + forceJoueur * 5
        if chance < 1:
            chance = 1
        if chance > 90:
            chance = 90
    except Exception as e:
        print(e)
    if (MoviemonballTry):
        if (game.nombreMovieballs > 0 and MoviemonABattre):
            game.nombreMovieballs = game.nombreMovieballs - 1
            forceMonstre = float(MoviemonABattre['rating']) * 10
            chance = 50 - int(forceMonstre) + forceJoueur * 5
            randomNumber = random.randint(1, 100)
            MoviemonListAvecDetailClean = []
            if (chance >= randomNumber or MoviemonballTry == 'cheat'):
                game.moviedex.append(MoviemonABattre)
                for Moviemon in game.MoviemonListAvecDetail:
                    if (Moviemon['title'] != MoviemonABattre['nom']):
                        MoviemonListAvecDetailClean.append(Moviemon)
                game.MoviemonListAvecDetail = MoviemonListAvecDetailClean
                game.saveTMP()
                message = "Tu as attrapé un Moviemon !"
                MoviemonballTry = False
            else:
                if (game.nombreMovieballs > 0):
                    message = "Retente ta chance !"
                else:
                    message = "Tu n'as plus de movieballs"
            game.saveTMP()
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
        "nombreMovieballs": game.nombreMovieballs,
        "MoviemonABattre": MoviemonABattre, "id": id, "chance": chance
    }
    return render(request, "ex00/battle.html", params)


def do_move_moviedex(settings, move, selected):
    did_move = False
    count = 0
    dict_selected = {'selected': '', 'left': '', 'right': '', 'up': '',
                     'down': ''}
    if (move == 'left'):
        did_move = True
    if (move == 'right'):
        did_move = True
    if (move == 'up'):
        did_move = True
    if (move == 'down'):
        did_move = True
    if did_move:
        for movie in settings.moviedex:
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
    settings = Moviemon()
    settings = settings.dump()
    moviedex = settings.moviedex
    count = 0
    if not selected:
        selected = '0'
    dict_selected = do_move_moviedex(settings, move, selected)
    if dict_selected:
        settings.saveTMP()
    for Moviemon in moviedex:
        Moviemon['id'] = str(count)
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
    return render(request, "ex00/moviedex.html", controls_params)


def moviedexDetail(request, id):
    settings = Moviemon()
    game = settings.dump()
    moviedex = game.moviedex
    controls_params = {
        'left_href': '', 'up_href': '', 'down_href': '', 'right_href': '',
        'left_title': '', 'up_title': '', 'down_title': '', 'right_title': '',
        'select_href': '', 'start_href': '',
        'select_title': '', 'start_title': '',
        'a_href': '', 'b_href': '/moviedex',
        'a_title': '', 'b_title': 'Moviedex',
        "MoviemonDetail": moviedex[int(id)]
    }
    return render(request, "ex00/moviedex_detail.html", controls_params)


def options(request):
    settings = Moviemon()
    settings.load_default_settings()
    settings.saveTMP()
    controls_params = {
        'left_href': '', 'up_href': '', 'down_href': '', 'right_href': '',
        'left_title': '', 'up_title': '', 'down_title': '', 'right_title': '',
        'select_href': '', 'start_href': '/worldmap',
        'select_title': '', 'start_title': 'Back to World Map',
        'a_href': '/options/save_game', 'b_href': '/',
        'a_title': 'Save', 'b_title': 'Quit',
    }
    return render(request, "ex00/options.html", controls_params)


def options_load_game(request):
    settings = Moviemon()
    listeFichiers = os.listdir("saved_game/")
    listeGame = []
    for fichiers in listeFichiers:
        if (fichiers != "mypicklefile.txt"):
            listeGame.append(fichiers)
    selectionne = request.GET.get('selectionne')
    if (selectionne != None):
        for fichier in listeGame:
            if selectionne in fichier:
                game = settings.load(fichier)
                game.saveTMP()
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
    return render(request, "ex00/options_load_game.html",
                  {"slota": slota, "slotb": slotb, "slotc": slotc,
                   "slotaNiveau": gameSplitA, "slotbNiveau": gameSplitB,
                   "slotcNiveau": gameSplitC, "b_href": "/", "b_title": "menu",
                   "a_href": "/worldmap/", "a_title": "load"})


def options_save_game(request):
    settings = Moviemon()
    tmp = settings.dump()
    listeFichiers = os.listdir("saved_game/")
    listeGame = []
    for fichiers in listeFichiers:
        if (fichiers != "mypicklefile.txt"):
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
            commandeEffacer = os.system("rm -f saved_game/slota*")
            tmp.save(fileName=saveName)
        if ("slotb" in saveName):
            commandeEffacer = os.system("rm -f saved_game/slotb*")
            tmp.save(fileName=saveName)
        if ("slotc" in saveName):
            commandeEffacer = os.system("rm -f saved_game/slotc*")
            tmp.save(fileName=saveName)
    tmp.dump()
    return render(request, "ex00/options_save_game.html",
                  {"slota": slota, "slotb": slotb, "slotc": slotc,
                   "slotaNiveau": gameSplitA, "slotbNiveau": gameSplitB,
                   "slotcNiveau": gameSplitC, "b_href": "/options/",
                   "b_title": "retour"})


def handler404(request):
    return render(request, '404.html', status=404)
