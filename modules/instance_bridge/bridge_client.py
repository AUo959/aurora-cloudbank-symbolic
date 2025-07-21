import asyncio

import websockets

async def relay(uri: str, channel: str, client_id: str) -> None:
    async with websockets.connect(f"{uri}/ws/{channel}/{client_id}") as websocket:
        while True:
            msg = await asyncio.get_event_loop().run_in_executor(None, input, "")
            await websocket.send(msg)

def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Aurora bridge client")
    parser.add_argument("uri", help="Bridge server URI, e.g. ws://localhost:8090")
    parser.add_argument("channel", help="Channel name")
    parser.add_argument("client_id", help="Unique client identifier")
    args = parser.parse_args()

    asyncio.run(relay(args.uri, args.channel, args.client_id))

if __name__ == "__main__":
    main()
