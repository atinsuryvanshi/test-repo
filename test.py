import asyncio
import json
import os
from typing import Awaitable, Callable

import websockets


# बेहतर है कि key को environment variable से लें
# लेकिन फिलहाल आपके मौजूदा JS कोड जैसा direct value रखा है
API_KEY = os.getenv(
    "TWEETSTREAM_API_KEY",
    "86372f9c2320232ae9323bd6c854c66d2e5361ea060d148f7c1e63298ccd1bc2",
)
WS_URL = "wss://ws.tweetstream.io/ws"


async def run_tweet_stream() -> None:
    """TweetStream websocket से tweets read करता है (long‑running task)."""
    protocols = [
        "tweetstream.v1",
        f"tweetstream.auth.token.{API_KEY}",
    ]

    while True:
        try:
            async with websockets.connect(WS_URL, subprotocols=protocols) as ws:
                print("Connected to TweetStream!")

                async for message in ws:
                    try:
                        envelope = json.loads(message)
                    except json.JSONDecodeError:
                        print("Received non‑JSON message:", message)
                        continue

                    if envelope.get("t") == "tweet" and envelope.get("op") == "content":
                        tweet = envelope.get("d", {}) or {}
                        author_info = tweet.get("author") or {}
                        author = (
                            author_info.get("handle")
                            or author_info.get("name")
                            or "unknown"
                        )
                        text = tweet.get("text", "")
                        print(f"[{author}] {text}")

        except websockets.exceptions.ConnectionClosed as e:
            print(f"WebSocket closed, retrying in 5s: {e}")
            await asyncio.sleep(5)
        except Exception as e:
            print(f"WebSocket error, retrying in 5s: {e}")
            await asyncio.sleep(5)


async def _tcp_health_handler(
    reader: asyncio.StreamReader, writer: asyncio.StreamWriter
) -> None:
    """Simple TCP health handler जो बस connection accept करके close कर देता है."""
    try:
        # Data read/ignore (agar koi bhej दे तो)
        await reader.read(1024)
    except Exception:
        pass
    finally:
        writer.close()
        await writer.wait_closed()


async def main() -> None:
    """
    App Runner के लिए:
    - TCP port (default 8080 / $PORT) पर server start करता है (health check pass करने के लिए)
    - Background में TweetStream websocket client चलाता है
    """
    port = int(os.getenv("PORT", "8080"))

    server = await asyncio.start_server(
        _tcp_health_handler,
        host="0.0.0.0",
        port=port,
    )
    addr = ", ".join(str(sock.getsockname()) for sock in server.sockets or [])
    print(f"Health TCP server listening on: {addr}")

    # TweetStream background task
    tweet_task = asyncio.create_task(run_tweet_stream())

    async with server:
        await server.serve_forever()

    # Theoretically yahan तक नहीं पहुँचना चाहिए
    await tweet_task


if __name__ == "__main__":
    asyncio.run(main())
