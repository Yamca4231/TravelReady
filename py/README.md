# Aplikacja: TravelReady – Lista Pakowania na Wakacje

**TravelReady** to aplikacja webowa do interaktywnego zarządzania listą rzeczy do spakowania. Frontend (HTML + JavaScript) komunikuje się z backendem Python/Flask. Checklista jest pogrupowana na kategorie; użytkownik może zaznaczać/odznaczać pozycje.

Aplikacja obsługuje tryby DEV i PROD (konfiguracja w config.env).
---

## 📦 Funkcje

- REST API w Python/Flask.
- Frontend statyczny (HTML + JS) z dynamicznym renderowaniem checklisty.
- Dwa tryby zapisu zaznaczeń:
    - API (per-user) – zapis po stronie serwera w pliku JSON użytkownika (identyfikacja przez ciasteczko tr_uid),
    - Local – zapis w localStorage.
- Kategorowanie elementów checklisty.
- Interaktywny efekt paralaksy w tle (z wykorzystaniem JS).
- Obsługa wielu środowisk (development / production) z jednego pliku `config.env`.
- Globalna obsługa błędów (400/404/500) i logowanie.
- Walidacja po stronie backendu w ChecklistService:
  - poprawność typu (lista stringów),
  - whitelista dozwolonych elementów,
  - limit długości MAX_CHECKLIST_ITEMS

### Dodane w 1.2.0:
- Wersje wieloużytkownikowe (checklista per użytkownik).

## 📌 Planowane funkcje
- Edycja checklisty po stronie użytkownika (dodawanie/edycja kategorii).
- Logowanie i autoryzacja sesji dla indywidualnych list.
- Podgląd historii zmian / raporty.
- Panel administracyjny.

---

## 📁 Struktura projektu

TravelReady/
├── onfig.env.example             # Przykładowa konfiguracja środowiskowa (DEV/PROD)
│   pytest.ini
├── static/                       # Frontend serwowany przez Flask
│   ├── index.html
│   ├── css/
│   │   ├── main.js
│   │   └── checklist.js
│   ├── js/
│   │   │   checklist.js          # Logika checklisty i zapisu
│   │   │   main.js
│   │   │   parallax-init.js
│   │   │
│   │   └───lib
│   │           interactive-bg.js   
│   └── images/
│       ├── bg.jpg
│       └── favicon.ico
└── py/                           # Backend Flask
    ├── run.py                    # Start dev
    ├── wsgi.py                   # Start prod
    ├── README.md
    ├── requirements.txt
    ├── config/
    │   └── config.py       # Wczytanie pliku .env
    └── app/
        ├── __init__.py               # create_app(), konfiguracja static_folder itp.
        ├── log_config.py
        ├── error_handlers.py
        ├── repository.py          # Repozytorium danych (plik JSON / per-user)
        ├── storage.py
        ├── validation.py       # centralna walidacja
        ├── data/
        │   ├── items.py           # Statyczna lista pozycji checklisty
        │   ├── checked_items.json
        │   └── checked/           # (API per-user) pliki <tr_uid>.json
        ├── routes/
        │   ├── checklist_routes.py
        │   ├── debug_routes.py
        │   └── frontend_routes.py
        ├── services/
        │   └── checklist_service.py
        └───config
            └── config.py

---

## 💻 Tryb deweloperski – uruchomienie lokalne (dev)

1. Przejdź do katalogu głównego projektu:
```bash
cd TravelReady
```

2. Utwórz środowisko wirtualne i je aktywuj:
```bash
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. Zainstaluj wymagane biblioteki:
```bash
pip install -r py/requirements.txt
```

4. Ustaw zmienną środowiskową:
```bash
export TRAVELREADY_ENV=development  # Windows (CMD): set TRAVELREADY_ENV=development
```

5. Uruchom backend z pliku `run.py`, który obsługuje zarówno API, jak i pliki statyczne:
```bash
python py/run.py
```

6. Otwórz przeglądarkę i przejdź pod adres:
```
http://localhost:5000
```

7. Aplikacja automatycznie załaduje frontend z katalogu `htdocs/` oraz checklistę z backendu.

---

## OLD VERSION Apache host - STILL WORKING (Manual)

## XAMPP / MAMP (statyczne pliki)

1. Zainstaluj XAMPP (Windows) lub MAMP (macOS).
2. Skopiuj folder `TravelReady/` do katalogu serwera WWW, np. `C:/xampp/htdocs/TravelReady/`.
3. Uruchom Apache z panelu XAMPP.
4. Otwórz przeglądarkę i przejdź pod adres: `http://localhost/travelready/static/index.html`.

🔗 Aplikacja frontendowa połączy się z backendem Flask pod `http://localhost:5000`.

⚠️ Upewnij się, że backend działa (Flask API) i że adres `API_BASE_URL_DEVELOPMENT` w pliku `config.env` wskazuje na `http://localhost:5000`.

---

## 💻 Tryb deweloperski – wdrożenie automatyczne (CI/CD z GitLab)

