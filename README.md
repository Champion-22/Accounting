# Buchhaltungs-Trainer 🎓



Eine interaktive Lernsoftware in Python, um Schweizer Buchungssätze auf spielerische Weise zu üben. [cite_start]Das Spiel basiert auf dem **Kontenrahmen KMU**  und ist als "Serious Game" konzipiert.

## 🚀 Features

* **Gamification:** Sammeln Sie Punkte, bauen Sie "Streaks" (🔥) auf und jagen Sie den Highscore. Aber Vorsicht: Sie haben nur 3 Leben (❤️)!
* **Zwei Lern-Modi:**
    * **Klassisch:** Mit Zeitlimit (25-30 Sek.) für schnelle Brutto-Buchungen.
    * **Pro:** Ohne Zeitlimit, für komplexe Netto-Buchungen mit mehreren Zeilen (wie im Screenshot-Beispiel).
* **Dynamische Aufgaben:** Kein stures Auswendiglernen. Die Geschäftsfälle werden bei jedem Start dynamisch und kontextbasiert generiert (z.B. "Zahlung der Büromiete..." statt "Zahle 6000").
* **Moderner Dark-Mode:** Eine saubere, dunkle Benutzeroberfläche (erstellt mit `tkinter` und `ttk`).
* **"Smoother" Timer:** Ein mit `Pillow (PIL)` gezeichneter, geglätteter Kreis-Timer.
* **Flexibler Kontenplan:** Ein separates, durchsuchbares Fenster zeigt alle Konten an und bleibt während des Spiels im Vordergrund.
* **Intelligente Eingabe:** Akzeptiert Kontonummern (`4200`), Namen (`Warenaufwand`) oder gängige Abkürzungen (`wa`, `fll`, `vst` etc.).

## ⚙️ Installation & Start

Das Skript benötigt Python 3 und eine zusätzliche Bibliothek.

1.  **Abhängigkeit installieren (Pillow):**
    ```bash
    pip install pillow
    ```

2.  **Skript ausführen:**
    ```bash
    python <name_ihrer_datei>.py
    ```

## 📝 Kontenplan

Der verwendete Kontenplan basiert auf dem Schweizer Kontenrahmen KMU.
