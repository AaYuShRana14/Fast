import httpx
from fastapi import HTTPException
from storeapi.mail import send_joke_mail
import asyncio
async def get_a_joke(email):
    async with httpx.AsyncClient() as client:
        await asyncio.sleep(10)
        try:
            response = await client.get("https://official-joke-api.appspot.com/random_joke")
            response.raise_for_status()
            response=response.json()
            joke=response.get("setup")+" "+response.get("punchline")
            return await send_joke_mail(email, joke)
        except httpx.RequestError as e:
            raise HTTPException(status_code=500, detail="Error fetching joke")
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail="Error fetching joke")