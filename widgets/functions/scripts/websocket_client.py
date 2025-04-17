import asyncio
import websockets
import os
from widgets.functions.scripts.transfer_icons import get_icons
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

async def websocket_client():
    #Send over gui_icons
    print("setting up websocket connection")
    all_paths = get_icons(r'C:\Users\chave\PycharmProjects\PythonProject1\gui_assets\gui_icons')
    async with websockets.connect(server_address) as websocket:
        for path in all_paths:
            await send_file(websocket, path)

        try:
            #if send page signal is active run a lamda function that runs a co_routine with current websocket server
            global_signal_dispatcher.send_pages_signal.connect(
                lambda: asyncio.run_coroutine_threadsafe(
                    send_pages_data(websocket), asyncio.get_event_loop()
                )
            )

            # Wait for messages from the Pi
            while True:

                message = await websocket.recv()
                print(f"Server >>> {message}")
                #emit a pyqt signal to
                global_signal_dispatcher.raspi_button_signal.emit(message)

        except websockets.exceptions.ConnectionClosed:
            print("Connection closed by server.")

async def send_pages_data(websocket):
    file_path = r"C:\Users\chave\PycharmProjects\PythonProject1\saved_pages.json"
    print("send pages signal received, sending page data")
    await send_file(websocket, file_path)


#if __name__ == "__main__":
#    asyncio.run(main())