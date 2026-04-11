import os
from openai import AsyncOpenAI
import anthropic

openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY", "dummy"))
anthropic_client = anthropic.AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY", "dummy"))

openrouter_client = AsyncOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY", "dummy")
)

async def generate_response(provider: str, model: str, prompt: str, system: str = None, temp: float = 0.7):
    if provider == "openai":
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        
        resp = await openai_client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temp,
        )
        return resp.choices[0].message.content

    elif provider == "openrouter":
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        
        resp = await openrouter_client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temp,
            extra_headers={
                "HTTP-Referer": "https://genna.railway.app",
                "X-Title": "Genna Annotation System"
            }
        )
        return resp.choices[0].message.content

    elif provider == "anthropic":
        kwargs = {
            "model": model,
            "max_tokens": 1024,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temp
        }
        if system:
            kwargs["system"] = system
            
        resp = await anthropic_client.messages.create(**kwargs)
        return resp.content[0].text
        
    raise ValueError(f"Unknown provider: {provider}")
