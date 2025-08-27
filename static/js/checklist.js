// js/checklist.js
// Moduł zarządzający checklistą: pobieranie danych, renderowanie, zapamiętywanie stanu
// API-first (fallback do localStorage)

// Klucz do przechowywania lokalnych danych checklisty
const STORAGE_KEY = "travelready_checked_items";

// Zmienna globalna wewnątrz modułu (widoczna dla wszystkich funkcji)
// Składana dynamicznie na podstawie protokołu i hosta bieżącej strony.
const apiBase = window.location.origin;

export const Checklist = (() => {
  let strategy = "api"; // domyślnie API (fallback do localStorage)
  /**
   * Funkcja Checklist
   * Pobiera checklistę z API i renderuje ją na stronie.
   * Zaznaczenia są odczytywane z localStorage.
   */
  async function init() {
    try {
      const res = await fetch(`${apiBase}/api/checklist`);      // Pobieranie listy elementów zgrupowanych wg kategorii
      const itemsByCategory = await res.json();                 // Parsowanie odpowiedzi jako JSON

// Spróbuj odczytać zaznaczenia z API; w razie problemu – z localStorage
      let checkedItems = [];
      try {
        const r2 = await fetch(`${apiBase}/api/checked`);
        if (r2.ok) {
          checkedItems = await r2.json();
        } else {
          checkedItems = loadFromStorage();
        }
      } catch {
        checkedItems = loadFromStorage();
      }
      const container = document.getElementById("checklist");   // kontener DOM, w którym umieszcza listę
      if (!container) return;                                   // Bez kontenera nie ma co renderować
      container.innerHTML = "";                                 // Czyszczenie zawartości kontenera

      renderChecklist(container, itemsByCategory, checkedItems);
    } catch (err) {
      console.error("❌ Błąd podczas pobierania danych checklisty:", err);
      showStatus("Błąd połączenia z API", "danger");
    }
  }

  /**
   * Renderuje checklistę z podziałem na kategorie.
   */
  function renderChecklist(container, itemsByCategory, checked) {
    for (const [category, items] of Object.entries(itemsByCategory)) {
      const section = document.createElement("section");
      section.classList.add("mb-4");

      // Nagłówek kategorii
      const header = document.createElement("h3");
      header.classList.add("h5", "fw-bold");
      header.textContent = category;
      section.appendChild(header);;

      // Lista elementów
      const ul = document.createElement("ul");
      ul.classList.add("list-group", "list-group-flush");

      // Iterowanie po elementach w tej kategorii
      items.forEach(item => ul.appendChild(createChecklistItem(item, checked)));

      section.appendChild(ul);
      container.appendChild(section);
    }
  }

  /**
   * Tworzy pojedynczy element listy (li) z checkboxem.
   */
  function createChecklistItem(item, checked) {
    const li = document.createElement("li");
    li.classList.add("list-group-item");

    //Tworzy element input typu checkbox
    const input = document.createElement("input");
    input.type = "checkbox";
    input.name = "item";
    input.value = item;
    input.checked = checked.includes(item);
    input.id = `item-${item}`;

    //Tworzy etykietę label powiązaną z checkboxem
    const label = document.createElement("label");
    label.htmlFor = input.id;
    label.classList.add("ms-2");
    label.textContent = item;

    // zapis lokalny – czekamy na wynik i dopiero wtedy pokazujemy komunikat
    input.addEventListener("change", async () => {
      const ok = await save();
      if (ok) {
        showStatus("Zapisano ✅", "success");
      }
      // w razie błędu saveToApi samo pokaże komunikat "Błąd zapisu do API"
    });

    // Złożenie struktury
    li.appendChild(input);
    li.appendChild(label);
    return li;
  }

  /**
   * Funkcja save
   * Zbiera wszystkie zaznaczone elementy do localStorage
   * Dodatkowo informuje użytkownika o sukcesie lub błędzie.
   */
  async function save() {
    const checked = getCheckedItems();

    if (strategy === "local") {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(checked));
      return true;
    } else if (strategy === "api") {
      return await saveToApi(checked);
    }
    return false;
  }

  /**
   * Strategia odczytu – local lub api
   * Wczytuje zaznaczone elementy z localStorage
   */
  function loadFromStorage() {
      const stored = localStorage.getItem(STORAGE_KEY);
      return stored ? JSON.parse(stored) : [];
  }

  /**
   * Zwraca aktualnie zaznaczone elementy checkboxów.
   */
  function getCheckedItems() {
    return Array.from(document.querySelectorAll("input[name='item']:checked"))
      .map(cb => cb.value);
  }

   /**
   * Ustawia tryb zapisu (strategię): "local" lub "api".
   */
    function setStrategy(mode) {
      if (["local", "api"].includes(mode)) {
        strategy = mode;
      } else {
        console.warn(`Nieznana strategia: ${mode}`);
      }
    }

  /**
   * Wysyła dane do API (zarezerwowane na przyszłość)
   */
  async function saveToApi(checked) {
    try {
      // Wysłanie danych do API – JSON z tablicą zaznaczonych wartości
      const res = await fetch(`${apiBase}/api/checked`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(checked)
      });
      if (!res.ok) {
        let detail = "";
        try { detail = await res.text(); } catch {}
        console.error("API error", res.status, detail);
        showStatus("Błąd zapisu do API", "danger");
        return false;
      }
      return true;
    } catch (err) {
      console.error("❌ Błąd zapisu checklisty do API:", err);
      showStatus("Błąd zapisu do API", "danger");
      return false;
    }
  }

  /**
   * Wyświetla komunikat statusu na ekranie.
   */
  function showStatus(message, type = "success") {
    const status = document.getElementById("status");
    if (!status) return;

    //status.classList.remove("alert-success", "alert-danger", "d-none");
    //status.classList.add(type === "success" ? "alert-success" : "alert-danger");
    status.className = `alert alert-${type}`;
    status.textContent = message;

    // Ukrycie alertu po 2 sekundach
    setTimeout(() => {
      status.classList.add("d-none");
      status.textContent = "";
    }, 2000);
  }

  // Publiczne API modułu
  return { init, setStrategy, getCheckedItems };
})();

export const ChecklistModule = Checklist;