import asyncio
import json
import os
import threading
from flask import Flask
import websockets

app = Flask(__name__)

@app.route('/')
def home():
    # AWS ping karega, Flask turant jawab dega
    return "<h1>Bot is Running! Health Check Passed! 🚀</h1>"

# --- TUMHARA ASLI TWEETSTREAM LOGIC ---
API_KEY = os.getenv(
    "TWEETSTREAM_API_KEY",
    "86372f9c2320232ae9323bd6c854c66d2e5361ea060d148f7c1e63298ccd1bc2",
)
WS_URL = "wss://ws.tweetstream.io/ws"

async def run_tweet_stream():
    protocols = [
        "tweetstream.v1",
        f"tweetstream.auth.token.{API_KEY}",
    ]
    
    # Maine while loop laga diya hai, agar internet katega toh bot marega nahi, wapas connect hoga
    while True:
        try:
            async with websockets.connect(WS_URL, subprotocols=protocols) as ws:
                print("Connected to TweetStream! Waiting for tweets...")
                async for message in ws:
                    try:
                        envelope = json.loads(message)
                        if envelope.get("t") == "tweet" and envelope.get("op") == "content":
                            tweet = envelope.get("d", {}) or {}
                            author = tweet.get("author", {}).get("handle", "unknown")
                            text = tweet.get("text", "")
                            print(f"[{author}] {text}")
                    except json.JSONDecodeError:
                        continue
        except Exception as e:
            print(f"WebSocket Error/Disconnected: {e}. Reconnecting in 3 seconds...")
            await asyncio.sleep(3)

def start_background_worker():
    # Naye thread ke liye naya loop banana zaroori hota hai
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run_tweet_stream())

if __name__ == "__main__":
    # Step 1: TweetStream ko background worker bana kar start karo
    worker = threading.Thread(target=start_background_worker, daemon=True)
    worker.start()

    # Step 2: Flask ko Main Thread par rakho taaki AWS khush rahe
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port, use_reloader=False)
