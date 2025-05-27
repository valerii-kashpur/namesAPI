from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from src.database.models import Name, NameCountry


class NameRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_or_create_name(self, name: str) -> Name:
        name_record = self.db.query(Name).filter(Name.name == name).first()
        if name_record:
            name_record.count_of_requests += 1
            name_record.last_accessed_at = datetime.utcnow()
        else:
            name_record = Name(name=name, count_of_requests=1, last_accessed_at=datetime.utcnow())
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
