import asyncio
import os
import sys
import websockets
from widgets.functions.function_handler import handle_message
from widgets.functions.scripts.transfer_icons import get_icons
from gui_assets.signal_dispatcher import global_signal_dispatcher

host_ip = "0.0.0.0"
port = 1738

server_shutdown = False  # Global shutdown flag
shutdown_event = asyncio.Event()
server_connection = None  # Will hold the server instance
websocket_communication_server = None
json_confirmation = None

file_base_path = r"C:\Users\chave\PycharmProjects\PythonProject1\gui_assets\gui_icons"
json_path = r"C:\Users\chave\PycharmProjects\PythonProject1\saved_pages.json"
initial_file_path = r"This path doesn't exist yet but when it does, put it here :D"

async def send_initial_files(websocket):
    all_paths = get_icons(initial_file_path)
    for path in all_paths:
        await send_file(websocket,path)

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
            elif message.startswith("json"):
                await send_file(websocket,json_path)
            elif "heartbeat" in message:
                pass
            else:
                handle_message(message)
    except websockets.ConnectionClosed:
        print("Connection closed by client.")
    except Exception as e:
        print(f"Receive error >>> {e}")

async def send_json_file():
    global server_connection
    await send_message("json?")


async def handle_client(websocket):
    print("Client connected")
    await receive_messages(websocket)
    print("Client disconnected")

def shutdown_server():
    global server_shutdown
    print("Shutdown signal received")
    server_shutdown = True
    shutdown_event.set()

async def send_message(message):
    global server_connection
    if server_connection is not None:
        try:
            await server_connection.send(message)
            print(f"Sent to Pi >>> {message}")
        except Exception as e:
            print(f"Error sending message: {e}")
    else:
        print("No server connections")

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


global_signal_dispatcher.websocket_send_message.connect(lambda msg: asyncio.create_task(send_message(msg)))

#Add a signal to call send_json_file when we press a certain button, everything is set up once you call that function