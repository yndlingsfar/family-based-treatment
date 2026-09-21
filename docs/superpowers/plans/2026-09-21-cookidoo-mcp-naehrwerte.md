# Cookidoo-MCP: Nährwerte und Zubereitungsschritte — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `cookidoo_get_recipe_details` liefert die Nährwerte (kcal und Makros) und die Zubereitungsschritte eines Rezepts, die die Cookidoo-API bereits mitschickt, aber der Mapper verwirft.

**Architecture:** Rein additive Änderung an einer Stelle. Der HTTP-Client holt die Rezeptantwort bereits vollständig; `recipeDetailsFromJson` greift sich nur eine Teilmenge der Felder heraus. Zwei neue Mapper-Hilfsfunktionen und zwei neue Felder im Domain-Typ. Kein Eingriff in Client, Query-Handler, Transport oder Suchendpunkt.

**Tech Stack:** TypeScript, NestJS, CQRS, Jest, pnpm

**Spec:** `/Users/danielsteiner/Projects/family-based-treatment/docs/superpowers/specs/2026-09-21-fbt-plugin-design.md` (Abschnitt 4)

**Arbeitsverzeichnis:** `/Users/danielsteiner/Projects/cookidoo-mcp` — ein **anderes Repo** als das, in dem dieser Plan liegt. Alle Pfadangaben unten sind relativ zu diesem Arbeitsverzeichnis.

## Global Constraints

- **Bezugsgröße wird durchgereicht, nicht normalisiert.** `basisUnit` behält den Wert aus `unitNotation` (`"Portion"`, `"100 g"`, …). Niemals auf „Portion" annehmen oder umrechnen.
- **Cookidoos Typnamen bleiben roh.** `carb2`, `kJ`, `dietaryFibre` werden nicht umbenannt oder umgedeutet.
- **`nutrition` ist nullable.** Fehlende Nährwerte sind `null`, niemals ein Objekt mit Nullwerten. Fehlend ≠ null Kalorien.
- **Das API-Feld heißt `unittype`** (kleines t), nicht `unitType`.
- **Der Suchendpunkt bleibt unangetastet.** `searchResultFromJson` und `CookidooSearchRecipeHit` werden nicht verändert.
- **Bestehende Tests bleiben grün.** Die Änderung ist additiv; kein bestehendes Feld ändert Name, Typ oder Semantik.
- **Sprache im Code:** Englisch (Bezeichner, Kommentare, Commit-Messages), wie im übrigen Repo.
- Branch: `feat/recipe-nutrition-and-steps`, ausgehend von `main`.

## File Structure

| Datei | Verantwortung | Änderung |
|---|---|---|
| `src/contexts/cookidoo/domain/types/cookidoo-recipe.type.ts` | Domänentypen für Rezepte | 3 neue Interfaces, 2 neue Felder in `CookidooRecipeDetails` |
| `src/contexts/cookidoo/infrastructure/cookidoo/cookidoo.mappers.ts` | Übersetzung API-JSON → Domäne | 2 neue Hilfsfunktionen, `recipeDetailsFromJson` erweitert |
| `src/contexts/cookidoo/infrastructure/cookidoo/cookidoo.mappers.spec.ts` | Mapper-Tests | neue Testfälle |
| `src/contexts/cookidoo/transport/mcp/tools/recipe-get-details.tool.ts` | MCP-Tool-Beschreibung | Beschreibungstext ergänzt |
| `scripts/verify-recipe-details.ts` | Einmal-Verifikation gegen die echte API | neu |

Kein Eingriff in `cookidoo-http.client.ts`, `recipe-find-details.handler.ts` oder die Schemas — der Client reicht die Antwort bereits vollständig an den Mapper weiter.

---

### Task 0: Branch anlegen

**Files:** keine

- [ ] **Step 1: Branch von `main` erzeugen**

```bash
cd /Users/danielsteiner/Projects/cookidoo-mcp
git checkout main
git status --short
git checkout -b feat/recipe-nutrition-and-steps
```

