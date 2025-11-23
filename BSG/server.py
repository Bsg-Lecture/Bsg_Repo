import asyncio
import websockets
from websockets import Subprotocol

connected_clients = set()

async def on_connect(websocket, path):
    """Yeni bir istemci bağlandığında çağrılır."""
    client_ip = websocket.remote_address[0]
    print(f"Client connected: {client_ip} | Path: {path}")
    connected_clients.add(websocket)

    try:
        async for message in websocket:
            print(f"[{client_ip}] {message}")

            # BootNotification mesajına yanıt ver
            if '"BootNotification"' in message:
                response = '[3,"boot_notification_response",{"status":"Accepted","currentTime":"2025-11-11T12:00:00Z","interval":10}]'
                await websocket.send(response)
                print(f"✅ Sent BootNotification response to {client_ip}")

    except websockets.exceptions.ConnectionClosed:
        print(f"Client disconnected: {client_ip}")
    finally:
        connected_clients.remove(websocket)

async def main():
    IP = "127.0.0.1"
    PORT = 9101

    print("Certificate is currently valid")
    print(f"Starting OCPP server at ws://{IP}:{PORT}")

    async with websockets.serve(
        on_connect,
        IP,
        PORT,
        subprotocols=[Subprotocol("ocpp1.6")]
    ):
        await asyncio.Future()  # sonsuza kadar açık kalır

if __name__ == "__main__":
    asyncio.run(main())
