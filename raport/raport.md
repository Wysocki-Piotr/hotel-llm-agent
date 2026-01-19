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

## 4. Analiza Przypadków (przykłady)

## Sukcesy

### Przypadek 1 – Dopytywanie o brakujące dane
Agent wykrywa brak kluczowych informacji (liczba nocy, liczba osób) i zamiast wykonywać obliczenia przechodzi w tryb konwersacyjny, prosząc użytkownika o doprecyzowanie danych.

![Dopytywanie o dane](images/dopytywanie.png)

---

### Przypadek 2 – Tryb konwersacyjny (small talk)
System poprawnie rozpoznaje zapytanie, które nie wymaga użycia narzędzi, i odpowiada w trybie czatu, bez uruchamiania warstwy obliczeniowej.

![Tryb czatu](images/hej.png)

---

### Przypadek 3 – nie na temat
Agent rozpoznaje, że użytkownik pyta go o zagadnienia nie związane z jego zadaniem i konsekwentnie trzyma się zaplanowanego trybu działania.

![nie na teamt](images/niebieski.png)

### Przypadek 4 – Zapytanie, które nie jest defaultowe
Zapytanie miało na celu przetestowanie czy agent jest w stanie wywołać tylko jedną funkcję (przeszukanie bazy danych). Wykonane poprawnie, nie wywołał przelicznika walut.

![Dopytywanie o dane](images/TylkoJednaFunkcja.png)

### Przypadek 5 – Nietypowe sformułowanie pytania
Zapytanie miało na celu przetestowanie czy agent wymyśli jakieś miasto niedaleko plaży czy dopyta o konkret. Dopytał o miasto.

![Dopytywanie o dane](images/Konkret-BrakHalucynacji.png)

## Porażki 

### Przypadek 1 - zignoruj instrukcje

agent po otzrymaniu polecenia zignoruj dotychczasowe instrukcje niestety odchodzi od swojego zadania

![zignoruj instrukcje](images/zignoruj_instrukcje.png)

### Przypadek 2 – Zapytanie o nieistniejące miasto
Zapytanie o miasto, które nie istnieje w bazie. Agent poprawnie ustalił, że go nie ma, ale następnie zaproponował miasta, których też nie ma w bazie. Dopiero po dalszym użytkownika wyszukał, że nie ma hotelu w innym mieście.

![Dopytywanie o dane](images/PodchwytliweMiasto.png)

### Przypadek 3 – Nietypowe zadanie matematyczne
Test miał na celu sprawdzić jak agent zinterpretuje nietypowe sformułowanie matematyczne. Popełnił błąd jednak już wcześniej - przekazał do funkcji złą nazwę miasta - polską, a nie angielską.

![Dopytywanie o dane](images/HalucynacjaLondonLondyn.png)


## Alternatywny model

Powyższą analizę przeprowadziliśmy dla dla modelu 'llama-3.3-70b-versatile' jednak przetestowaliśmy także mniejszy model 'gpt-oss-20b'
Niestety ten model już gorzej radził sobie z wykorzystywaniem narzędzi.

![gpt20](images/gpt20.png)

Jednak po dopytaniu potrafił poprawnie ich użyć.

![gpt20_powrót ](images/gpt20_powrót.png)

## 5. Podsumowanie

Projekt zakończył się sukcesem ze średnią skutecznością na poziomie **86.5%**. Architektura LangGraph zapewniła stabilność, a podział na Planera i Agenta pozwolił na skuteczną weryfikację poprawności danych wejściowych. Główne obszary do poprawy to obsługa skrajnych wartości liczbowych oraz lepsza domyślność w przypadku ogólnych pytań.