Erwartet: `git status --short` ist leer (sauberer Arbeitsbaum), danach Branch `feat/recipe-nutrition-and-steps`.

- [ ] **Step 2: Abhängigkeiten sicherstellen und Ausgangslage prüfen**

```bash
pnpm install
pnpm test
```

Erwartet: Alle Tests grün. **Wenn hier schon etwas rot ist, zuerst melden und nicht weiterarbeiten** — sonst ist später nicht unterscheidbar, ob ein Fehler von dieser Änderung stammt.

---

### Task 1: Nährwerte im Domain-Typ und Mapper

**Files:**
- Modify: `src/contexts/cookidoo/domain/types/cookidoo-recipe.type.ts`
- Modify: `src/contexts/cookidoo/infrastructure/cookidoo/cookidoo.mappers.ts:169-201` (`recipeDetailsFromJson`)
- Test: `src/contexts/cookidoo/infrastructure/cookidoo/cookidoo.mappers.spec.ts`

**Interfaces:**
- Consumes: nichts aus früheren Tasks.
- Produces:
  - `CookidooNutritionValue { readonly type: string; readonly number: number; readonly unit: string }`
  - `CookidooNutrition { readonly basisQuantity: number; readonly basisUnit: string; readonly values: CookidooNutritionValue[] }`
  - Feld `readonly nutrition: CookidooNutrition | null` auf `CookidooRecipeDetails`

**Hintergrund — so sieht die API-Antwort aus** (echter Auszug aus `r16687`):

```json
"nutritionGroups": [
  { "name": "",
    "recipeNutritions": [
      { "quantity": 1,
        "unitNotation": "Portion",
        "nutritions": [
          { "type": "protein",      "number": 5,   "unittype": "g" },
          { "type": "kJ",           "number": 959, "unittype": "kJ" },
          { "type": "fat",          "number": 14,  "unittype": "g" },
          { "type": "kcal",         "number": 229, "unittype": "kcal" },
          { "type": "dietaryFibre", "number": 5.9, "unittype": "g" },
          { "type": "carb2",        "number": 19,  "unittype": "g" } ] } ] } ]
```

- [ ] **Step 1: Typen ergänzen**

In `src/contexts/cookidoo/domain/types/cookidoo-recipe.type.ts` **vor** `CookidooRecipeDetails` einfügen:

```ts
/** A single nutrition figure as reported by Cookidoo, with its raw type name. */
export interface CookidooNutritionValue {
  readonly type: string;
  readonly number: number;
  readonly unit: string;
}

/**
 * Nutrition figures for a recipe, together with the basis they refer to.
 * The basis is preserved verbatim: it may be `1 Portion`, `100 g`, or another
 * unit, and must never be assumed to be per portion.
 */
export interface CookidooNutrition {
  readonly basisQuantity: number;
  readonly basisUnit: string;
  readonly values: CookidooNutritionValue[];
}
```

In `CookidooRecipeDetails` **nach** `readonly utensils: string[];` einfügen:

```ts
  readonly nutrition: CookidooNutrition | null;
```

- [ ] **Step 2: Fehlschlagenden Test schreiben**

In `cookidoo.mappers.spec.ts`, innerhalb von `describe('recipeDetailsFromJson', ...)`, nach dem bestehenden Test `'falls back to null times when not present'` einfügen:

