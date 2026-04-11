import os
from openai import AsyncOpenAI
import anthropic

async def generate_response(
    provider: str,
    model: str,
    prompt: str,
    system: str = None,
    temp: float = 0.7,
    max_tokens: int = 1024,
    openrouter_key: str = None,
    openai_key: str = None,
    anthropic_key: str = None
):
    if provider == "openai":
        key = openai_key or os.getenv("OPENAI_API_KEY")
        if not key:
            raise ValueError("OpenAI API key missing")
        client = AsyncOpenAI(api_key=key)
        
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        
        resp = await client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temp,
        )
        return resp.choices[0].message.content

    elif provider == "openrouter":
        key = openrouter_key or os.getenv("OPENROUTER_API_KEY")
        if not key:
            raise ValueError("OpenRouter API key missing")
        client = AsyncOpenAI(base_url="https://openrouter.ai/api/v1", api_key=key)
        
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        
        resp = await client.chat.completions.create(
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
        key = anthropic_key or os.getenv("ANTHROPIC_API_KEY")
        if not key:
            raise ValueError("Anthropic API key missing")
        client = anthropic.AsyncAnthropic(api_key=key)
        
        kwargs = {
            "model": model,
            "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temp
        }
        if system:
            kwargs["system"] = system
            
        resp = await client.messages.create(**kwargs)
        return resp.content[0].text
        
    raise ValueError(f"Unknown provider: {provider}")
