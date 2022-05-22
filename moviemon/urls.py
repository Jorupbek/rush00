from django.urls import path
from .views import HomePageView, worldmap, battle, moviedex, moviedex_detail, \
    options, options_save_game, options_load_game

urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path('worldmap/', worldmap, name='worldmap'),
    path('worldmap/<slug:id>', worldmap, name='worldmap'),
    path('battle/<slug:id>', battle, name='battle'),
    path('moviedex/', moviedex, name='moviedex'),
    path('moviedex/<slug:id>',moviedex_detail, name='moviedex_detail'),
    path('options/', options, name='options'),
    path('options/load_game/', options_load_game, name='optionsLoad'),
    path('options/save_game/', options_save_game, name='optionsSave'),
]
