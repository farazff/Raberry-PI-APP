import asyncio
from gpiozero import DigitalInputDevice
import berry_interface
# from time import sleep


# radar_in = DigitalInputDevice(18, pull_up=False, bounce_time=2.0)
# radar_out = DigitalInputDevice(17, pull_up=False, bounce_time=2.0)


# def detector():
#         print("got some motion innnn in in in\t\t" + radar_in.value) 

# def out_detect():
#         print("out detected\t\t" + radar_out.value)



# radar_in.when_activated = detector
# radar_out.when_activated = out_detect

# async def main():
#     while True:
#         print("new cycle..." + (radar_in.value, radar_out.value))
#         if radar_out.value == 1:
#             print("out detected")

#         if radar_in.value == 1:
#             print("in detected")
        # await asyncio.sleep(1)


r = berry_interface.radar

async def foo():
    while True:
        print("waiting")
        waitor =  r.wait_for_active()

        await waitor

        await asyncio.sleep(4)
        pass
    pass

asyncio.run(foo())
