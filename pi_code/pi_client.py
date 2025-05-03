import asyncio
import websockets
import os
from pi_code.signal_dispatcher_pi import pi_signal_dispatcher
import time

server_address = "ws://10.0.6.190:1738"
save_path = "pi_assets"
save_path_button = "pi_assets/button_images"
files_updated = False
websocket_connection = None
spotify_updated = False
weather_updated = False
buttons_updated = False
initial_page_load = False

async def receive_file(websocket):
    global websocket_connection
    global initial_page_load
    if websocket_connection is not None:
        try:
            while True:
                incoming = await websocket.recv()
                if "json?" in incoming:
                    await send_message("json")
                if "progress" in incoming:
                    pi_signal_dispatcher.update_spotify_progress.emit(incoming)
                else:
                    file_name = incoming
                    print(f"Receiving file: {file_name}")
                    if file_name.endswith((".jpg",".png",".svg",".ico",".jpeg",".gif")):
                        os.makedirs(save_path_button, exist_ok=True)
                        file_path = os.path.join(save_path_button, file_name)
                    else:
                        os.makedirs(save_path, exist_ok=True)
                        file_path = os.path.join(save_path, file_name)
                    print("File path good")
                    with open(file_path, "wb") as file:
                        while True:
                            chunk = await websocket.recv()
                            if chunk == b"EOF":
                                print("EOF recieved")
                                break
                            file.write(chunk)
                    print(f"Saved {file_name}")
                    if file_name == "spotify_data.json":
                        pi_signal_dispatcher.update_spotify_widget.emit()
                    if file_name == "saved_pages.json":
                        pi_signal_dispatcher.update_pages.emit()
                    if file_name == "weather_data.json":
                        pi_signal_dispatcher.update_weather_widget.emit()
        except Exception as e:
            print(f"Exception receiving file: {e}")
    else:
        print("Not connected to server")
        asyncio.create_task(websocket_client())

async def send_message(message):
    global websocket_connection
    if websocket_connection is not None:
        try:
            await websocket_connection.send(message)
            print(f"Sent to PC >>> {message}")
        except Exception as e:
            print(f"Error sending message: {e}")
    else:
        print("Not connected to server")
        asyncio.create_task(websocket_client())

async def websocket_client():
    global websocket_connection
    global files_updated
    global spotify_updated
    global weather_updated
    global buttons_updated
    while True:
        try:
            print(f"Attempting to connect to {server_address}")
            async with websockets.connect(server_address) as websocket:
                print(f"Connected to {server_address}")
                websocket_connection = websocket
                if not buttons_updated:
                    await send_message("button")
                    buttons_updated = True
                    await asyncio.sleep(2)
                if not spotify_updated:
                    await request_from_server("spotify_json")
                    print("requesting initial spotify")
                    pi_signal_dispatcher.update_spotify_widget.emit()
                    spotify_updated = True
                    await asyncio.sleep(2)
                if not weather_updated:
                    print("requesting initial weather")
                    await request_from_server("weather_json")
                    await receive_file(websocket)
                    pi_signal_dispatcher.update_weather_widget.emit()
                    weather_updated = True
                    await asyncio.sleep(2)
                if not files_updated:
                    await send_message("files")
                    files_updated = True
                    await asyncio.sleep(2)

                await receive_file(websocket)

        except Exception as e:
            print(f"Error occured while connecting to server.\n"
                  f"Error: {e}\nRetrying in 5 seconds...")
            websocket_connection = None
            await asyncio.sleep(5)

async def handle_send_func_signal(message):
    global websocket_connection
    print(message)
    if websocket_connection is not None:
        await send_message(message)
    else:
        print("Connection not available")
        asyncio.create_task(websocket_client())

async def request_from_server(request):
    global spotify_updated
    global websocket_connection
    if not spotify_updated and websocket_connection:
        print("pi_client, requesting json")
        asyncio.create_task(send_message(request))
        print("pi_client, task created")
    else:
        print("Didn't make it")
        print(f"Websocket_connection: {websocket_connection}")
        print(f"Spotify updated {spotify_updated}")

pi_signal_dispatcher.send_func_signal.connect(lambda msg: asyncio.create_task(handle_send_func_signal(msg)))
