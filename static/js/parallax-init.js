// parallax-init.js
// Inicjalizuje efekt paralaksy oraz skalowanie tła przy zmianie rozmiaru

import { InteractiveBackground } from './lib/interactive-bg.js';

/**
 * Dostosowuje rozmiar tła wewnątrz kontenera
 */
function updateBgSize(container) {
	const bg = container.querySelector(".ibg-bg");
	if (bg) {
		bg.style.width = container.offsetWidth + "px";
		bg.style.height = container.offsetHeight + "px";
	}
}

export function initParallax() {
	const container = document.querySelector(".ibg-container");
	if (!container || container.dataset.ibgInit === "true") return;

	container.dataset.ibgInit = "true"; 	// Zabezpieczenie przed wielokrotną inicjalizacją
	new InteractiveBackground(container);	// Inicjalizacja paralaksy
	updateBgSize(container); // Pierwsze skalowanie

    //Obsługa window.resize
	let resizeTimeout;
	window.addEventListener("resize", () => {
		clearTimeout(resizeTimeout);
		resizeTimeout = setTimeout(() => updateBgSize(container), 250);
	});
}