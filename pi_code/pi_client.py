import asyncio
import websockets
import os
from pi_code.signal_dispatcher_pi import pi_signal_dispatcher

server_address = "ws://10.0.6.190:1738"
save_path = "client_assets"
files_updated = False
websocket_connection = None

async def receive_file(websocket):
    global websocket_connection
    if websocket_connection is not None:
        try:
            while True:
                incoming = await websocket.recv()
                if "json?" in incoming:
                    await send_message("json")
                else:
                    file_name = incoming
                    print(f"Receiving file: {file_name}")
                    os.makedirs(save_path, exist_ok=True)
                    file_path = os.path.join(save_path, file_name)
                    with open(file_path, "wb") as file:
                        while True:
                            chunk = await websocket.recv()
                            if chunk == b"EOF":
                                break
                            file.write(chunk)
                    print(f"Saved {file_name}")
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
    while True:
        try:
            print(f"Attempting to connect to {server_address}")
            async with websockets.connect(server_address) as websocket:
                print(f"Connected to {server_address}")
                websocket_connection = websocket
                if not files_updated:
                    await send_message("files")
                    files_updated = True
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


pi_signal_dispatcher.send_func_signal.connect(lambda msg: asyncio.create_task(handle_send_func_signal(msg)))

if __name__ == "__main__":
    asyncio.run(websocket_client())