import sys
from qasync import QEventLoop, QApplication
from gui_assets.main_gui import *
from widgets.functions.getapps import get_apps
from server import *
from threading import Thread
from widgets.spotify_widget.tempwebserver import app as flask_app

def run_flask():
    #Run the Flask server
    try:
        flask_app.run(port=2266, debug=False, use_reloader=False)  # Disable reloader to avoid duplicate threads
    except Exception as e:
        print(f"Flask server error: {e}")

async def start_server():
    #start the websockets server task
    await main_server()


async def run_everything():
    #start the websocket server task in the asyncio loop without blocking
    asyncio.create_task(start_server())


def main():
    #initialize the app and loop

    flask_thread = Thread(target=run_flask, daemon=True)
    flask_thread.start()

    app = QApplication(sys.argv)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)  #set the asyncio event loop

    #initialize the MainWindow
    window = MainWindow()
    window.show()
    window.init()

    #run additional tasks within the asyncio loop
    loop.create_task(run_everything())  #start the server task

    #start the event loop for both asyncio and PyQt
    with loop:
        get_apps()  #run get_apps to retrieve app information
        loop.run_forever()  #start the combined asyncio and PyQt event loop


if __name__ == "__main__":
    main()
