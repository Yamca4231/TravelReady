// main.js
// Główny plik startowy frontendowej logiki aplikacji
// Inicjalizuje efekt paralaksy oraz checklistę po załadowaniu strony

import { initParallax } from './parallax-init.js';
import { ChecklistModule } from './checklist.js';

/**
 * Inicjalizuje główne moduły aplikacji:
 * - Efekt paralaksy
 * - Checklistę (render + zapis)
 */
function initializeApp() {
	try {
		initParallax();     		// Inicjalizacja paralaksy dla wszystkich kontenerów
		ChecklistModule.init(); 	// Pobranie i wyrenderowanie checklisty
	} catch (err) {
		console.error("Błąd inicjalizacji aplikacji:", err);
	}
  }

// Rejestruje funkcję po pełnym załadowaniu DOM
// Dzięki temu mamy pewność, że elementy DOM są dostępne

document.addEventListener("DOMContentLoaded", initializeApp);