```ts
    it('maps nutrition values and preserves the basis they refer to', () => {
      const result = recipeDetailsFromJson(
        {
          id: 'r4',
          title: 'Soup',
          recipeIngredientGroups: [],
          nutritionGroups: [
            {
              name: '',
              recipeNutritions: [
                {
                  quantity: 1,
                  unitNotation: 'Portion',
                  nutritions: [
                    { type: 'kcal', number: 229, unittype: 'kcal' },
                    { type: 'fat', number: 14, unittype: 'g' },
                    { type: 'carb2', number: 19, unittype: 'g' },
                  ],
                },
              ],
            },
          ],
        },
        localization,
      );

      expect(result.nutrition).toEqual({
        basisQuantity: 1,
        basisUnit: 'Portion',
        values: [
          { type: 'kcal', number: 229, unit: 'kcal' },
          { type: 'fat', number: 14, unit: 'g' },
          { type: 'carb2', number: 19, unit: 'g' },
        ],
      });
    });

    it('keeps a per-100g basis instead of assuming portions', () => {
      const result = recipeDetailsFromJson(
        {
          id: 'r5',
          title: 'Spread',
          recipeIngredientGroups: [],
          nutritionGroups: [
            {
              recipeNutritions: [
                {
                  quantity: 100,
                  unitNotation: 'g',
                  nutritions: [{ type: 'kcal', number: 560, unittype: 'kcal' }],
                },
              ],
            },
          ],
        },
        localization,
      );

      expect(result.nutrition?.basisQuantity).toBe(100);
      expect(result.nutrition?.basisUnit).toBe('g');
    });

    it('returns null nutrition when the recipe reports none', () => {
      const result = recipeDetailsFromJson(
        { id: 'r6', title: 'Unknown', recipeIngredientGroups: [] },
        localization,
      );

      expect(result.nutrition).toBeNull();
    });

    it('returns null nutrition when the groups contain no usable figures', () => {
      const result = recipeDetailsFromJson(
        {
          id: 'r7',
          title: 'Empty',
          recipeIngredientGroups: [],
          nutritionGroups: [{ recipeNutritions: [{ nutritions: [] }] }],
        },
        localization,
      );

      expect(result.nutrition).toBeNull();
    });
```

- [ ] **Step 3: Tests laufen lassen und Fehlschlag bestätigen**

```bash
cd /Users/danielsteiner/Projects/cookidoo-mcp
npx jest src/contexts/cookidoo/infrastructure/cookidoo/cookidoo.mappers.spec.ts -t "nutrition"
```

Erwartet: FAIL. Die vier neuen Tests scheitern, weil `result.nutrition` `undefined` ist.

- [ ] **Step 4: Mapper implementieren**

In `cookidoo.mappers.ts` **direkt vor** `export function recipeDetailsFromJson` einfügen:

```ts
/**
 * Read the nutrition figures from a recipe payload.
 *
 * Cookidoo reports figures against a basis (`1 Portion`, `100 g`, …) that is
 * carried through unchanged: assuming portions here would silently scale every
 * downstream calculation. Returns null when no usable figures are present,
 * which is not the same as zero.
 */
function nutritionFromJson(groups: unknown): CookidooNutrition | null {
  if (!Array.isArray(groups)) {
    return null;
  }
  for (const group of groups as Json[]) {
    const entries: Json[] = group?.recipeNutritions ?? [];
    if (!Array.isArray(entries)) {
      continue;
    }
    for (const entry of entries) {
      const raw: Json[] = Array.isArray(entry?.nutritions)
        ? entry.nutritions
        : [];
      const values: CookidooNutritionValue[] = raw
        .filter(
          (value) =>
            typeof value?.type === 'string' &&
            value?.number !== undefined &&
            value?.number !== null &&
            !Number.isNaN(Number(value.number)),
        )
        .map((value) => ({
          type: value.type,
          number: Number(value.number),
          unit: typeof value.unittype === 'string' ? value.unittype : '',
        }));
      if (values.length === 0) {
        continue;
      }
      return {
        basisQuantity: Number(entry?.quantity ?? 1),
        basisUnit:
          typeof entry?.unitNotation === 'string' ? entry.unitNotation : '',
        values,
      };
    }
  }
  return null;
}
```

Den Import in `cookidoo.mappers.ts` ergänzen — in dem bestehenden Import-Block aus `'../../domain/types/cookidoo-recipe.type'` die Namen `CookidooNutrition` und `CookidooNutritionValue` hinzufügen (alphabetisch vor `CookidooRecipeDetails`).

