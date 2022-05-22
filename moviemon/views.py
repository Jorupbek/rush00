from django.shortcuts import render, redirect
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
    found_moviemon = name_rating = ''
    if rand == 1:
        movmn.movieballs += 1
    elif rand == 2:
        if len(movmn.movies_detail) > 0:
            m = movmn.get_random_movie(movmn.movies_detail)
            found_moviemon = m['id']
            name_rating = m['title'] + ' ' + m['rating']
        else:
            rand = 0
    return rand, found_moviemon, name_rating


def worldmap(request):
    move = request.GET.get('move', '')
    old_id = request.GET.get('id', '')
    movmn = Moviemon().dump()
    if do_move(movmn, move):
        movmn.found, movmn.found_moviemon, movmn.name_rating = random_move_event(movmn)
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
        'name_rating': movmn.name_rating,
        'movieballs': movmn.movieballs
    }

    return render(request, "worldmap.html", context)


def battle(request, id):
    game = Moviemon().dump()
    battle_moviemon = game.get_movie(id)
    movieball_try = request.GET.get('movieball')
    message = ""

    strange = game.get_strength()
    strange_monstr = float(battle_moviemon['rating']) * 10 if battle_moviemon else 0
    chance = 50 - int(strange_monstr) + strange * 5
    if chance < 1:
        chance = 1
    if chance > 90:
        chance = 90

    if movieball_try:
        if game.movieballs > 0 and battle_moviemon:
            game.movieballs -= 1
            random_n = random.randint(1, 90)
            if chance >= random_n:
                game.moviedex.append(battle_moviemon)
                game.movies_detail.remove(battle_moviemon)
                message = "You catched moviemon!"
            else:
                message = "Try your luck again!"
            game.save_tmp()
        else:
            message = "You don't have movieballs"

    context = {
        'left_href': '', 'up_href': '', 'down_href': '', 'right_href': '',
        'left_title': '', 'up_title': '', 'down_title': '', 'right_title': '',
        'select_href': '', 'start_href': '',
        'select_title': '', 'start_title': '',
        'a_href': '/battle/' + id + '?movieball=true',
        'b_href': '/worldmap?id=' + id,
        'a_title': '', 'b_title': 'Return to World Map',
        "message": message, "strange": strange,
        "movieballs": game.movieballs,
        "battle_moviemon": battle_moviemon, "id": id, "chance": chance
    }

    return render(request, "battle.html", context)


def do_move_moviedex(movmn, move, selected):
    did_move = False
    dict_selected = {'selected': '', 'left': '', 'right': '', 'up': '', 'down': ''}
    if move in ['left', 'right', 'up', 'down']:
        did_move = True
    if did_move:
        count = len(movmn.moviedex)
        if count >= 0:
            if selected in range(10):
                dict_selected['selected'] = selected
        if dict_selected['selected'] in range(10):
            if selected in range(5, 10) and move == 'up':
                if count > (int(selected) - 5):
                    dict_selected['up'] = str(int(selected) - 5)
            elif selected in range(5) and move == 'down':
                if count > (int(selected) + 5):
                    dict_selected['down'] = str(int(selected) + 5)
            elif selected in range(1, 10) and move == 'left':
                if count > (int(selected) - 1):
                    dict_selected['left'] = str(int(selected) - 1)
            elif selected in range(9) and move == 'right':
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
    movmn = Moviemon().dump()
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


def moviedex_detail(request, id):
    game = Moviemon().dump()
    controls_params = {
        'left_href': '', 'up_href': '', 'down_href': '', 'right_href': '',
        'left_title': '', 'up_title': '', 'down_title': '', 'right_title': '',
        'select_href': '', 'start_href': '',
        'select_title': '', 'start_title': '',
        'a_href': '', 'b_href': '/moviedex',
        'a_title': '', 'b_title': 'Moviedex',
        "moviemonDetail": game.moviedex[int(id)]
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
    save_dir = os.listdir("saved_files/")
    games_list = []
    for file in save_dir:
        if file != "session.txt":
            games_list.append(file)
    select_one = request.GET.get('select_one')
    if select_one:
        for file in games_list:
            if select_one in file:
                game = movmn.load(file)
                game.save_tmp()
                return(redirect("/worldmap"))
    slota = False
    slotb = False
    slotc = False
    gameSplitA = 0
    gameSplitB = 0
    gameSplitC = 0
    for game in games_list:
        if "slota" in game:
            slota = True
            gameSplit = game.split("_")
            gameSplitA = gameSplit[1]
        if "slotb" in game:
            slotb = True
            gameSplit = game.split("_")
            gameSplitB = gameSplit[1]
        if "slotc" in game:
            slotc = True
            gameSplit = game.split("_")
            gameSplitC = gameSplit[1]
    return render(request, "options_load_game.html",
                  {"slota": slota, "slotb": slotb, "slotc": slotc,
                   "slot_a": gameSplitA, "slot_b": gameSplitB,
                   "slot_c": gameSplitC, "b_href": "/", "b_title": "menu",
                   "a_href": "/worldmap/", "a_title": "load"})


def options_save_game(request):
    tmp = Moviemon().dump()
    save_dir = os.listdir("saved_files/")
    games_list = []
    for file in save_dir:
        if file != "session.txt":
            games_list.append(file)
    slota = False
    slotb = False
    slotc = False
    gameSplitA = 0
    gameSplitB = 0
    gameSplitC = 0
    for game in games_list:
        if "slota" in game:
            slota = True
            gameSplit = game.split("_")
            gameSplitA = gameSplit[1]
        if "slotb" in game:
            slotb = True
            gameSplit = game.split("_")
            gameSplitB = gameSplit[1]
        if "slotc" in game:
            slotc = True
            gameSplit = game.split("_")
            gameSplitC = gameSplit[1]
    slot_name = request.GET.get('slot')
    len_moviedex = len(tmp.moviedex)
    if slot_name:
        file_name = "slot" + slot_name.lower() + "_" + str(
            len_moviedex) + "_10.mmg"
        if "slota" in file_name:
            os.system("rm -f saved_files/slota*")
            tmp.save(file_name=file_name)
        if "slotb" in file_name:
            os.system("rm -f saved_files/slotb*")
            tmp.save(file_name=file_name)
        if "slotc" in file_name:
            os.system("rm -f saved_files/slotc*")
            tmp.save(file_name=file_name)
    tmp.dump()
    return render(request, "options_save_game.html",
                  {"slota": slota, "slotb": slotb, "slotc": slotc,
                   "slot_a": gameSplitA, "slot_b": gameSplitB,
                   "slot_c": gameSplitC, "b_href": "/options/",
                   "b_title": "return"})
