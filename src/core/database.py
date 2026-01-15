from sqlalchemy import create_engine, String, Float, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session

from src.core.config import config

engine = create_engine(config.db_url)


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


def init_db():
    """Tworzy tabele i seeduje dane jeśli baza jest pusta."""
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        if session.query(Hotel).first() is None:
            _seed_data(session)


def _seed_data(session: Session):
    # Skrócona wersja seedowania dla czytelności - tu wstaw dane z oryginalnego pliku
    cities_data = {
        "Barcelona": ("EUR", [("Hostel Hola", 45), ("W Barcelona", 420)]),
        "Paris": ("EUR", [("Le Meurice", 800), ("Ibis Tour Eiffel", 150)]),
        "Warsaw": ("PLN", [("Bristol", 900), ("Novotel", 350)]),
        # ... reszta miast
    }
    for city, (curr, hotels) in cities_data.items():
        for name, price in hotels:
            session.add(Hotel(city=city, name=name, price_per_night=float(price), currency=curr))
    session.commit()
    print("Zainicjalizowano bazę danych.")
