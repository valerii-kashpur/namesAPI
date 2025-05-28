from datetime import datetime, timedelta

from sqlalchemy.exc import SQLAlchemyError, DatabaseError
from sqlalchemy.orm import Session

from src.database.models import Name, NameCountry, Country
from src.utils.normalize import normalize_name


class NameRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_or_create_name(self, name: str) -> Name:
        normalized_name = normalize_name(name)
        name_record = self.db.query(Name).filter(Name.name == normalized_name).first()
        if name_record:
            name_record.count_of_requests += 1
            name_record.last_accessed_at = datetime.utcnow()
        else:
            name_record = Name(
                name=normalized_name,
                count_of_requests=1,
                last_accessed_at=datetime.utcnow()
            )
            self.db.add(name_record)
        self.db.commit()
        return name_record

    def get_name_countries(self, name_id: int, days_threshold: int = 1) -> list[NameCountry]:
        name = self.db.query(Name).filter(Name.id == name_id).first()
        if not name:
            return []
        if name.last_accessed_at > datetime.utcnow() - timedelta(days=days_threshold):
            return self.db.query(NameCountry).filter(NameCountry.name_id == name_id).all()
        return []

    def add_name_country(self, name_id: int, country_id: int, probability: float):
        name_country = NameCountry(name_id=name_id, country_id=country_id, probability=probability)
        self.db.add(name_country)
        self.db.commit()

    def get_popular_names_by_country(self, country_code: str) -> list:
        try:
            result = (
                self.db.query(Name)
                .join(NameCountry, Name.id == NameCountry.name_id)
                .join(Country, NameCountry.country_id == Country.id)
                .filter(Country.code == country_code)
                .order_by(Name.count_of_requests.desc())
                .limit(5)
                .all()
            )
            return result
        except SQLAlchemyError as e:
            raise DatabaseError(f"Database error while fetching popular names for country {country_code}: {str(e)}")
