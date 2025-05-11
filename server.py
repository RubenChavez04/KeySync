import asyncio
import os
import sys
import websockets
from widgets.functions.function_handler import handle_message
from widgets.functions.scripts.transfer_icons import get_icons
from gui_assets.signal_dispatcher import global_signal_dispatcher
from widgets.spotify_widget.spotify_signals import spotify_signals

host_ip = "0.0.0.0"
port = 1738

server_shutdown = False  # Global shutdown flag
shutdown_event = asyncio.Event()
server_connection = None  # Will hold the server instance
active_connections = set()
websocket_communication_server = None
json_confirmation = None


json_path = "pi_assets/saved_pages.json"
initial_file_path = "pi_assets"
button_images_file_path = "pi_assets/button_images"
spotify_data_path = "pi_assets/spotify_data.json"
weather_data_path = "pi_assets/weather_data.json"

async def send_initial_files(websocket):
    all_paths = get_icons(initial_file_path)
    for path in all_paths:
        await send_file(websocket,path)
        await asyncio.sleep(0.3)

async def send_file(websocket, file_path):
    if os.path.exists(file_path):
        file_name = os.path.basename(file_path)
        print(f"Sending file: {file_name}")
        await websocket.send(file_name)

        with open(file_path, "rb") as file:
            while chunk := file.read(4096):
                await websocket.send(chunk)
        await websocket.send(b"EOF")

        print(f"Sent file: {file_name}")
        await asyncio.sleep(0.3)
    else:
        print(f"File not found: {file_path}")

async def receive_messages(websocket):
    global json_confirmation
    try:
        while True:
            message = await websocket.recv()
            print(f"Pi >>> {message}")
            if message.startswith("files"):
                await send_initial_files(websocket)
                await asyncio.sleep(0.2)
            elif message.startswith("json"):
                await send_file(websocket,json_path)
                await asyncio.sleep(0.2)
            elif "spotify_json" in message:
                await send_file(websocket,spotify_data_path)
                await asyncio.sleep(0.2)
            elif "button" in message:
                await send_button_images()
            else:
                handle_message(message)
    except websockets.ConnectionClosed:
        print("Connection closed by client.")
    except Exception as e:
        print(f"Receive error >>> {e}")

async def handle_client(websocket):
    global active_connections
    print("Client connected")
    active_connections.add(websocket)  # Add connection to the set
    try:
        await receive_messages(websocket)  # Handle messages
    finally:
        active_connections.remove(websocket)  # Ensure it's removed on disconnect
        print("Client disconnected")


def shutdown_server():
    global server_shutdown
    print("Shutdown signal received")
    server_shutdown = True
    shutdown_event.set()

async def send_message(message):
    global active_connections
    if active_connections:
        for websocket in list(active_connections):  # Iterate through clients
            try:
                await websocket.send(message)
                if "progress" in message:
                    pass
                else:
                    print(f"Sent to client >>> {message}")
            except Exception as e:
                print(f"Error sending to client: {e}")
    else:
        print("No active WebSocket connections.")


async def main_server():
    global server_connection
    print("Server starting")
    server = await websockets.serve(handle_client, host_ip, port)
    server_connection = server
    print(f"Server running on {host_ip}:{port}")
    await shutdown_event.wait()  # Wait here until `shutdown_event.set()` is called

    print("Closing server...")
    server.close()
    await server.wait_closed()
    print("Server shut down.")
    sys.exit(-1)

async def send_spotify_data_file():
    global active_connections
    if active_connections:
        for websocket in list(active_connections):  # Iterate through clients
            try:
                await send_file(websocket, spotify_data_path)  # Send Spotify data
            except Exception as e:
                print(f"Error sending Spotify data file: {e}")
    else:
        print("No active WebSocket connection to send Spotify data file.")

async def send_weather_data_file():
    global active_connections
    if active_connections:
        for websocket in list(active_connections):  # Iterate through clients
            try:
                await send_file(websocket, weather_data_path)  # Send Spotify data
            except Exception as e:
                print(f"Error sending Weather data file: {e}")
    else:
        print("No active WebSocket connection to send Weather data file.")

async def send_json_file():
    global active_connections
    if active_connections:
        for websocket in list(active_connections):
            try:
                await send_file(websocket, json_path)
            except Exception as e:
                print(f"Error sending json data file: {e}")
    else:
        print("No active WebSocket connection to send json data file.")

async def send_button_images():
    global active_connections
    if active_connections:
        for websocket in list(active_connections):
            for path in get_icons(button_images_file_path):
                try:
                    await send_file(websocket, path)
                    await asyncio.sleep(.1)
                except Exception as e:
                    print(f"Error sending button_image: {e}")
            await send_json_file()
    else:
        print("No active WebSocket connection to send json data file.")


global_signal_dispatcher.websocket_send_message.connect(lambda msg: asyncio.create_task(send_message(msg)))
global_signal_dispatcher.websocket_send_spot.connect(lambda: asyncio.create_task(send_spotify_data_file()))
global_signal_dispatcher.websocket_send_spot_progress.connect(lambda msg: asyncio.create_task(send_message(msg)))
global_signal_dispatcher.websocket_send_pages.connect(lambda: asyncio.create_task(send_button_images()))
global_signal_dispatcher.websocket_send_weather.connect(lambda: asyncio.create_task(send_weather_data_file()))
#Add a signal to call send_json_file when we press a certain button, everything is set up once you call that function