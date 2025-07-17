from typing import Optional, List, Annotated
from pydantic import BaseModel, Field, ConfigDict, BeforeValidator, field_validator


PyObjectId = Annotated[str, BeforeValidator(str)]

class CarModel(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    brand: str = Field(..., description="Brand of the car")
    make: str = Field(..., description="Make of the car")
    year: int = Field(..., gt=1970, lt=2025, description="Year of manufacture")
    cm3: int = Field(..., gt=0, lt=5000, description="Engine displacement in cubic centimeters")
    km: int = Field(..., gt=0, lt=500000, description="Kilometers driven")
    price: int = Field(..., gt=0, lt=100000, description="Price of the car in currency units")

    @field_validator("brand")
    @classmethod
    def check_brand_case(cls, value: str) -> str:
        """Ensure brand is in uppercase."""
        return value.title()
    
    @field_validator("make")
    @classmethod
    def check_make_case(cls, value: str) -> str:
        """Ensure make is in uppercase."""
        return value.title()
    
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "brand": "Toyota",
                "make": "Corolla",
                "year": 2020,
                "cm3": 1800,
                "km": 30000,
                "price": 20000
            }
        }
    )

class UpdateCarModel(BaseModel):
    brand: Optional[str] = Field(...)
    make: Optional[str] = Field(...)
    year: Optional[int] = Field(..., gt=1970, lt=2025)
    cm3: Optional[int] = Field(..., gt=0, lt=5000)
    km: Optional[int] = Field(..., gt=0, lt=500000)
    price: Optional[int] = Field(..., gt=0, lt=100000)

class CarCollection(BaseModel):
    cars: List[CarModel]

# test_car = CarModel(
#     brand="toyota",
#     make="corolla",
#     year=2020,
#     cm3=1800,
#     km=30000,
#     price=20000
# )
# print(test_car)