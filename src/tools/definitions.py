from langchain_core.tools import tool
from bs4 import BeautifulSoup
import requests
from sqlalchemy import select, asc, desc
from sqlalchemy.orm import Session

from src.core.database import engine, Hotel


@tool
def search_hotels(city: str, sort_order: str = "optimal") -> str:
    """
    Wyszukuje hotele w podanym mieście w lokalnej bazie danych.
    
    Args:
        city: Nazwa miasta (np. 'Warsaw', 'Paris').
        sort_order: Sposób sortowania: 'cheapest' (najtańsze), 'most_expensive' (najdroższe), 
                    lub 'optimal' (domyślne/bez sortowania).
    """
    stmt = select(Hotel).where(Hotel.city == city, Hotel.is_available == True)

    if sort_order == "cheapest":
        stmt = stmt.order_by(asc(Hotel.price_per_night))
    elif sort_order == "most_expensive":
        stmt = stmt.order_by(desc(Hotel.price_per_night))

    with Session(engine) as session:
        results = session.scalars(stmt).all()
        
        if not results:
            return f"Nie znaleziono dostępnych hoteli w mieście {city}."

        response_lines = [f"Dostępne hotele w {city} ({sort_order}):"]
        for hotel in results:
            response_lines.append(f"- {hotel.name}: {hotel.price_per_night} {hotel.currency}")
            
        return "\n".join(response_lines)



@tool
def get_exchange_rate(source_currency: str, target_currency: str) -> float:
    """
    Pobiera aktualny kurs wymiany walut ze strony Google Finance.
    
    Args:
        source_currency: Kod waluty źródłowej (np. 'EUR').
        target_currency: Kod waluty docelowej (np. 'PLN').
    """
    if source_currency == target_currency:
        return 1.0

    url = f"https://www.google.com/finance/quote/{source_currency}-{target_currency}"
    
    try:
        response = requests.get(url)
        response.raise_for_status() 
        
        soup = BeautifulSoup(response.text, "html.parser")

        price_div = soup.find("div", class_="YMlKec fxKbKc")
        
        if not price_div:
            price_div = soup.find("div", {"data-last-price": True})
            if price_div:
                return float(price_div["data-last-price"])
            else:
                raise ValueError("Nie znaleziono elementu z ceną na stronie.")

        return float(price_div.text.replace(",", ""))

    except Exception as e:
        print(f"Błąd pobierania kursu: {e}. Używam kursu awaryjnego.")
        fallback_rates = {
            ("EUR", "PLN"): 4.30,
            ("USD", "PLN"): 4.00,
            ("GBP", "PLN"): 5.15,
            ("JPY", "PLN"): 0.027,
            ("PLN", "EUR"): 0.23,
            ("PLN", "USD"): 0.25
        }
        return fallback_rates.get((source_currency, target_currency), 1.0)

@tool
def calculate_trip_cost(price_per_night: float, nights: int, exchange_rate: float, people: int) -> float:
    """
    Oblicza całkowity koszt wyjazdu w walucie docelowej.
    
    Args:
        price_per_night: Cena za jedną noc.
        nights: Liczba nocy.
        exchange_rate: Kurs waluty.
        people: Liczba osób do rezerwacji.
    """
    return round(price_per_night * nights * exchange_rate * people, 2)


ALL_TOOLS = [search_hotels, get_exchange_rate, calculate_trip_cost]
