import asyncio
import json
import os
import websockets
from flask import Flask
import threading

# --- 1. AWS KO KHUSH RAKHNE WALA DUMMY SERVER ---
app = Flask(__name__)

@app.route('/')
def home():
    return "<h1>Bot is Running! Background WebSocket is Active. 🚀</h1>"

def run_dummy_server():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port, use_reloader=False)

# --- 2. TUMHARA ASLI TWEETSTREAM LOGIC ---
API_KEY = os.getenv(
    "TWEETSTREAM_API_KEY",
    "86372f9c2320232ae9323bd6c854c66d2e5361ea060d148f7c1e63298ccd1bc2",
)
WS_URL = "wss://ws.tweetstream.io/ws"

async def run_tweet_stream() -> None:
    protocols = [
        "tweetstream.v1",
        f"tweetstream.auth.token.{API_KEY}",
    ]

    try:
        async with websockets.connect(WS_URL, subprotocols=protocols) as ws:
            print("Connected to TweetStream! Waiting for tweets...")

            async for message in ws:
                try:
                    envelope = json.loads(message)
                except json.JSONDecodeError:
                    print("Received non-JSON message:", message)
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
                    # Yeh line real-time tweets print karegi
                    print(f"[{author}] {text}") 

    except websockets.exceptions.ConnectionClosed as e:
        print(f"WebSocket closed: {e}")
    except Exception as e:
        print(f"WebSocket error: {e}")


if __name__ == "__main__":
    # Step 1: Web server ko ek alag raste (thread) par start karo taaki AWS Health Check pass ho jaye
    server_thread = threading.Thread(target=run_dummy_server)
    server_thread.start()

    # Step 2: Apne main raste par WebSocket (asynchronous) ko start karo
    asyncio.run(run_tweet_stream())
