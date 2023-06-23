import asyncio
from asyncio.tasks import Task

import gpiozero
from loguru import logger


class Gate:
    # todo: gate logic, checking the previous state and stuff
    pin: int

    relay: gpiozero.OutputDevice = None

    state: bool = False

    def __init__(self, pin) -> None:
        self.pin = pin
        try:
            self.relay = gpiozero.OutputDevice(self.pin, active_high=False, initial_value=False)
        except Exception as e:
            print("error loading gate")
            logger.warning("gate device not made, probably pin is in use")
            logger.exception(e)

    def open(self) -> None:
        # open only if the gate is closed
        if self.relay is not None and self.state is False:
            logger.info("gate is being opened")
            self.state = True
            self.relay.on()

    def close(self) -> None:
        # close only if the gate is already opened
        if self.relay is not None and self.state is True:
            logger.info("gate is being closed")
            self.state = False
            self.relay.off()

    def get_state(self) -> bool:
        return self.state


class MotionSensor:
    pin: int
    queue_len: int = 1
    sample_rate: float = 10
    threshold: float = 0.5

    device: gpiozero.MotionSensor = None

    def __init__(self, pin) -> None:
        self.pin = pin
        try:
            self.device = gpiozero.MotionSensor(self.pin,
                                                queue_len=self.queue_len,
                                                sample_rate=self.sample_rate,
                                                threshold=self.threshold)
        except Exception as e:
            print("error loading motion sensor")
            logger.warning("motion sensor not made, probably pins are in use")
            logger.exception(e)

    async def _device_wait(self):
        logger.debug(F"sensor is on a wait -> {self.pin}")
        # todo: should have a break signal
        while True:
            if self.device.value == 1:
                logger.debug(F"breaking the sensor wait -> {self.pin}")
                break
            logger.debug(f"{self.pin}::::cycle...")
            await asyncio.sleep(2)
        return

    def wait_for_motion(self) -> Task:
        if self.device is None:
            return
        else:
            logger.debug(f'created motion waiting task {self.pin}')
            task = asyncio.create_task(self._device_wait())
            return task


class LED:
    pin: int
    device: gpiozero.LED
    state: bool = False

    def __init__(self, pin) -> None:
        self.pin = pin
        self.state = False
        try:
            self.device = gpiozero.LED(pin=pin, initial_value=False)
        except Exception as e:
            logger.warning("gate device not made, probably pin is in use")
            logger.exception(e)
        pass

    def on(self):
        if self.device is not None:
            self.state = True
            self.device.on()

    def off(self):
        if self.device is not None:
            self.state = False
            self.device.off()

    def get_state(self) -> bool:
        return self.state


# instances

motion_in = MotionSensor(pin=17)
motion_out = MotionSensor(pin=18)
gate = Gate(pin=23)
