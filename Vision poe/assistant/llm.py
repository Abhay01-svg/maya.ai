import os


def query_local_model(prompt: str) -> str:
    """Query local LLM model.
    
    Supports:
    - Ollama: Set LOCAL_LLM_PROVIDER=ollama and LOCAL_LLM_MODEL=model_name
    - Hugging Face Transformers: Set LOCAL_LLM_PROVIDER=transformers
    - Custom endpoint: Set LOCAL_LLM_ENDPOINT=http://localhost:port
    
    Returns text response.
    """
    provider = os.environ.get('LOCAL_LLM_PROVIDER', 'stub')
    
    if provider == 'ollama':
        return _query_ollama(prompt)
    elif provider == 'transformers':
        return _query_transformers(prompt)
    elif provider == 'endpoint':
        return _query_endpoint(prompt)
    else:
        return _query_stub(prompt)


def _query_ollama(prompt: str) -> str:
    """Query Ollama local model."""
    try:
        import requests
        endpoint = os.environ.get('LOCAL_LLM_ENDPOINT', 'http://localhost:11434')
        model = os.environ.get('LOCAL_LLM_MODEL', 'llama2')
        
        response = requests.post(
            f"{endpoint}/api/generate",
            json={"model": model, "prompt": prompt, "stream": False},
            timeout=60
        )
        if response.status_code == 200:
            return response.json().get('response', '(No response)').strip()
        return f"(Ollama error: {response.status_code})"
    except ImportError:
        return "(Ollama provider requires 'requests' package)"
    except Exception as e:
        return f"(Ollama error: {e})"


def _query_transformers(prompt: str) -> str:
    """Query local model using Hugging Face transformers."""
    try:
        from transformers import pipeline
        model_name = os.environ.get('LOCAL_LLM_MODEL', 'gpt2')
        
        generator = pipeline('text-generation', model=model_name, device=0 if _has_cuda() else -1)
        result = generator(prompt, max_length=200, num_return_sequences=1)
        return result[0]['generated_text'].strip() if result else '(No response)'
    except ImportError:
        return "(Transformers provider requires 'transformers' package)"
    except Exception as e:
        return f"(Transformers error: {e})"


def _query_endpoint(prompt: str) -> str:
    """Query custom local inference endpoint."""
    try:
        import requests
        endpoint = os.environ.get('LOCAL_LLM_ENDPOINT', 'http://localhost:5000/generate')
        
        response = requests.post(
            endpoint,
            json={"prompt": prompt},
            timeout=60
        )
        if response.status_code == 200:
            data = response.json()
            return data.get('response', data.get('text', '(No response)')).strip()
        return f"(Endpoint error: {response.status_code})"
    except ImportError:
        return "(Custom endpoint requires 'requests' package)"
    except Exception as e:
        return f"(Endpoint error: {e})"


def _query_stub(prompt: str) -> str:
    """Fallback stub response."""
    return f"(local model) I can help with: {prompt}"


def _has_cuda() -> bool:
    """Check if CUDA is available."""
    try:
        import torch
        return torch.cuda.is_available()
    except Exception:
        return False


def query(prompt: str, mode: str = 'local') -> str:
    """Query local LLM model.
    
    Args:
        prompt: Input text prompt
        mode: Execution mode (default: 'local')
    
    Returns:
        Text response from model
    """
    return query_local_model(prompt)
