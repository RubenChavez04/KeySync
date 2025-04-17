from pi_code.main_gui_pi import *
from pi_code.pi_client import *
import sys
import asyncio
from qasync import QApplication, QEventLoop



async def start_client():
    #start the websockets server task
    await websocket_client()


async def run_everything():
    #start the websocket server task in the asyncio loop without blocking
    asyncio.create_task(start_client())


def main():
    #initialize the client app and loop
    app = QApplication(sys.argv)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)  #set the asyncio event loop

    #initialize the MainWindow
    window = MainWindow()
    window.show()

    #run additional tasks within the asyncio loop
    loop.create_task(run_everything())  #start the server task

    #start the event loop for both asyncio and PyQt
    with loop:
        loop.run_forever()  #start the combined asyncio and PyQt event loop


if __name__ == "__main__":
    main()