Im Rückgabeobjekt von `recipeDetailsFromJson` **nach** `utensils,` einfügen:

```ts
    nutrition: nutritionFromJson(recipe.nutritionGroups),
```

- [ ] **Step 5: Tests laufen lassen und Erfolg bestätigen**

```bash
npx jest src/contexts/cookidoo/infrastructure/cookidoo/cookidoo.mappers.spec.ts
```

Erwartet: PASS, inklusive der beiden vorher schon vorhandenen `recipeDetailsFromJson`-Tests.

- [ ] **Step 6: Committen**

```bash
git add src/contexts/cookidoo/domain/types/cookidoo-recipe.type.ts \
        src/contexts/cookidoo/infrastructure/cookidoo/cookidoo.mappers.ts \
        src/contexts/cookidoo/infrastructure/cookidoo/cookidoo.mappers.spec.ts
git commit -m "feat(recipe): map nutrition figures with their reported basis"
```

---

### Task 2: Zubereitungsschritte im Domain-Typ und Mapper

**Files:**
- Modify: `src/contexts/cookidoo/domain/types/cookidoo-recipe.type.ts`
- Modify: `src/contexts/cookidoo/infrastructure/cookidoo/cookidoo.mappers.ts`
- Test: `src/contexts/cookidoo/infrastructure/cookidoo/cookidoo.mappers.spec.ts`

**Interfaces:**
- Consumes: `CookidooRecipeDetails` aus Task 1 (das Feld `nutrition` existiert bereits).
- Produces:
  - `CookidooRecipeStep { readonly group: string | null; readonly number: string | null; readonly text: string }`
  - Feld `readonly steps: CookidooRecipeStep[]` auf `CookidooRecipeDetails`

**Hintergrund — so sieht die API-Antwort aus** (echter Auszug aus `r16687`):

```json
"recipeStepGroups": [
  { "title": "",
    "recipeSteps": [
      { "title": "1", "formattedText": "Wasser und Salz in den Mixtopf geben, Gareinsatz einhängen, Möhren, Staudensellerie, <NOBR>100 g Kartoffeln</NOBR> und <NOBR>100 g Porree</NOBR> einwiegen und <nobr>14 Min./Varoma/Stufe 1</nobr> garen." },
      { "title": "2", "formattedText": "Zwiebel und <NOBR>50 g Porree</NOBR> in den Mixtopf geben, <nobr>8 Sek./Stufe 5</nobr> zerkleinern." } ] } ]
```

Die Gruppentitel sind häufig leer. `<NOBR>` kommt in beiden Schreibweisen vor.

- [ ] **Step 1: Typ ergänzen**

In `cookidoo-recipe.type.ts` **nach** `CookidooNutrition` einfügen:

```ts
/** One preparation step, with the group it belongs to and its printed number. */
export interface CookidooRecipeStep {
  readonly group: string | null;
  readonly number: string | null;
  readonly text: string;
}
```

In `CookidooRecipeDetails` **nach** `readonly nutrition: CookidooNutrition | null;` einfügen:

```ts
  readonly steps: CookidooRecipeStep[];
```

- [ ] **Step 2: Fehlschlagenden Test schreiben**

In `cookidoo.mappers.spec.ts`, innerhalb von `describe('recipeDetailsFromJson', ...)`, nach den Nährwert-Tests einfügen:

