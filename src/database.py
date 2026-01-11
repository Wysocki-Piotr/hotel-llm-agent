from sqlalchemy import create_engine, String, Float, Integer, select, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session
import random

DATABASE_URL = "sqlite:///data/hotels.db"
engine = create_engine(DATABASE_URL)

class Base(DeclarativeBase):
    pass

class Hotel(Base):
    __tablename__ = "hotels"

    id: Mapped[int] = mapped_column(primary_key=True)
    city: Mapped[str] = mapped_column(String(50))
    name: Mapped[str] = mapped_column(String(100))
    price_per_night: Mapped[float] = mapped_column(Float)
    currency: Mapped[str] = mapped_column(String(10), default="EUR")
    is_available: Mapped[bool] = mapped_column(Boolean, default=True)

    def __repr__(self):
        return f"<Hotel(city='{self.city}', name='{self.name}', price={self.price_per_night} {self.currency})>"
    
def get_initial_hotels():
    cities_data = {
        "Barcelona": ("EUR", [
            ("Hostel Hola", 45), ("W Barcelona", 420), ("Hotel Arts", 350), 
            ("ibis Styles", 120), ("Majestic Hotel", 290), ("Generator BCN", 50),
            ("Novotel City", 160), ("H10 Marina", 140)
        ]),
        "Paris": ("EUR", [
            ("Le Meurice", 800), ("Ibis Tour Eiffel", 150), ("Ritz Paris", 1200),
            ("Mama Shelter", 130), ("Hotel Henriette", 180), ("Pullman Bercy", 210),
            ("Le Bristol", 950)
        ]),
        "London": ("GBP", [
            ("The Savoy", 600), ("Generator Hostel", 40), ("The Ritz London", 750),
            ("Premier Inn Hub", 90), ("Shangri-La The Shard", 850), ("Strand Palace", 220),
            ("Travelodge Central", 60), ("Claridge's", 900)
        ]),
        "New York": ("USD", [
            ("The Plaza", 900), ("Pod 51", 120), ("Empire Hotel", 250),
            ("Wythe Hotel", 350), ("The Standard", 400), ("YOTEL Times Square", 160),
            ("Ace Hotel", 280), ("Waldorf Astoria", 1100)
        ]),
        "Tokyo": ("JPY", [
            ("Park Hyatt", 85000), ("APA Hotel", 12000), ("Hoshinoya", 110000),
            ("Capsule Inn", 4000), ("Shinjuku Prince", 18000), ("Imperial Hotel", 60000)
        ]),
        "Berlin": ("EUR", [
            ("Hotel Adlon", 450), ("Motel One", 90), ("Soho House", 320),
            ("Michelberger", 110), ("Radisson Collection", 200), ("EasyHotel", 60)
        ]),
        "Warsaw": ("PLN", [
            ("Raffles Europejski", 1200), ("Marriott", 600), ("Novotel Centrum", 350),
            ("Ibis Budget", 180), ("Bristol", 900), ("InterContinental", 700),
            ("Puro Hotel", 450)
        ]),
        "Rome": ("EUR", [
            ("Hotel Eden", 800), ("YellowSquare Hostel", 55), ("Hassler Roma", 950),
            ("Hotel Artemide", 250), ("NH Collection", 300)
        ])
    }

    hotels_list = []
    
    for city, (currency, hotels) in cities_data.items():
        for name, price in hotels:
            is_avail = random.random() < 0.8
            hotels_list.append(Hotel(
                city=city,
                name=name,
                price_per_night=float(price),
                currency=currency,
                is_available=is_avail
            ))
            
    return hotels_list
    
def init_db():
    Base.metadata.create_all(engine)
    
    with Session(engine) as session:
        if session.query(Hotel).first() is None:
            hotels = get_initial_hotels()
            session.add_all(hotels)
            session.commit()
            print(f"Dodano {len(hotels)} hoteli do bazy 'travel.db'.")
        else:
            print("Baza 'travel.db' już zawiera dane.")


def list_available_hotels(city: str):
    with Session(engine) as session:
        stmt = select(Hotel).where(Hotel.city == city, Hotel.is_available == True)
        result = session.scalars(stmt).all()
        return result

if __name__ == "__main__":
    init_db()
    test_city = "Barcelona"
    print(f"\n--- Dostępne hotele w {test_city}: ---")
    available = list_available_hotels(test_city)
    for h in available:
        print(f"- {h.name}: {h.price_per_night} {h.currency}")
        
    print(f"\nŁącznie w bazie: {len(available)} dostępnych w tym mieście.")