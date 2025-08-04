# run.py
# Uruchamianie aplikacji Flask lokalnie (dla środowiska developerskiego)

from app import create_app

# Tworzenie aplikacji z konfiguracją środowiskową (config.py + config.env)
app = create_app()

if __name__ == "__main__":
    # Host i port odczytujemy z app.config, bo zostały załadowane z klasy konfiguracyjnej
    host = app.config.get("FLASK_HOST", "0.0.0.0")
    port = int(app.config.get("FLASK_PORT", 5000))
    debug = app.config.get("FLASK_DEBUG", True)
    env = app.config.get("ENV", "development")

    app.logger.info(f"Start aplikacji TravelReady na http://{host}:{port} [środowisko: {env}, debug={debug}]")
    app.run(host=host, port=port, debug=debug)
    