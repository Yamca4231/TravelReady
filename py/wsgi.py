# wsgi.py
# Punkt wejścia dla produkcyjnych serwerów WSGI

from app import create_app

# Tworzymy instancję aplikacji Flask na podstawie środowiska (.env)
app = create_app()