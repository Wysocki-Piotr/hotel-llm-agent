from langchain_core.tools import tool
from sqlalchemy import select, asc, desc
from sqlalchemy.orm import Session

from src.core.database import engine, Hotel


@tool
def search_hotels(city: str, sort_order: str = "optimal") -> str:
    """Wyszukuje hotele w podanym mieście w lokalnej bazie danych."""
    stmt = select(Hotel).where(Hotel.city == city, Hotel.is_available == True)

    if sort_order == "cheapest":
        stmt = stmt.order_by(asc(Hotel.price_per_night))
    elif sort_order == "most_expensive":
        stmt = stmt.order_by(desc(Hotel.price_per_night))

    with Session(engine) as session:
        results = session.scalars(stmt).all()
        if not results:
            return f"Nie znaleziono dostępnych hoteli w mieście {city}."

        lines = [f"Dostępne hotele w {city} ({sort_order}):"]
        for h in results:
            lines.append(f"- {h.name}: {h.price_per_night} {h.currency}")
        return "\n".join(lines)


@tool
def get_exchange_rate(source_currency: str, target_currency: str) -> float:
    """Pobiera kurs walut (mock lub live)."""
    if source_currency == target_currency: return 1.0
    # Tutaj uproszczona logika dla przejrzystości - wstaw pełną logikę scrape'owania
    fallback = {("EUR", "PLN"): 4.30, ("USD", "PLN"): 4.00, ("GBP", "PLN"): 5.20}
    return fallback.get((source_currency, target_currency), 1.0)  # Uproszczenie


@tool
def calculate_trip_cost(price_per_night: float, nights: int, exchange_rate: float, people: int) -> float:
    """Oblicza koszt całkowity."""
    return round(price_per_night * nights * exchange_rate * people, 2)


ALL_TOOLS = [search_hotels, get_exchange_rate, calculate_trip_cost]
