import asyncio
import websockets

async def handler(websocket):
    # Continuously listen for incoming messages
    async for message in websocket:
        print(f"Received: {message}")
        await websocket.send(f"Server echoed: {message}")

async def main(ip, port):
    # Use "0.0.0.0" to allow external connections when hosting
    async with websockets.serve(handler, ip, port):
        print(f"WebSocket server running IP {ip} with port {port}")
        await asyncio.Future()  # Keep the server running forever

if __name__ == "__main__":
    asyncio.run(main("127.0.0.1",8765)) #0.0.0.0 for final
