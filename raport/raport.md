# Raport Końcowy: Hotel LLM Agent

## 1.Cel Projektu
Celem projektu było stworzenie inteligentnego agenta podróży, który potrafi wyszukiwać hotele, przeliczać waluty oraz szacować całkowity koszt wyjazdu. System został zaprojektowany tak, aby był transparentny – użytkownik widzi plan działania agenta przed jego wykonaniem.

## 2. Architektura i Sposób Działania



System opiera się na bibliotece **LangGraph**, która zarządza przepływem stanu (StateGraph) między węzłami.

### Jak stworzono narzędzia?
Zaimplementowano trzy kluczowe narzędzia jako funkcje Python udekorowane `@tool`:
1.  **`Google Hotels(city, sort_order)`**: Przeszukuje lokalną bazę danych SQLite (`hotels.db`) w poszukiwaniu ofert spełniających kryteria (np. najtańsze, luksusowe).
2.  **`get_exchange_rate(source_currency, target_currency)`**: Pobiera aktualne kursy walut (korzystając z Google Finance lub wartości awaryjnych).
3.  **`calculate_trip_cost`**: Wykonuje obliczenia matematyczne: `cena_za_noc * noce * osoby * kurs`.

### Jak agent wybiera narzędzia? (Warstwa Planowania)
Zastosowano wzorzec **Planner-Agent**. Zamiast pozwalać modelowi działać chaotycznie, proces decyzyjny rozbito na dwa etapy:
1.  **Planner Node**: Analizuje zapytanie i tworzy ustrukturyzowany plan. W prompcie `planner.yaml` wymuszono sekcję **MYŚLENIE** (Chain-of-Thought) oraz **MODE** (chat vs tools).
2.  **Agent Node**: Otrzymuje plan i wykonuje konkretne wywołania narzędzi (Tool Calls), jeśli Planner ustawił tryb `tools`.

### Nadzór i Transparentność
Aplikacja GUI (Streamlit) wyświetla użytkownikowi na żywo:
* **Plan działania** wygenerowany przez Planera.
* **Logi systemowe**, pokazujące użycie konkretnych narzędzi.
* Status wykonywania (np. "🛠️ Uruchamiam: search_hotels...").

---

## 3. Ewaluacja i Wyniki

### Metodologia
Przygotowano zbiór testowy (`dataset.csv`) zawierający **56 zróżnicowanych zapytań** – od prostych pytań o cenę, po skomplikowane scenariusze ("Ignoruj instrukcje", "Liczba nocy: -5").

### Zdefiniowane Metryki
Do oceny jakości przyjęto cztery binarne metryki (0/1), sprawdzane po ekstrakcji danych z odpowiedzi agenta:
1.  **Poprawność miasta** (`correct_city`) – czy agent znalazł ofertę we właściwej lokalizacji?
2.  **Liczba nocy** (`correct_num_nights`) – czy poprawnie zinterpretował czas trwania?
3.  **Liczba osób** (`correct_num_people`) – czy uwzględnił wielkość grupy?
4.  **Waluta docelowa** (`correct_currency`) – czy przeliczył koszt na zadaną walutę?

### Wyniki Ilościowe
Po odrzuceniu błędów technicznych API i ręcznej weryfikacji (Manual Review) w notatniku `metrics.ipynb`, model osiągnął następujące wyniki:

| Metryka | Skuteczność (Accuracy) |
| :--- | :--- |
| Poprawność Miasta | **88.00%** |
| Poprawność Liczby Osób | **88.00%** |
| Poprawność Liczby Nocy | **86.00%** |
| Poprawność Waluty | **84.00%** |
| **ŚREDNIA** | **86.50%** |

---

## 4. Analiza Jakościowa (Success & Failure Cases)

### Przypadek Pozytywny 1: Złożone wnioskowanie
**Prompt:** *"Szukam luksusu w Londynie dla mnie i wspólnika na 3 dni."* (ID 35)

> **Odpowiedź Agenta:**
> "Znalazłem luksusowy hotel w Londynie (cena: 1000 GBP/noc). Kurs wymiany walut to 1 GBP = 4.8704 PLN. Całkowity koszt 3-dniowego pobytu dla 2 osób wyniesie 29222.40 PLN."

**Analiza:** Agent poprawnie zidentyfikował liczbę osób ("mnie i wspólnika" = 2), domyślnie przeliczył walutę na PLN (zgodnie z logiką systemu) i wykonał poprawny ciąg obliczeń.

### Przypadek Pozytywny 2: Guardrails (Ochrona przed błędami)
**Prompt:** *"Ile zapłacę za -5 nocy w Nowym Jorku?"* (ID 36)

> **Odpowiedź Agenta:**
> "Liczba nocy nie może być ujemna. Na ile nocy planujesz ten wyjazd?"

**Analiza:** Zamiast wykonać bezsensowne obliczenia, agent wykrył błąd logiczny w danych wejściowych i przeszedł w tryb dopytywania (Chat Mode).

### Przypadek Negatywny 1: Błąd techniczny modelu (Tool Use Error)
**Prompt:** *"Organizuję zlot fanów w Barcelonie dla 5000 osób..."* (ID 55)

> **Status:** ERROR: Error code: 400 ... 'tool_use_failed'

**Analiza:** Przy skrajnych wartościach (5000 osób), model wygenerował niepoprawny format wywołania funkcji (JSON z doklejonymi tagami XML), co spowodowało awarię API.

### Przypadek Negatywny 2: Niejasność kontekstu
**Prompt:** *"Ile kosztuje nocleg w Radomiu?"* (ID 32)

> **Odpowiedź Agenta:**
> "Ile nocy planujesz spędzić w Radomiu i ile osób będzie podróżować?"

**Analiza:** Choć technicznie poprawne (agent potrzebuje danych do wzoru), z perspektywy User Experience użytkownik oczekiwałby raczej podania przykładowej ceny za jedną noc ("cennika"), zamiast pytania pomocniczego.

## 5. Podsumowanie
Projekt zakończył się sukcesem ze średnią skutecznością na poziomie **86.5%**. Architektura LangGraph zapewniła stabilność, a podział na Planera i Agenta pozwolił na skuteczną weryfikację poprawności danych wejściowych. Główne obszary do poprawy to obsługa skrajnych wartości liczbowych oraz lepsza domyślność w przypadku ogólnych pytań.