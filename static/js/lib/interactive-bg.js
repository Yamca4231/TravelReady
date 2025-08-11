// interactive-bg.js
// Klasa implementująca efekt paralaksy reagujący na mysz i czujniki ruchu

export class InteractiveBackground {
	constructor(element, options = {}) {
	  this.el = element;                  // element DOM, do którego przypisywany jest efekt tła

        // Domyślne ustawienia
		const defaults = {
			strength: 25,				// siła przesunięcia (w pikselach)
			scale: 1.05,				// powiększenie tła (dla efektu głębi)
			animationSpeed: 100,		// szybkość animacji (ms)
			contain: true,				// czy ukrywać przepełnienie tła (overflow)
			wrapContent: false			// czy zawinąć oryginalną zawartość w dodatkowy div z tłem
		};
		this.settings = { ...defaults, ...options };

        // Wymiary kontenera
		this.width = this.el.offsetWidth;
		this.height = this.el.offsetHeight;

        // Współczynniki przesunięcia w osi X i Y
		this.sh = this.settings.strength / this.height;     // siła pionowa
		this.sw = this.settings.strength / this.width;      // siła pozioma

        // Wykrycie urządzenia z ekranem dotykowym
		this.hasTouch = 'ontouchstart' in document.documentElement;

		this.init();    // inicjalizacja komponentu
	}

	init() {
        // Jeśli `contain` włączony, blokuje wyciekanie obrazu poza element
		if (this.settings.contain) {
			this.el.style.overflow = "hidden";
		}
		this.prepareBackground();
		this.bg = this.el.querySelector(":scope > .ibg-bg");	// Referencja do tła
		if (!this.bg) return;

        // Pobieranie tła z atrybutu data-ibg-bg, jeśli istnieje
		const bgUrl = this.el.getAttribute("data-ibg-bg");
		if (bgUrl) {
			this.bg.style.background = `url('${bgUrl}') no-repeat center center`;
			this.bg.style.backgroundSize = "cover";
		}

		// Nadaje tłu rozmiary kontenera
		this.bg.style.width = `${this.width}px`;
		this.bg.style.height = `${this.height}px`;

        // Reakcja zależna od typu urządzenia:
		// – Na desktopie obsługuje efekt przez ruch myszy
		// – Na urządzeniach mobilnych próbuje użyć akcelerometru,
		//   TO DO: Wiele przeglądarek na użądzeniach mobilnych wymaga uprzedniego zezwolenia użytkownika
		if (this.hasTouch || screen.width <= 699) {
            // TO DO: Wymaga zgody użytkownika (np. przez uprawnienia lub dialog)
			window.addEventListener("devicemotion", this.handleMotion.bind(this));
		} else {
            // Ruch myszką
			this.el.addEventListener("mouseenter", this.handleEnter.bind(this));
			this.el.addEventListener("mousemove", this.handleMove.bind(this));
			this.el.addEventListener("mouseleave", this.handleLeave.bind(this));
		}

		// Obsługa zmiany rozmiaru kontenera
		window.addEventListener("resize", () => {
			this.width = this.el.offsetWidth;
			this.height = this.el.offsetHeight;
			this.sh = this.settings.strength / this.height;
			this.sw = this.settings.strength / this.width;
			this.bg.style.width = `${this.width}px`;
			this.bg.style.height = `${this.height}px`;
		});
	}

	prepareBackground() {
		if (this.settings.wrapContent) {
			const wrapper = document.createElement("div");
			wrapper.classList.add("ibg-bg");
			while (this.el.firstChild) wrapper.appendChild(this.el.firstChild);
			this.el.appendChild(wrapper);
		} else {
			const bg = document.createElement("div");
			bg.classList.add("ibg-bg");
			this.el.prepend(bg);
		}
	}

    // Obsługa ruchu urządzenia (jeśli dostęp do akcelerometru nie jest zablokowany)
	handleMotion(event) {
        // Przyspieszenie w osiach X i Y (odwrotne wartości do przesunięcia)
		const x = -(event.accelerationIncludingGravity.x || 0) * 2;
		const y = -(event.accelerationIncludingGravity.y || 0) * 2;
		this.setTransform(x, y);
	}

    // Wejście kursora – ustawienie animacji wejściowej
	handleEnter() {
		this.bg.style.transition = `transform ${this.settings.animationSpeed}ms linear`;
		this.setTransform(0, 0);    // reset pozycji tła
	}

    // Ruch kursora – dynamiczne przesuwanie tła względem pozycji myszy
	handleMove(e) {
		const x = ((this.sw * ((e.clientX - this.el.offsetLeft) - (this.width / 2))) * -1);
		const y = ((this.sh * ((e.clientY - this.el.offsetTop) - (this.height / 2))) * -1);
		this.bg.style.transition = "none";  // brak animacji przy ciągłym ruchu
		this.setTransform(x, y);
	}

    // Opuszczenie elementu – animowany powrót do środka
	handleLeave() {
		this.bg.style.transition = `transform ${this.settings.animationSpeed}ms linear`;
		this.setTransform(0, 0);    // reset
	}

    // Zastosowanie transformacji tła (przesunięcie + skalowanie)
	setTransform(x, y) {
		const scale = this.settings.scale;
        // Macierz transformacji CSS: [skalowanie X, 0, 0, skalowanie Y, przesunięcie X, przesunięcie Y]
		const transform = `matrix(${scale}, 0, 0, ${scale}, ${x}, ${y})`;
		this.bg.style.transform = transform;
	}
}

// Automatyczna inicjalizacja wszystkich .ibg-container na stronie
export function initParallaxAll() {
	const containers = document.querySelectorAll(".ibg-container");
	containers.forEach(container => new InteractiveBackground(container));
  }  
