import asyncio
from asyncio.tasks import FIRST_COMPLETED

from loguru import logger as log

import berry_interface
import ftp_client
import parking_api
import plate_recognition


class BackgroundRunner:
    image_path: str = "/images"
    exit_sleep_time: int = 5

    def __init__(self):
        pass

    async def run_main(self):

        loop = asyncio.get_event_loop()
        plate_module = plate_recognition.PlateRecognition()
        parking_interface = parking_api.ParkingInterface()
        ftp_server = ftp_client.FTP_Client()

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

        sample_request = parking_api.CarCheckinRequest(**payload)
        bad_request = parking_api.CarCheckinRequest(**bad_payload)

        while True:
            log.debug("waiting for movement")
            entering_flag = False

            entrance_waitor = berry_interface.motion_in.wait_for_motion()
            exit_waitor = berry_interface.motion_out.wait_for_motion()
            # done, pending = loop.run_until_complete()
            singolar_waitor = asyncio.create_task(
                asyncio.wait([entrance_waitor, exit_waitor], return_when=asyncio.FIRST_COMPLETED))
            await singolar_waitor
            log.debug("pass singolar")
            done, pending = singolar_waitor.result()

            log.debug("done task count" + str(len(done)))

            for done_task in done:
                if done_task == entrance_waitor:
                    log.debug("entering... waiting exit_waitor")
                    entering_flag = True
                    await exit_waitor
                    break

            if entering_flag is False:
                log.debug("exiting.... waiting entrance awaitor")
                await entrance_waitor

            log.debug("entering flag = " + str(entering_flag))

            # connect to somewhere and get an image path
            # car_image_path = str(os.path.join(self.image_path, "0.jpg"))
            car_image_path = "0.jpg"
            # log.debug(car_image_path, os.path.dirname(os.path.realpath(__file__)))
            ftp_server.download(car_image_path)

            plate_string = plate_module.recognize_plate(car_image_path)

            log.debug(f"plate string: {plate_string}")

            car_valid_response = parking_interface.car_enter(bad_request)
            await asyncio.sleep(1)
            # if car_valid_response:
            if car_valid_response:
                berry_interface.gate.open()

                # wait for 5 seconds without movement
                # set up a timeout mechanism not
                exit_sleep_flag = True
                while exit_sleep_flag:
                    enter_waitor = berry_interface.motion_in.wait_for_motion()
                    ex_waitor = berry_interface.motion_out.wait_for_motion()
                    timer_task = asyncio.create_task(asyncio.sleep(self.exit_sleep_time))

                    singolar_waitor = asyncio.create_task(
                        asyncio.wait([enter_waitor, ex_waitor, timer_task], return_when=FIRST_COMPLETED))
                    await singolar_waitor
                    done, pending = singolar_waitor.result()
                    log.debug("passing mass waitor - exit cycle")
                    # check the done tasks
                    for t in done:
                        if t == timer_task:
                            # break the waiting and go close the door
                            log.debug("breaking the exit loop")
                            exit_sleep_flag = False
                            enter_waitor.cancel()
                            ex_waitor.cancel()

                    if enter_waitor.done() == False:
                        log.debug("in closing wait - canceling entrance")
                        entrance_waitor.cancel()
                    if ex_waitor.done() == False:
                        log.debug("in closing wait - canceling exit")
                        exit_waitor.cancel()
                    if timer_task.done() == False:
                        log.debug("in closing wait - canceling timer")
                        timer_task.cancel()

                    ex_waitor.cancel()
                    enter_waitor.cancel()
                    await asyncio.sleep(0.5)

                # if entering_flag:
                #     # car entering
                #     print(f"entering flag {entering_flag} -> waiting for exit sensor")
                #     await berry_interface.motion_out.wait_for_motion()
                #     # send something to the api, add a request retry policy or smthing
                # else:
                #     # car going out
                #     print(f"entering flag {entering_flag} -> waiting for enter sensor")
                #     await berry_interface.motion_in.wait_for_motion()
                #     # send something to the api, add a request retry policy or smthing

                berry_interface.gate.close()
            else:
                log.error("invalid response from backend")

            # end of the loop
            log.debug("<><><><><><><><><><><><><><>")
            log.debug("sleeping for 15 seconds")
            await asyncio.sleep(15)

    async def test(self):
        # todo; maybe not while true and wait for a break signal or something
        while True:
            print("waiting for movement")
            radar_waitor = berry_interface.radar.wait_for_active()

            await radar_waitor

            berry_interface.gate.open()

            await asyncio.sleep(2)

            berry_interface.gate.close()

            # todo: should config the sleep timer
            await asyncio.sleep(4)
        pass
