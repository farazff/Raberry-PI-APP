from fastapi import FastAPI, Request
from starlette.routing import Host, Match
import berry_interface
import plate_recognition
import parking_api
import auth as ah
import asyncio
from runner import BackgroundRunner
from loguru import logger
from custom_logging import LogConfig
import uvicorn

temp_path = ""

app = FastAPI()

plate_module = plate_recognition.PlateRecognition()
parking_interface = parking_api.ParkingInterface()

runner = BackgroundRunner()

@app.on_event('startup')
async def app_startup():
    startup_led = berry_interface.LED(20)
    startup_led.on()
    await asyncio.sleep(10)
    asyncio.create_task(runner.run_main())
    log_config = LogConfig()
    logger.configure(**log_config.get_logging_config())
    logger.info("---cstart up---")
    pass

#todo: add shutdown event and closing ftp

# logging middleware to log http events
@app.middleware("http")
async def log_middle(request: Request, call_next):
    logger.debug(f"{request.method} {request.url}")
    routes = request.app.router.routes
    logger.debug("Params:")
    for route in routes:
        match, scope = route.matches(request)
        if match == Match.FULL:
            for name, value in scope["path_params"].items():
                logger.debug(f"\t{name}: {value}")
    logger.debug("Headers:")
    for name, value in request.headers.items():
        logger.debug(f"\t{name}: {value}")

    response = await call_next(request)
    return response

# Parking Api
@app.post("/parking/car-enter")
async def get_car_enter_response(request: parking_api.CarCheckinRequest,current_user: ah.User = ah.Depends(ah.get_current_active_user)):
    return parking_interface.car_enter(request)


# Config

@app.get("/conf/plate-recongnition")
async def get_plate_conf() -> plate_recognition.PlateRecognitionConfig:
    return plate_module.get_config()

@app.post("/conf/plate-recongnition")
async def set_plate_conf(config: plate_recognition.PlateRecognitionConfig) -> plate_recognition.PlateRecognitionConfig:
    plate_module.load_config(config)
    return plate_module.get_config()

# Gate
@app.get("/gate/state")
async def get_gate_state(current_user: ah.User = ah.Depends(ah.get_current_active_user)):
    return berry_interface.gate.get_state()


@app.post("/gate/open")
async def gate_open(current_user: ah.User = ah.Depends(ah.get_current_active_user)):
    berry_interface.gate.open()
    return berry_interface.gate.get_state()


@app.post("/gate/close")
async def gate_open(current_user: ah.User = ah.Depends(ah.get_current_active_user)):
    berry_interface.gate.close()
    return berry_interface.gate.get_state()

app.mount("/auth", ah.authapi)

if __name__ == "__main__":
    try:
        uvicorn.run("server:app", host="localhost", port=8000, log_level="info")
    except Exception as e:
        logger.exception(e)