```ts
    it('flattens preparation steps and strips NOBR markup', () => {
      const result = recipeDetailsFromJson(
        {
          id: 'r8',
          title: 'Soup',
          recipeIngredientGroups: [],
          recipeStepGroups: [
            {
              title: '',
              recipeSteps: [
                {
                  title: '1',
                  formattedText:
                    'Add <NOBR>100 g potatoes</NOBR> and cook <nobr>14 min/Varoma/speed 1</nobr>.',
                },
                { title: '2', formattedText: 'Blend for 8 sec/speed 5.' },
              ],
            },
          ],
        },
        localization,
      );

      expect(result.steps).toEqual([
        {
          group: null,
          number: '1',
          text: 'Add 100 g potatoes and cook 14 min/Varoma/speed 1.',
        },
        { group: null, number: '2', text: 'Blend for 8 sec/speed 5.' },
      ]);
    });

    it('keeps non-empty group titles on every step of the group', () => {
      const result = recipeDetailsFromJson(
        {
          id: 'r9',
          title: 'Cake',
          recipeIngredientGroups: [],
          recipeStepGroups: [
            {
              title: 'Dough',
              recipeSteps: [{ title: '1', formattedText: 'Mix.' }],
            },
            {
              title: 'Topping',
              recipeSteps: [{ title: '1', formattedText: 'Whip.' }],
            },
          ],
        },
        localization,
      );

      expect(result.steps).toEqual([
        { group: 'Dough', number: '1', text: 'Mix.' },
        { group: 'Topping', number: '1', text: 'Whip.' },
      ]);
    });

    it('returns an empty step list when the recipe reports none', () => {
      const result = recipeDetailsFromJson(
        { id: 'r10', title: 'Unknown', recipeIngredientGroups: [] },
        localization,
      );

      expect(result.steps).toEqual([]);
    });
```

- [ ] **Step 3: Tests laufen lassen und Fehlschlag bestätigen**

```bash
npx jest src/contexts/cookidoo/infrastructure/cookidoo/cookidoo.mappers.spec.ts -t "step"
```

Erwartet: FAIL, weil `result.steps` `undefined` ist.

- [ ] **Step 4: Mapper implementieren**

In `cookidoo.mappers.ts` **direkt vor** `export function recipeDetailsFromJson` (neben `nutritionFromJson`) einfügen:

```ts
/**
 * Flatten the preparation steps of a recipe.
 *
 * `<NOBR>` wrappers are markup that Cookidoo uses to keep quantities and
 * machine settings on one line; the text inside them is content and is kept.
 */
function stepsFromJson(groups: unknown): CookidooRecipeStep[] {
  if (!Array.isArray(groups)) {
    return [];
  }
  return (groups as Json[]).flatMap((group) => {
    const steps: Json[] = Array.isArray(group?.recipeSteps)
      ? group.recipeSteps
      : [];
    const groupTitle =
      typeof group?.title === 'string' && group.title.trim() !== ''
        ? group.title
        : null;
    return steps
      .filter((step) => typeof step?.formattedText === 'string')
      .map((step) => ({
        group: groupTitle,
        number:
          typeof step.title === 'string' && step.title.trim() !== ''
            ? step.title
            : null,
        text: step.formattedText.replace(/<\/?nobr>/gi, ''),
      }));
  });
}
```

Den Import-Block aus `'../../domain/types/cookidoo-recipe.type'` um `CookidooRecipeStep` ergänzen.

Im Rückgabeobjekt von `recipeDetailsFromJson` **nach** der `nutrition`-Zeile einfügen:

```ts
    steps: stepsFromJson(recipe.recipeStepGroups),
```

- [ ] **Step 5: Tests laufen lassen und Erfolg bestätigen**

```bash
npx jest src/contexts/cookidoo/infrastructure/cookidoo/cookidoo.mappers.spec.ts
```

Erwartet: PASS, alle Tests der Datei.

- [ ] **Step 6: Committen**

```bash
git add src/contexts/cookidoo/domain/types/cookidoo-recipe.type.ts \
        src/contexts/cookidoo/infrastructure/cookidoo/cookidoo.mappers.ts \
        src/contexts/cookidoo/infrastructure/cookidoo/cookidoo.mappers.spec.ts
git commit -m "feat(recipe): map preparation steps, stripping NOBR markup"
```

---

### Task 3: Tool-Beschreibung und Verifikation gegen die echte API

**Files:**
- Modify: `src/contexts/cookidoo/transport/mcp/tools/recipe-get-details.tool.ts:18-19`
- Create: `scripts/verify-recipe-details.ts`

