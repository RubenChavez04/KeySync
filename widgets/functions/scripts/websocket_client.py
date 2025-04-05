import asyncio
import websockets
import os
import transfer_icons
from gui_assets.signal_dispatcher import global_signal_dispatcher

server_address = "ws://10.0.7.239:1738"

async def send_file(websocket, file_path):
    if os.path.exists(file_path):
        try:
            file = os.path.basename(file_path)
            print(f"Sending {file} to {server_address}")
            await websocket.send(file)

            with open(file_path, "rb") as file:
                while chunk := file.read(4096):
                    await websocket.send(chunk)

            await websocket.send(b"EOF")
            print(f"{file} successfully sent to {server_address}")
        except Exception as e:
            print(f"Exception >>> {e}")
    else:
        print(f"{file_path} not found")

async def main():
    #Send over gui_icons
    all_paths = transfer_icons.get_icons(r'C:\Users\chave\PycharmProjects\PythonProject1\gui_assets\gui_icons')
    async with websockets.connect(server_address) as websocket:
        for path in all_paths:
            await send_file(websocket, path)
        try:
            #Wait for messages from the Pi
            while True:
                message = await websocket.recv()
                print(f"Server >>> {message}")
                #emit a pyqt signal to
                global_signal_dispatcher.raspi_button_signal.emit(message)
        except websockets.exceptions.ConnectionClosed:
            print("Connection closed by server.")


if __name__ == "__main__":
    asyncio.run(main())