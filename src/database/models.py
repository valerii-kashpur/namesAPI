from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from src.database.db import Base


class Name(Base):
    __tablename__ = "names"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    count_of_requests = Column(Integer, default=0)
    last_accessed_at = Column(DateTime(timezone=True), nullable=False)
    countries = relationship("NameCountry", back_populates="name")


class Country(Base):
    __tablename__ = "countries"
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True)
    name = Column(String)
    full_name = Column(String)
    region = Column(String)
    subregion = Column(String)
    independent = Column(Boolean)
    google_maps_url = Column(String, nullable=True)
    open_street_map_url = Column(String, nullable=True)
    capital_name = Column(String)
    capital_latitude = Column(Float)
    capital_longitude = Column(Float)
    flag_png_url = Column(String)
    flag_svg_url = Column(String)
    flag_alt = Column(String)
    coat_of_arms_png_url = Column(String, nullable=True)
    coat_of_arms_svg_url = Column(String, nullable=True)
    borders = Column(String)
    names = relationship("NameCountry", back_populates="country")


class NameCountry(Base):
    __tablename__ = "name_country"
    id = Column(Integer, primary_key=True, index=True)
    name_id = Column(Integer, ForeignKey("names.id"))
    country_id = Column(Integer, ForeignKey("countries.id"))
    probability = Column(Float)
    name = relationship("Name", back_populates="countries")
    country = relationship("Country", back_populates="names")


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
