# This file is called by api/whisper_api.py on startup to ensure the configured
# Ollama LLM (e.g. qwen2.5:7b-instruct-q4_K_M) is preloaded and kept resident in GPU
# VRAM alongside Faster-Whisper.
#
# Inputs:
#   - api_url: Base endpoint URL for Ollama generation (e.g. http://127.0.0.1:11434/api/generate)
#   - model: Name of the Ollama model to preload (e.g. qwen2.5:7b-instruct-q4_K_M)
#   - keep_alive: Duration or flag for keeping model in memory (-1 for indefinite / forever)
#   - max_retries: Number of retry attempts in case Ollama is still starting up
#   - retry_delay: Delay in seconds between retries
#   - logger_fn: Optional callable for logging messages (e.g. _fastlog)
#
# Outputs:
#   - Returns True if model was successfully preloaded into VRAM, False otherwise.
#   - Emits log records to console and logger_fn tracking preload status and memory state.

import time
import threading
from typing import Any, Callable, Optional, Union
import requests


def preload_ollama_model(
    api_url: str,
    model: str,
    keep_alive: Union[int, str] = -1,
    max_retries: int = 12,
    retry_delay: float = 5.0,
    logger_fn: Optional[Callable[[str], None]] = None,
) -> bool:
    """Sends an empty generate request to Ollama with keep_alive to preload
    the model into VRAM immediately without waiting for the first voice edit.
    """
    if not api_url or not model:
        return False

    # If keep_alive is explicitly 0, model unloading immediately is intended.
    if str(keep_alive).strip() == "0":
        msg = f"[Ollama Warmup] keep_alive is 0 for {model}; skipping VRAM preload."
        print(msg)
        if logger_fn:
            logger_fn(msg)
        return False

    def log(msg: str):
        print(f"[Ollama Warmup] {msg}")
        if logger_fn:
            logger_fn(f"[Warmup] {msg}")

    log(f"Initiating background preload for '{model}' at {api_url} (keep_alive={keep_alive})...")

    payload = {
        "model": model,
        "keep_alive": keep_alive,
    }

    start_time = time.time()
    for attempt in range(1, max_retries + 1):
        try:
            resp = requests.post(api_url, json=payload, timeout=90)
            if resp.status_code == 200:
                elapsed = time.time() - start_time
                log(f"Successfully loaded '{model}' into VRAM in {elapsed:.2f}s (attempt {attempt}).")
                return True
            else:
                log(f"Attempt {attempt}/{max_retries}: Ollama returned HTTP {resp.status_code}: {resp.text[:120]}")
        except requests.exceptions.RequestException as e:
            log(f"Attempt {attempt}/{max_retries}: Ollama not ready yet ({e.__class__.__name__}). Retrying in {retry_delay}s...")

        if attempt < max_retries:
            time.sleep(retry_delay)

    log(f"Failed to preload '{model}' after {max_retries} attempts. Will fall back to on-demand loading.")
    return False


def start_async_ollama_warmup(
    api_url: str,
    model: str,
    keep_alive: Union[int, str] = -1,
    max_retries: int = 12,
    retry_delay: float = 5.0,
    logger_fn: Optional[Callable[[str], None]] = None,
) -> threading.Thread:
    """Spawns a background daemon thread to preload Ollama asynchronously so
    FastAPI and Faster-Whisper startup are never blocked.
    """
    t = threading.Thread(
        target=preload_ollama_model,
        args=(api_url, model, keep_alive, max_retries, retry_delay, logger_fn),
        name="OllamaWarmupThread",
        daemon=True,
    )
    t.start()
    return t
