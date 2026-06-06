import time
import requests

DEFAULT_API_URL = "http://127.0.0.1:1234/v1/chat/completions"
MAX_RETRIES = 3
RETRY_DELAY = 5


def check_connection(api_url=DEFAULT_API_URL):
    try:
        base_url = api_url.rsplit("/v1/", 1)[0]
        resp = requests.get(f"{base_url}/v1/models", timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            models = data.get("data", [])
            if models:
                return True, models[0].get("id", "Unknown Model")
            return True, "Unknown Model"
        return False, ""
    except Exception:
        return False, ""


def send_to_llm(prompt, system_prompt, api_url=DEFAULT_API_URL, temperature=0.1, retry=0):
    payload = {
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        "temperature": temperature,
        "max_tokens": -1,
        "stream": False
    }

    try:
        response = requests.post(api_url, json=payload, timeout=600)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"].strip()
    except requests.exceptions.Timeout:
        if retry < MAX_RETRIES:
            time.sleep(RETRY_DELAY)
            return send_to_llm(prompt, system_prompt, api_url, temperature, retry + 1)
        raise RuntimeError("LLM request timed out after all retries.")
    except requests.exceptions.ConnectionError:
        if retry < MAX_RETRIES:
            time.sleep(RETRY_DELAY)
            return send_to_llm(prompt, system_prompt, api_url, temperature, retry + 1)
        raise RuntimeError("Cannot connect to LM Studio. Is it running?")
    except Exception as e:
        if retry < MAX_RETRIES:
            time.sleep(RETRY_DELAY)
            return send_to_llm(prompt, system_prompt, api_url, temperature, retry + 1)
        raise
