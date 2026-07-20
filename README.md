# Familyboard Whiteboard für Home Assistant

Backend-Integration für ein freies Zeichenbrett: Freihand-Striche (Stift/
Radierer) und frei platzierbare Text-Notizen mit Tastatureingabe, gespeichert
und über mehrere Geräte hinweg abrufbar.

Die passende Lovelace-Karte (die eigentliche Zeichenfläche) lebt in einem
eigenen Repository:
👉 **[familyboard-whiteboard-card](https://github.com/GoDigitalizeMe/familyboard-whiteboard-card)**

Schwesterprojekte:
👉 **[familyboard-planner-ha](https://github.com/GoDigitalizeMe/familyboard-planner-ha)** (Kalender)
👉 **[familyboard-tasks-ha](https://github.com/GoDigitalizeMe/familyboard-tasks-ha)** (To-Dos/Einkaufslisten)

## Architektur

Anders als Planner und Tasks hat ein Whiteboard keine externe
Home-Assistant-Quelle, die es abfragen könnte (keine Kalender, keine
To-Do-Listen) – der gesamte Inhalt entsteht direkt durch Zeichnen/Tippen in
der Karte. Deshalb ist dieses Backend bewusst schlank:

- **`custom_components/familyboard_whiteboard/`** (Python) – ein Board pro
  Config Entry, Inhalt (`strokes` = Freihand-Striche, `notes` =
  Text-Notizen) liegt in einem eigenen Storage (`.storage/`), kein
  `DataUpdateCoordinator`/Polling nötig.
- Zwei WebSocket-Befehle für die Karte: `familyboard_whiteboard/get_board`
  (laden) und `familyboard_whiteboard/save_board` (**kompletter** Ersatz
  von Strichen + Notizen bei jedem Speichern – kein Merge/Patch. Für ein
  Familien-Wandboard ausreichend, aber kein Editor für gleichzeitiges
  Bearbeiten durch mehrere Personen in Echtzeit).
- Ein schlankes Sensor-Entity (`sensor.<board>_whiteboard`, Zeitstempel der
  letzten Änderung) dient der Karte als Anker (`config_entry_id` in den
  Attributen) und zeigt Strich-/Notizanzahl als Zusatzattribute.
- Service `familyboard_whiteboard.clear_board` (Entity-Ziel) leert ein
  Board – praktisch auch für Automationen (z. B. „jeden Montag früh leeren“).

## Installation

### Über HACS (empfohlen)

HACS → Integrationen → benutzerdefiniertes Repository hinzufügen:
`https://github.com/GoDigitalizeMe/familyboard-whiteboard-ha`, Kategorie
**Integration**. Danach Home Assistant **neu starten**.

### Manuell

1. Ordner `custom_components/familyboard_whiteboard` nach
   `config/custom_components/familyboard_whiteboard` kopieren.
2. Home Assistant neu starten.

## Einrichtung

1. **Einstellungen → Geräte & Dienste → Integration hinzufügen** →
   „Familyboard Whiteboard“ suchen.
2. Namen für das Board vergeben (z. B. „Küche“).
3. Fertig – es entsteht `sensor.<board>_whiteboard`.

Du kannst mehrere Whiteboards anlegen – jedes bekommt sein eigenes
Sensor-Entity und kann in einer eigenen Karte angezeigt werden.

Installiere anschließend **[familyboard-whiteboard-card](https://github.com/GoDigitalizeMe/familyboard-whiteboard-card)**
und wähle dort im Karten-Editor das eben entstandene Sensor-Entity aus.
