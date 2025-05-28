from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.api.schemas import RestCountryResponse
from src.database.models import Country
from src.exceptions.custom_exceptions import DatabaseError


class CountryRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_country_by_code(self, code: str):
        country = self.db.query(Country).filter(Country.code == code).first()
        return country

    def create_country(self, **kwargs) -> Country:
        try:
            country = Country(**kwargs)
            self.db.add(country)
            self.db.commit()
            return country
        except SQLAlchemyError as e:
            self.db.rollback()
            raise DatabaseError(f"Database error while creating country: {str(e)}")

    def create_country_from_rest(self, rest_country: RestCountryResponse) -> Country:
        try:
            country_data = rest_country.to_country_data()
            return self.create_country(**country_data)
        except SQLAlchemyError as e:
            raise DatabaseError(
                f"Database error while mapping REST country data: {str(e)}"
            )
        except Exception as e:
            raise DatabaseError(
                f"Unexpected error while mapping REST country data: {str(e)}"
            )