**Interfaces:**
- Consumes: `recipeDetailsFromJson` sowie `CookidooNutrition` und `CookidooRecipeStep` aus Tasks 1 und 2.
- Produces: nichts für spätere Tasks.

Warum ein Verifikationsskript und keine Fixture-Datei: Die synthetischen Tests aus Tasks 1 und 2 belegen das Verhalten des Mappers, aber nicht, dass unsere Annahmen über die echte Antwortstruktur stimmen. Ein Skript, das den öffentlichen Endpunkt abruft und den Mapper darauf anwendet, prüft genau das — ohne Cookidoos Rezeptinhalte dauerhaft im Repo abzulegen.

- [ ] **Step 1: Tool-Beschreibung ergänzen**

In `recipe-get-details.tool.ts` das Feld `description` ersetzen durch:

```ts
  readonly description =
    'Returns the full details of a single recipe by id: ingredients, preparation steps, nutrition (with the basis the figures refer to, e.g. per portion or per 100 g), utensils, notes, difficulty, serving size, active/total time and image URLs.';
```

- [ ] **Step 2: Verifikationsskript anlegen**

`scripts/verify-recipe-details.ts`:

```ts
/**
 * Verifies the recipe details mapper against a live Cookidoo response.
 *
 * The recipe endpoint answers with JSON without authentication, so this needs
 * no session. Run it after changing the mapper to confirm that the assumptions
 * about the upstream payload still hold.
 *
 * Usage: pnpm verify:recipe [recipeId]
 */
import { CookidooLocalization } from '../src/core/config/cookidoo.config';
import { recipeDetailsFromJson } from '../src/contexts/cookidoo/infrastructure/cookidoo/cookidoo.mappers';

const localization: CookidooLocalization = {
  countryCode: 'de',
  language: 'de-DE',
  url: 'https://cookidoo.de/foundation/de-DE',
};

async function main(): Promise<void> {
  const id = process.argv[2] ?? 'r16687';
  const url = `https://cookidoo.de/recipes/recipe/de-DE/${id}`;

  const response = await fetch(url, { headers: { Accept: 'application/json' } });
  if (!response.ok) {
    throw new Error(`${url} answered ${response.status}`);
  }

  const details = recipeDetailsFromJson(await response.json(), localization);
  const kcal = details.nutrition?.values.find((v) => v.type === 'kcal');

  console.log(`recipe:     ${details.name} (${details.id})`);
  console.log(`portions:   ${details.servingSize}`);
  console.log(
    `nutrition:  ${
      details.nutrition
        ? `${kcal?.number ?? '?'} kcal per ${details.nutrition.basisQuantity} ${details.nutrition.basisUnit}`
        : 'none reported'
    }`,
  );
  console.log(`steps:      ${details.steps.length}`);
  if (details.steps.length > 0) {
    console.log(`first step: ${details.steps[0].text.slice(0, 80)}…`);
  }
  if (details.steps.some((step) => /<\/?nobr>/i.test(step.text))) {
    throw new Error('NOBR markup survived in at least one step');
  }
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
```

- [ ] **Step 3: Skript-Eintrag in `package.json` ergänzen**

In `scripts` nach der Zeile `"login:check": ...` einfügen:

```json
    "verify:recipe": "ts-node -r tsconfig-paths/register scripts/verify-recipe-details.ts",
```

- [ ] **Step 4: Verifikation ausführen**

```bash
cd /Users/danielsteiner/Projects/cookidoo-mcp
pnpm verify:recipe
```

Erwartet, wörtlich:

```
recipe:     Kartoffelsuppe (r16687)
portions:   4
nutrition:  229 kcal per 1 Portion
steps:      6
first step: Wasser und Salz in den Mixtopf geben, …
```

Weicht die kcal-Zahl ab, wurde das Rezept bei Cookidoo geändert — dann prüfen, ob `basisUnit` weiterhin `Portion` ist und die Zahl zur Seite `https://cookidoo.de/recipes/recipe/de-DE/r16687` passt. Schlägt das Skript mit „NOBR markup survived" fehl, greift die Ersetzung in `stepsFromJson` nicht.

