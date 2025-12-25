# from django.apps import AppConfig


# class CartConfig(AppConfig):
#     default_auto_field = 'django.db.models.BigAutoField'
#     name = 'cart'

from django.apps import AppConfig

class CartConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cart'
    verbose_name = 'Aplikasi Cart'  # Memberi nama yang lebih awal di alfabet
