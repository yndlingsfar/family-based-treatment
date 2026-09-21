---
description: Plant einen Tag mit sechs Mahlzeiten auf die ärztlich vorgegebene Kalorienmenge
---

Plane einen Tag für das Refeeding. Argument: `heute`, `morgen` oder ein Datum
(JJJJ-MM-TT). Ohne Argument: morgen.

Nutze die Skill `mahlzeit-planen`.

Ablauf:

1. Profil laden (`fbt.daten.lade_profil`). Fehlt `kcal_taeglich`, frage danach
   und plane nicht auf einer erfundenen Zahl — sag das offen, bevor irgendein
   Vorschlag kommt. Ist der Wert nur ein Platzhalter (siehe `kcal_quelle`),
   behandle ihn genauso, nicht als Vorgabe.
2. Die letzten drei Tagesdateien unter `$FBT_DATEN/tage/` ansehen, um
   Wiederholungen zu vermeiden und zu sehen, was zuletzt gut lief (welche
   Gerichte akzeptiert wurden, wo `anteil_gegessen` niedrig war).
3. Sechs Mahlzeiten vorschlagen, gemischt aus Netzwerk-Kochbuch und Cookidoo.
   Unverträglichkeiten und Fearfoods aus dem Profil ausschließen. Reicht ein
   Rezept nicht an die Zielkalorien heran, die Skill `rezept-anreichern`
   heranziehen statt die Portion frei zu schätzen.
4. Die Tagesdatei `$FBT_DATEN/tage/JJJJ-MM-TT.toml` nach dem Muster in
   `referenz/tag.vorlage.toml` schreiben. Alle Schlüssel der obersten Ebene
   (`datum`, `ziel_kcal`, `beobachtungen`) müssen vor der ersten
   `[[mahlzeit]]`-Tabelle stehen.
5. **Beide Ausgaben zeigen** — zuerst die Elternansicht mit kcal je Gericht und
   Tagessumme, danach die Tischansicht ohne jede Zahl, so wie sie am
   Kühlschrank hängen oder dem Kind gezeigt werden könnte.
6. Fragen, ob die fehlenden Zutaten in die Cookidoo-Einkaufsliste sollen
   (`cookidoo_add_recipe_ingredients` für Cookidoo-Rezepte,
   `cookidoo_add_additional_items` für alles andere). Nur schieben, wenn
   zugestimmt wird.
