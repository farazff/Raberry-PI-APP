import requests
from loguru import logger as log
from pydantic import BaseModel


class ParkingApiConfig(BaseModel):
    pass


class CarCheckinRequest(BaseModel):
    plate_first: str
    plate_middle: str
    plate_last: str
    plate_global: str
    # token: str


class CarInRequest(BaseModel):
    carId: int


# class EmptySlotRequest(BaseModel):
#     floor: int
#     token: str


# class ZoneChangeRequest(BaseModel):
#     zone_id: int
#     zone_changed: bool
#     zone_counter: int
#     token: str

class ParkingInterface():
    endpoint_base: str = "http://94.101.189.230:65432/"
    endpoints: dict = {
        "car_enter": "car-entered",  # post

    }

    def __init__(self) -> None:
        pass

    # todo: response
    def car_enter(self, model: CarCheckinRequest) -> bool:
        # method: post
        try:
            response = requests.post(self.endpoint_base + self.endpoints['car_enter'], data=model.__dict__)
            print(self.endpoints['car_enter'] + "responded: -->" + str(response.status_code))
            if response.status_code == 200:
                return True
            else:
                return False
        except Exception as e:
            log.exception(e)
        pass


if __name__ == "__main__":
    interface = ParkingInterface()
    payload = {
        'plate_first': '11',
        'plate_middle': 'ب',
        'plate_last': '265',
        'plate_global': '26'
    }

    bad_payload = {
        'plate_first': '44',
        'plate_middle': 'ب',
        'plate_last': '265',
        'plate_global': '26'
    }

    sample_request = CarCheckinRequest(**payload)
    bad_request = CarCheckinRequest(**bad_payload)
    res = interface.car_enter(sample_request)

    print(res)

    print(interface.car_enter(bad_request))
