import asyncio
import websockets

async def fake_handshake():
    uri = "ws://0.0.0.0:8765"
    async with websockets.connect(uri) as websocket:
        await websocket.send('{'+
                            '"method": "handshake",'+
                            '"project_id": "1202780939",'+
                            '"user": "ScratchCat"'+
                            '}')
        response = await websocket.recv()
        print(f"Received: {response}")

asyncio.run(fake_handshake())