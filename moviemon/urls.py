from django.urls import path, re_path
from moviemon.views import home_page, worldmap, battle, moviedex, moviedexDetail, \
    options, options_save_game, options_load_game

urlpatterns = [
    path('', home_page, name='home'),
    path('worldmap/', worldmap, name='worldmap'),
    path('worldmap/<slug:id>', worldmap, name='worldmap'),
    path('battle/<slug:id>', battle, name='battle'),
    path('moviedex/', moviedex, name='moviedex'),
    path('moviedex/<slug:id>',moviedexDetail, name='moviedexDetail'),
    path('options/', options, name='options'),
    path('options/load_game/', options_load_game, name='optionsLoad'),
    path('options/save_game/', options_save_game, name='optionsSave'),
]
