import asyncio
import websockets

async def on_connect(websocket):
    print("[SERVER] subprotocol seçildi:", websocket.subprotocol)
    try:
        async for msg in websocket:
            print("[SERVER] Received:", msg)
            await websocket.send('{"status":"OK"}')
    except Exception as e:
        print("[SERVER ERROR]:", e)

async def main():
    server = await websockets.serve(
        on_connect,
        "127.0.0.1",
        9000,
        subprotocols=["ocpp2.0.1"]  # kritik satır
    )
    print("[SERVER] Listening on ws://127.0.0.1:9000")
    await asyncio.Future()

asyncio.run(main())