1. Upewnij się, że w repozytorium znajduje się plik `.gitlab-ci.yml`. Przykład konfiguracji:
```yaml
stages:
  - deploy

deploy_development:
  stage: deploy
  only:
    - dev
  script:
    - ssh user@host 'cd ~/TravelReady && git pull'
    - ssh user@host 'cd ~/TravelReady && source venv/bin/activate && pip install -r py/requirements.txt'
    - ssh user@host 'export TRAVELREADY_ENV=development && python py/run.py'
```

2. Ten pipeline:
   - aktualizuje kod z gałęzi `dev`,
   - instaluje zależności z `py/requirements.txt`,
   - uruchamia aplikację w trybie developerskim z `py/run.py`.

3. Aplikacja będzie dostępna pod adresem `http://<host>:5000`.

---

## 🌍 Tryb produkcyjny – wdrożenie ręczne (manualne)

1. Skopiuj cały katalog `TravelReady/` na serwer, np. do `/opt/travelready/`:
```bash
scp -r TravelReady user@host:/opt/travelready
```

2. Zaloguj się na serwer i przejdź do katalogu:
```bash
ssh user@host
cd /opt/travelready
```

3. Utwórz środowisko i aktywuj je:
```bash
python3 -m venv venv
source venv/bin/activate
```

4. Zainstaluj zależności:
```bash
pip install -r py/requirements.txt
```

5. Uruchom backend za pomocą Gunicorn i `wsgi.py`:
```bash
gunicorn --chdir py --bind 127.0.0.1:5000 wsgi:app
```

6. Skonfiguruj serwer nginx jako reverse proxy dla portu 80/443:
```nginx
server {
    listen 80;
    server_name travelready.pl;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

7. Pliki statyczne (HTML, CSS, JS, obrazy) są serwowane przez backend Flask z katalogu `htdocs/`, dzięki wykorzystaniu `url_for('static', filename='...')`.

8. Ustaw w pliku `config.env`:
```env
API_BASE_URL_PRODUCTION=https://travelready.pl
```

9. Pamiętaj o ustawieniu zmiennej środowiskowej w konfiguracji systemu lub sesji:
```bash
export TRAVELREADY_ENV=production
```

---

## 🚀 Tryb produkcyjny – wdrożenie automatyczne (CI/CD z GitLab)

1. Ustaw plik `.gitlab-ci.yml` z poniższą konfiguracją (przykład):
```yaml
stages:
  - deploy

deploy_production:
  stage: deploy
  only:
    - main
  script:
    - ssh user@host 'cd /opt/travelready && git pull'
    - ssh user@host 'cd /opt/travelready && source venv/bin/activate && pip install -r py/requirements.txt'
    - ssh user@host 'sudo systemctl restart travelready'
```

2. Stwórz usługę systemową (`/etc/systemd/system/travelready.service`):
```ini
[Unit]
Description=TravelReady Flask App with Gunicorn
After=network.target

[Service]
User=yourusername
Group=www-data
WorkingDirectory=/opt/travelready/py
Environment="TRAVELREADY_ENV=production"
ExecStart=/opt/travelready/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:5000 wsgi:app

[Install]
WantedBy=multi-user.target
```

3. Aktywuj usługę:
```bash
sudo systemctl daemon-reload
sudo systemctl enable travelready
sudo systemctl start travelready
```

4. Aplikacja dostępna będzie pod `https://travelready.pl/`, a pliki statyczne nadal obsługiwane będą przez backend Flask z `htdocs/`.

---

## ⚙️ Konfiguracja środowisk

# Aplikacja obsługuje dwa środowiska działania:

development – lokalne uruchomienie z debugowaniem,
production – środowisko produkcyjne (np. Gunicorn + nginx).

Wszystkie ustawienia środowiskowe znajdują się w pliku config.env, który jest ładowany automatycznie przez aplikację Flask (config/config.py).

# Zmienna TRAVELREADY_ENV określa aktywne środowisko i powinna być ustawiona przed uruchomieniem aplikacji:

export TRAVELREADY_ENV=development     # Linux/macOS
set TRAVELREADY_ENV=development        # Windows (CMD)


## 🛠️ CI/CD z GitLab (planowana funkcja)

Wdrożenie aplikacji może zostać zautomatyzowane za pomocą GitLab CI/CD. Aktualna konfiguracja umożliwia automatyczne:

- pobranie kodu z repozytorium,
- zainstalowanie zależności Pythona (requirements.txt),
- restart aplikacji w trybie development lub production,
- w przyszłości: integrację z systemd/nginx + testy integracyjne.

# 📌 W pliku config.env musisz wcześniej ustawić wszystkie wymagane zmienne (np. klucze, porty, adresy API).

# 📍 Szczegóły konfiguracji produkcyjnej (np. reverse proxy z nginx) znajdziesz w sekcji Tryb produkcyjny – wdrożenie manualne / automatyczne powyżej.



