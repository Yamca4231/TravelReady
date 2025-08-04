# Aplikacja: Checklista podróżna (wersja klasyczna)

## Uruchomienie lokalne

1. Zainstaluj zależności:
```
pip install -r requirements.txt
```

2. Uruchom aplikację:
```
python run.py
```

3. Wejdź na `http://localhost:5000` w przeglądarce.

## Wdrożenie ręczne (np. na serwerze VPS)

1. Skopiuj pliki na serwer:
```
scp -r checklist-app/ user@host:/ścieżka
```

2. Połącz się przez SSH i uruchom:
```
cd /ścieżka/checklist-app
pip3 install -r requirements.txt
python3 run.py
```

3. (Opcjonalnie) Zainstaluj `screen` lub `tmux` żeby aplikacja działała w tle.
