from typing import List, Optional

from pydantic import BaseModel


class CountryBase(BaseModel):
    code: str
    name: str
    full_name: str
    region: str
    subregion: str
    independent: bool
    google_maps_url: Optional[str] = None
    open_street_map_url: Optional[str] = None
    capital_name: str
    capital_latitude: float
    capital_longitude: float
    flag_png_url: str
    flag_svg_url: str
    flag_alt: str
    coat_of_arms_png_url: Optional[str] = None
    coat_of_arms_svg_url: Optional[str] = None
    borders: str

    class Config:
        from_attributes = True


class CountryDTO(CountryBase):
    """DTO для преобразования модели Country в данные API."""
    pass


class RestCountryResponse(BaseModel):
    name: dict
    region: str
    subregion: str
    independent: bool
    maps: dict
    capital: List[str]
    capitalInfo: dict
    flags: dict
    coatOfArms: dict
    borders: Optional[List[str]] = None
    code: str

    class Config:
        from_attributes = True
        extra = "allow"

    def to_country_data(self) -> dict:
        return {
            "code": self.code,
            "name": self.name.get("common"),
            "full_name": self.name.get("official"),
            "region": self.region,
            "subregion": self.subregion,
            "independent": self.independent,
            "google_maps_url": self.maps.get("googleMaps"),
            "open_street_map_url": self.maps.get("openStreetMaps"),
            "capital_name": self.capital[0] if self.capital else None,
            "capital_latitude": self.capitalInfo.get("latlng", [None, None])[0],
            "capital_longitude": self.capitalInfo.get("latlng", [None, None])[1],
            "flag_png_url": self.flags.get("png"),
            "flag_svg_url": self.flags.get("svg"),
            "flag_alt": self.flags.get("alt"),
            "coat_of_arms_png_url": self.coatOfArms.get("png"),
            "coat_of_arms_svg_url": self.coatOfArms.get("svg"),
            "borders": ",".join(self.borders) if self.borders else "(island)"
        }


class NameCountryResponse(BaseModel):
    name: str
    country: CountryDTO
    probability: float

    class Config:
        from_attributes = True
