from car_model import CarModel, UpdateCarModel, CarCollection


test_car_1 = CarModel(
    brand="toyota",
    make="corolla",
    year=2020,
    cm3=1800,
    km=30000,
    price=20000
)
test_car_2 = CarModel(
    brand="honda",
    make="civic",
    year=2019,
    cm3=1600,
    km=25000,
    price=18000
)
car_list = CarCollection(cars=[test_car_1, test_car_2])
print(car_list.model_dump())