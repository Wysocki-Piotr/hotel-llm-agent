import csv
import random

CITIES = ["Barcelona", "Paris", "London", "New York", "Tokyo", "Berlin", "Warsaw", "Rome"]
TARGET_CURRENCIES = ["PLN", "EUR", "USD", "GBP", "JPY"]

SORTS_MAPPING = {
    "najtańszy": "cheapest",
    "tani": "cheapest",
    "ekonomiczny": "cheapest",
    "budżetowy": "cheapest",

    "najdroższy": "most_expensive",
    "luksusowy": "most_expensive",
    "ekskluzywny": "most_expensive",

    "dobry": "optimal",
    "polecany": "optimal",
    "przyzwoity": "optimal",
    "standardowy": "optimal",
    "średni": "optimal"
}

TEMPLATES = [
    "Ile zapłacę za {nights} nocy dla {people} osób w mieście {city}? Wynik w {currency}.",
    "Szukam noclegu w {city}. Interesuje mnie standard: {sort_adj}. {nights} noce, {people} osoby. Podaj cenę w {currency}.",
    "Jaki jest koszt pobytu w {city} (hotel: {sort_adj}) dla {people} gości na {nights} dni? Przelicz na {currency}.",
    "Planuję wyjazd do {city} na {nights} nocy. Jedziemy w {people} osób. Ile to wyjdzie w {currency}?",
    "Potrzebuję wyceny hotelu ({sort_adj}) w {city} dla {people} dorosłych na {nights} noclegów. Waluta docelowa: {currency}.",
    "Czy znajdziesz {sort_adj} nocleg w {city}? Pobyt: {nights} noce, Liczba osób: {people}. Podaj kwotę w {currency}.",
    "Ile kosztuje {nights}-dniowy pobyt w {city} dla {people} osobowej rodziny? Celuję w {sort_adj} standard. Cena w {currency}.",
    "Sprawdź ceny w {city} ({sort_adj}). {nights} nocy i {people} osoby. Przelicz na {currency}."
]

def generate_csv(filename="data/dataset.csv", num_rows=30):
    header = ["id", "prompt", "city", "sort_order", "num_nights", "num_people", "target_currency"]
    
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(header)
        
        print(f"Generowanie {num_rows} przykładów...")
        
        for i in range(1, num_rows + 1):
            city = random.choice(CITIES)
            target_currency = random.choice(TARGET_CURRENCIES)
            nights = random.randint(1, 14) 
            people = random.randint(1, 6) 
  
            sort_adj = random.choice(list(SORTS_MAPPING.keys()))
            sort_tech = SORTS_MAPPING[sort_adj]

            template = random.choice(TEMPLATES)
            prompt = template.format(
                city=city,
                nights=nights,
                people=people,
                currency=target_currency,
                sort_adj=sort_adj
            )

            writer.writerow([i, prompt, city, sort_tech, nights, people, target_currency])

    print(f"   Zawiera {num_rows} wygenerowanych wierszy.")

if __name__ == "__main__":
    generate_csv()