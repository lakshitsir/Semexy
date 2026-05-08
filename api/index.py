import os
from fastapi import FastAPI, HTTPException
from pyrogram import Client
from pyrogram.errors import BadRequest, FloodWait

# --- ENVIRONMENT VARIABLES ---
# We pull these securely from Vercel. 
# API_ID is wrapped in int() because Pyrogram requires it to be a number.
try:
    API_ID = int(os.environ.get("API_ID"))
    API_HASH = os.environ.get("API_HASH")
    BOT_TOKEN = os.environ.get("BOT_TOKEN")
    DEV_TAG = os.environ.get("DEV_TAG", "@YourUsername") # Add your Dev Tag in Vercel or it defaults to this
except TypeError:
    print("CRITICAL ERROR: Environment Variables are missing!")

app = FastAPI(title="Telegram ID API - Secure Vercel Edition")

@app.get("/api/get_id")
async def get_user_id(username: str):
    # Clean the input
    clean_username = username.strip().lstrip("@")
    
    if not clean_username:
        raise HTTPException(status_code=400, detail="Username cannot be empty")

    # Initialize Client in memory
    client = Client(
        "vercel_session",
        api_id=API_ID,
        api_hash=API_HASH,
        bot_token=BOT_TOKEN,
        in_memory=True
    )
        
    try:
        # Connect to Telegram
        await client.start()
        
        # Fetch user
        user = await client.get_users(clean_username)
        
        # Fully accurate JSON response WITH DEV TAG
        return {
            "status": "success",
            "dev": DEV_TAG,
            "query": username,
            "data": {
                "user_id": user.id,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name
            }
        }
        
    except BadRequest:
        raise HTTPException(status_code=404, detail="User not found or invalid username")
    except FloodWait as e:
        raise HTTPException(status_code=429, detail=f"Rate limit hit. Wait {e.value} seconds.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
    finally:
        # Disconnect safely
        if client.is_connected:
            await client.stop()