- [ ] **Step 5: Zweites Rezept gegenprüfen**

```bash
pnpm verify:recipe r747008
```

Erwartet: ein Rezeptname, eine Portionszahl, eine kcal-Angabe mit Bezugsgröße und mindestens ein Schritt. Der Zweck ist zu sehen, dass die Struktur nicht nur bei einem Rezept passt.

- [ ] **Step 6: Gesamte Testsuite und Build**

```bash
pnpm test
pnpm lint
pnpm build
```

Erwartet: alle drei ohne Fehler.

- [ ] **Step 7: Committen**

```bash
git add src/contexts/cookidoo/transport/mcp/tools/recipe-get-details.tool.ts \
        scripts/verify-recipe-details.ts package.json
git commit -m "feat(mcp): expose nutrition and steps in the recipe details tool"
```

---

### Task 4: Übergabe

**Files:** keine

- [ ] **Step 1: Änderungen zusammenfassen**

```bash
cd /Users/danielsteiner/Projects/cookidoo-mcp
git log --oneline main..HEAD
git diff main..HEAD --stat
```

- [ ] **Step 2: Ergebnis berichten und auf Entscheidung warten**

Berichte an Daniel:
- die drei Commits,
- die tatsächliche Ausgabe von `pnpm verify:recipe` (nicht die erwartete — die echte),
- das Resultat von `pnpm test` und `pnpm build`.

**Nicht selbstständig pushen, mergen oder deployen.** Der Connector läuft als
öffentlicher Connector in claude.ai; wann neu deployt wird, entscheidet Daniel.

---

## Self-Review

**Spec-Abdeckung (Abschnitt 4 der Spec):**

| Spec-Anforderung | Task |
|---|---|
| 4.2 `CookidooNutritionValue`, `CookidooNutrition`, Feld `nutrition` | Task 1 |
| 4.2 `CookidooRecipeStep`, Feld `steps` | Task 2 |
| 4.3 Bezugsgröße bleibt erhalten | Task 1, Step 2 (Test `keeps a per-100g basis`) |
| 4.3 Typnamen bleiben roh | Task 1, Step 2 (Test erwartet `carb2` unverändert) |
| 4.3 `nutrition` nullable | Task 1, Step 2 (zwei Null-Tests) |
| 4.3 `<NOBR>` entfernen | Task 2, Step 2 + Task 3, Step 4 (Laufzeitprüfung) |
| 4.3 Suchendpunkt unangetastet | Global Constraints; keine Task fasst ihn an |
| 4.4 Abnahme: 229 kcal und Schritte für `r16687` | Task 3, Step 4 |
| 4.4 bestehende Tests bleiben grün | Task 0 Step 2 (Ausgangslage), Task 3 Step 6 |

Keine Lücke.

**Platzhalter:** keine. Jeder Codeschritt enthält den einzusetzenden Code, jeder Testschritt den Befehl und die erwartete Ausgabe.

**Typkonsistenz:** `CookidooNutrition`, `CookidooNutritionValue`, `CookidooRecipeStep` und die Feldnamen `basisQuantity`, `basisUnit`, `values`, `type`, `number`, `unit`, `group`, `steps` sind in Tasks 1–3 identisch benannt. Die API-Felder `unittype`, `unitNotation`, `quantity`, `formattedText`, `recipeSteps`, `recipeNutritions`, `nutritionGroups`, `recipeStepGroups` sind gegen die echte Antwort von `r16687` geprüft.

**Abweichung von der Spec:** Die Spec definiert `CookidooRecipeStep` mit `{ group, text }`. Der Plan ergänzt `number`, weil die API die Schrittnummer als `title` mitliefert und sie beim Anreichern gebraucht wird („nach Schritt 3 die Sahne"). Rein additiv.
