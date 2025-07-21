from fastapi import (
    APIRouter, 
    Body,
    File,
    Form,
    Depends,
    HTTPException, 
    Request, 
    status,
    UploadFile
)
from fastapi.responses import Response
from users_auth.authentication import AuthHandler
from bson import ObjectId
from models.car_model import CarModel, CarCollectionPagination, UpdateCarModel
from pymongo import ReturnDocument
import cloudinary
from cloudinary import uploader
from config import BaseConfig


settings = BaseConfig()
router = APIRouter()
auth_handler = AuthHandler()

CARS_PER_PAGE = 10  # Number of cars per page

cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_SECRET_KEY
)

@router.post(
    "/",
    response_description="Add a new car", 
    response_model=CarModel, 
    status_code=status.HTTP_201_CREATED,
    response_model_by_alias=False
)
async def add_car_with_picture(
    request: Request, 
    brand: str = Form("brand"),
    make: str = Form("make"),
    year: int = Form("year"),
    cm3: int = Form("cm3"),
    km: int = Form("km"),
    price: int = Form("price"),
    picture: UploadFile = File("picture"),
    user: str = Depends(auth_handler.auth_wrapper)
):
    """
    Add a new car to the collection.
    
    Args:
        request (Request): The request object.
        car (CarModel): The car data to be added.
    
    Returns:
        CarModel: The added car data.
    """
    cloudinary_image = cloudinary.uploader.upload(
        picture.file,
        crop="fill",
        width=800
    )
    picture_url = cloudinary_image["url"]

    car = CarModel(
        brand=brand,
        make=make,
        year=year,
        cm3=cm3,
        km=km,
        price=price,
        picture_url=picture_url,
        user_id=user["user_id"]  # Assuming user_id is in the user dict
    )
    # Here you would typically save the car to a database
    cars = request.app.db["cars"]
    document = car.model_dump(by_alias=True, exclude=["id"])
    inserted = await cars.insert_one(document)
    # For now, we will just return the car data as is
    return await cars.find_one({"_id": inserted.inserted_id})

@router.get(
    "/",
    response_description="Get all cars",
    response_model=CarCollectionPagination,
    response_model_by_alias=False
)
async def get_all_cars(
    request: Request,
    page: int = 1,
    limit: int = CARS_PER_PAGE
):
    """
    Retrieve all cars from the collection.
    
    Args:
        request (Request): The request object.
    
    Returns:
        CarCollection: A collection of all cars.
    """
    cars = request.app.db["cars"]
    results = []
    cursor = cars.find().sort("companyName").limit(limit).skip((page - 1) * limit)
    total_documents = await cars.count_documents({})
    has_more = (page * limit) < total_documents
    async for document in cursor:
        results.append(document)
    return CarCollectionPagination(cars=results, page=page, has_more=has_more)
    # return CarCollection(cars=await cars.find().to_list(length=None))

@router.get(
    "/{car_id}",
    response_description="Get a car by ID",
    response_model=CarModel,
    response_model_by_alias=False
)
async def get_car_by_id(request: Request, car_id: str):
    """
    Retrieve a car by its ID.
    
    Args:
        request (Request): The request object.
        car_id (str): The ID of the car to retrieve.
    
    Returns:
        CarModel: The car data if found, otherwise raises 404.
    """
    cars = request.app.db["cars"]
    try:
        id = ObjectId(car_id)
    except Exception:
        raise HTTPException(status_code=404, detail="Invalid car ID format")
    if (car := await cars.find_one({"_id": ObjectId(car_id)})) is not None:
        return car
    raise HTTPException(status_code=404, detail=f"Car with {car_id} not found")

@router.put(
    "/{id}",
    response_description="Update a car",
    response_model=CarModel,
    response_model_by_alias=False
)
async def update_car(
    id: str,
    request: Request,
    user=Depends(auth_handler.auth_wrapper),
    car: UpdateCarModel = Body(...)
):
    try:
        id = ObjectId(id)
    except Exception:
        raise HTTPException(status_code=404, detail=f"Car {id} not found")
    car = {
        k: v
        for k, v in car.model_dump(by_alias=True).items()
        if v is not None and k != "_id"
    }
    if len(car) >= 1:
        cars = request.app.db["cars"]
        update_result = await cars.find_one_and_update(
            {"_id": ObjectId(id)},
            {"$set": car},
            return_document=ReturnDocument.AFTER
        )
        if update_result is not None:
            return update_result
        else:
            raise HTTPException(status_code=404, detail=f"Car {id} not found")
        
    if (existing_car := await cars.find_one({"_id": ObjectId(id)})) is not None:
        return existing_car
    
    raise HTTPException(status_code=404, detail=f"Car {id} not found")

@router.delete(
    "/{id}",
    response_description="Delete a car"
)
async def delete_car(
    id: str,
    request: Request,
    user=Depends(auth_handler.auth_wrapper)
):
    """
    Delete a car by its ID.
    
    Args:
        id (str): The ID of the car to delete.
        request (Request): The request object.
    
    Returns:
        dict: A message indicating the deletion status.
    """
    try:
        id = ObjectId(id)
    except Exception:
        raise HTTPException(status_code=404, detail=f"Car {id} not found")
    
    cars = request.app.db["cars"]
    delete_result = await cars.delete_one({"_id": ObjectId(id)})
    
    if delete_result.deleted_count == 1:
        return Response(status_code=HTTP_204_NO_CONTENT)
    
    raise HTTPException(status_code=404, detail=f"Car {id} not found")
