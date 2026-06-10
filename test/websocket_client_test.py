import asyncio
import websockets

async def fake_handshake():
    uri = "ws://localhost:8765"
    async with websockets.connect(uri) as websocket:
        await websocket.send('{'+
                            '"method": "handshake",'+
                            '"project_id": "1202780939",'+
                            '"user": "Boss_1s"'+
                            '}')
        response = await websocket.recv()
        print(f"Received: {response}")

asyncio.run(fake_handshake())