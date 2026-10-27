from google import genai
import config
from PIL import Image
from openai import OpenAI
import base64
from groq import Groq
import ollama
from mistralai.client.sdk import Mistral


def _model_entry(name):
    for m in config.MODELS:
        if m["name"] == name:
            return m
    raise KeyError(f"Model {name} not in config.MODELS")


def call_gemini(image_paths, prompt):
    entry = _model_entry("gemini-3.1-flash-lite-preview")
    client = genai.Client(api_key=entry["API_KEY"])
    images = [Image.open(path) for path in image_paths]
    response = client.models.generate_content(
        model=entry["name"], contents=[prompt] + images)
    return response.text


def call_llama_via_Groq(image_paths, prompt):
    entry = _model_entry("meta-llama/llama-4-scout-17b-16e-instruct")
    client = Groq(api_key=entry["API_KEY"])
    content = [{"type": "text", "text": prompt}]
    for path in image_paths:
        b64 = base64.b64encode(open(path, "rb").read()).decode("utf-8")
        content.append({"type": "image_url", "image_url": {
                       "url": f"data:image/png;base64,{b64}"}})
    response = client.chat.completions.create(
        model=entry["name"],
        messages=[{"role": "user", "content": content}],
        stream=False
    )
    return response.choices[0].message.content


def call_ollama(image_paths, prompt):
    response = ollama.chat(model="llama3.2-vision", messages=[
                           {"role": "user", "content": prompt, "images": image_paths}])
    return response["message"]["content"]


def call_mistral(image_paths, prompt):
    entry = _model_entry("pixtral-12b-2409")
    client = Mistral(api_key=entry["API_KEY"])
    content = [{"type": "text", "text": prompt}]
    for path in image_paths:
        b64 = base64.b64encode(open(path, "rb").read()).decode("utf-8")
        content.append({
            "type": "image_url",
            "image_url": f"data:image/png;base64,{b64}"
        })
    response = client.chat.complete(
        model=entry["name"],
        messages=[{"role": "user", "content": content}]
    )
    return response.choices[0].message.content


def call_openai(image_paths, prompt):
    entry = _model_entry("gpt-4o-mini")
    client = OpenAI(api_key=entry["API_KEY"])
    content = [{"type": "text", "text": prompt}]
    for path in image_paths:
        b64 = base64.b64encode(open(path, "rb").read()).decode("utf-8")
        content.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/png;base64,{b64}",
                "detail": "low"
            }
        })
    response = client.chat.completions.create(
        model=entry["name"],
        messages=[{"role": "user", "content": content}]
    )
    return response.choices[0].message.content
