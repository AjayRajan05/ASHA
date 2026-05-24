# Copyright 2026 Ajay Rajan
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Global SDK patching for viral PrivySHA adoption.

This enables true one-line integration: `import privysha; privysha.auto_patch()`
"""


from typing import Any, Callable, Dict, List, Optional
from functools import wraps


# Global state for patch management
_patches_applied: Dict[str, Any] = {}
_original_functions: Dict[str, Any] = {}
_privysha_enabled = True
_patch_warning_shown = False


# Version safety for critical SDKs
SUPPORTED_VERSIONS = {
    "openai": ["1.0.0", "1.1.0", "1.2.0", "1.3.0", "1.4.0", "1.5.0"],
    "anthropic": ["0.3.0", "0.5.0", "0.6.0", "0.7.0"],
    "google-generativeai": ["0.3.0", "0.4.0", "0.5.0"],
    "transformers": ["4.20.0", "4.21.0", "4.22.0", "4.23.0", "4.24.0", "4.25.0"],
}


def _parse_major_version(version: str) -> int:
    """Parse major version number from a semver string."""
    try:
        return int(str(version).split(".")[0])
    except (ValueError, IndexError):
        return 0


def _check_version_compatibility(provider: str, verbose: bool = False) -> bool:
    """
    Check if the installed SDK version is supported.

    Args:
        provider: Provider name (openai, anthropic, etc.)

    Returns:
        True if version is supported, False otherwise
    """
    try:
        if provider == "openai":
            import openai

            version = getattr(openai, "__version__", "unknown")
            # OpenAI SDK 1.x+ uses the new client API
            if _parse_major_version(version) >= 1:
                return True
        elif provider == "anthropic":
            import anthropic

            version = getattr(anthropic, "__version__", "unknown")
        elif provider == "google-generativeai":
            import google.generativeai as genai

            version = getattr(genai, "__version__", "unknown")
        elif provider == "transformers":
            import transformers

            version = getattr(transformers, "__version__", "unknown")
        else:
            return True  # Unknown provider, assume compatible

        supported = SUPPORTED_VERSIONS.get(provider, [])
        if version in supported:
            return True
        # Accept any newer major version for openai 1.x+
        if provider == "openai" and _parse_major_version(version) >= 1:
            return True
        if verbose:
            print(f"⚠️ Unsupported {provider} version: {version}")
            print(f"   Supported versions: {', '.join(supported)}")
        return False

    except ImportError:
        return False
    except Exception:
        return True  # Assume compatible if version check fails


def auto_patch(
    enable: bool = True, providers: List[str] = None, verbose: bool = False
) -> Dict[str, Any]:
    """
    Global SDK patching for viral PrivySHA adoption.

    This is the viral adoption feature - enables true one-line integration.
    Patches major LLM SDKs to automatically apply PrivySHA processing.

    Args:
        enable: Enable/disable patching
        providers: List of providers to patch (openai, anthropic, gemini, etc.)
        verbose: Enable verbose logging

    Returns:
        Dictionary with patch status and statistics
    """
    global _privysha_enabled, _patch_warning_shown

    if providers is None:
        providers = ["openai", "anthropic",
                     "google.generativeai", "huggingface"]

    _privysha_enabled = enable

    if enable and not _patch_warning_shown:
        import warnings

        warnings.warn(
            "PrivySHA auto_patch() monkey-patches installed LLM SDKs. "
            "Use wrap_llm() for explicit per-client control.",
            UserWarning,
            stacklevel=2,
        )
        _patch_warning_shown = True

    if verbose:
        print(
            f"[PrivySHA] Auto-patch {'enabled' if enable else 'disabled'} for providers: {providers}"
        )

    if not enable:
        # Disable all patches
        _unpatch_all()
        return {"status": "disabled", "patches_applied": 0}

    # Import PrivySHA processing function
    try:
        from ..utils.dropin import process as privysha_process
    except ImportError as e:
        if verbose:
            print(f"[PrivySHA] Failed to import PrivySHA: {e}")
        return {"status": "error", "error": str(e)}

    patches_applied = 0
    patch_errors = []

    # Patch OpenAI SDK
    if "openai" in providers:
        try:
            if not _check_version_compatibility("openai", verbose):
                patch_errors.append(
                    "OpenAI: Unsupported version - skipping patch")
            else:
                result = _patch_openai(privysha_process, verbose)
                if result["success"]:
                    patches_applied += 1
                    _patches_applied["openai"] = result
                else:
                    patch_errors.append(f"OpenAI: {result['error']}")
        except Exception as e:
            patch_errors.append(f"OpenAI: {str(e)}")

    # Patch Anthropic SDK
    if "anthropic" in providers:
        try:
            if not _check_version_compatibility("anthropic", verbose):
                patch_errors.append(
                    "Anthropic: Unsupported version - skipping patch")
            else:
                result = _patch_anthropic(privysha_process, verbose)
                if result["success"]:
                    patches_applied += 1
                    _patches_applied["anthropic"] = result
                else:
                    patch_errors.append(f"Anthropic: {result['error']}")
        except Exception as e:
            patch_errors.append(f"Anthropic: {str(e)}")

    # Patch Google Generative AI SDK
    if "google.generativeai" in providers:
        try:
            result = _patch_google_generativeai(privysha_process, verbose)
            if result["success"]:
                patches_applied += 1
                _patches_applied["google.generativeai"] = result
            else:
                patch_errors.append(f"Google GenerativeAI: {result['error']}")
        except Exception as e:
            patch_errors.append(f"Google GenerativeAI: {str(e)}")

    # Patch Hugging Face
    if "huggingface" in providers:
        try:
            result = _patch_huggingface(privysha_process, verbose)
            if result["success"]:
                patches_applied += 1
                _patches_applied["huggingface"] = result
            else:
                patch_errors.append(f"HuggingFace: {result['error']}")
        except Exception as e:
            patch_errors.append(f"HuggingFace: {str(e)}")

    if verbose:
        print(f"[PrivySHA] Successfully applied {patches_applied} patches")
        if patch_errors:
            print(f"[PrivySHA] Patch errors: {patch_errors}")

    return {
        "status": "success" if patches_applied > 0 else "partial",
        "patches_applied": patches_applied,
        "active_patches": list(_patches_applied.keys()),
        "errors": patch_errors,
        "enabled_providers": providers,
    }


def _coerce_processed(result: Any, fallback: str) -> str:
    """Normalize process() return value to a prompt string."""
    if isinstance(result, str):
        return result
    if isinstance(result, dict):
        prompts = result.get("prompts", {})
        return (
            prompts.get("optimized")
            or prompts.get("sanitized")
            or result.get("optimized")
            or fallback
        )
    return fallback


def _store_original(key: str, original: Any) -> None:
    if key not in _original_functions:
        _original_functions[key] = original


def _restore_original(key: str, target: Any, attr: str) -> None:
    if key in _original_functions:
        setattr(target, attr, _original_functions[key])


def _patch_openai(privysha_process: Callable, verbose: bool = False) -> Dict[str, Any]:
    """Patch OpenAI SDK for automatic PrivySHA processing."""
    try:
        import openai
    except ImportError:
        return {"success": False, "error": "OpenAI SDK not installed"}

    version = getattr(openai, "__version__", "0.0.0")
    if _parse_major_version(version) >= 1:
        return _patch_openai_v1(privysha_process, verbose)

    return _patch_openai_legacy(privysha_process, verbose)


def _patch_openai_v1(
    privysha_process: Callable, verbose: bool = False
) -> Dict[str, Any]:
    """Patch OpenAI SDK v1+ (client.chat.completions.create)."""
    try:
        from openai.resources.chat.completions import Completions
    except ImportError:
        return {
            "success": False,
            "error": "OpenAI SDK v1 structure not recognized",
        }

    original_create = Completions.create
    if getattr(original_create, "_privysha_patched", False):
        return {
            "success": True,
            "provider": "openai",
            "functions_patched": ["chat.completions.create"],
            "api_version": "v1",
            "already_patched": True,
        }

    _store_original("openai:Completions.create", original_create)

    @wraps(original_create)
    def patched_create(self, *args, **kwargs):
        if not _privysha_enabled:
            return original_create(self, *args, **kwargs)

        prompt = _extract_prompt_openai(kwargs)
        if not prompt:
            return original_create(self, *args, **kwargs)

        try:
            result = privysha_process(prompt, privacy=True, debug=verbose)
            processed_prompt = _coerce_processed(result, prompt)
            kwargs = _replace_prompt_openai(kwargs, processed_prompt)
            if verbose:
                print(
                    f"[PrivySHA] OpenAI v1 prompt processed: "
                    f"{len(prompt)} → {len(processed_prompt)} chars"
                )
            return original_create(self, *args, **kwargs)
        except Exception as e:
            if verbose:
                print(f"[PrivySHA] OpenAI v1 processing failed: {e}")
            return original_create(self, *args, **kwargs)

    patched_create._privysha_patched = True  # type: ignore[attr-defined]
    Completions.create = patched_create

    return {
        "success": True,
        "provider": "openai",
        "functions_patched": ["chat.completions.create"],
        "api_version": "v1",
        "original_functions_preserved": True,
    }


def _patch_openai_legacy(
    privysha_process: Callable, verbose: bool = False
) -> Dict[str, Any]:
    """Patch legacy OpenAI SDK (<1.0) ChatCompletion API."""
    try:
        import openai
    except ImportError:
        return {"success": False, "error": "OpenAI SDK not installed"}

    # Store original functions
    original_chat_create = getattr(openai.ChatCompletion, "create", None)
    original_completion_create = getattr(openai.Completion, "create", None)

    if not original_chat_create and not original_completion_create:
        return {"success": False, "error": "OpenAI SDK structure not recognized"}

    @wraps(original_chat_create)
    def patched_chat_create(*args, **kwargs):
        """Patched ChatCompletion.create with PrivySHA processing."""
        if not _privysha_enabled:
            return original_chat_create(*args, **kwargs)

        # Extract prompt from kwargs
        prompt = _extract_prompt_openai(kwargs)
        if not prompt:
            return original_chat_create(*args, **kwargs)

        try:
            # Process with PrivySHA
            result = privysha_process(prompt, privacy=True, debug=verbose)
            processed_prompt = _coerce_processed(result, prompt)

            # Replace prompt in kwargs
            kwargs = _replace_prompt_openai(kwargs, processed_prompt)

            if verbose:
                print(
                    f"[PrivySHA] OpenAI prompt processed: {len(prompt)} → {len(processed_prompt)} chars"
                )

            return original_chat_create(*args, **kwargs)

        except Exception as e:
            if verbose:
                print(f"[PrivySHA] OpenAI processing failed: {e}")
            return original_chat_create(*args, **kwargs)

    @wraps(original_completion_create)
    def patched_completion_create(*args, **kwargs):
        """Patched Completion.create with PrivySHA processing."""
        if not _privysha_enabled:
            return original_completion_create(*args, **kwargs)

        # Extract prompt from kwargs
        prompt = _extract_prompt_openai(kwargs)
        if not prompt:
            return original_completion_create(*args, **kwargs)

        try:
            # Process with PrivySHA
            result = privysha_process(prompt, privacy=True, debug=verbose)
            processed_prompt = _coerce_processed(result, prompt)

            # Replace prompt in kwargs
            kwargs = _replace_prompt_openai(kwargs, processed_prompt)

            if verbose:
                print(
                    f"[PrivySHA] OpenAI completion prompt processed: {len(prompt)} → {len(processed_prompt)} chars"
                )

            return original_completion_create(*args, **kwargs)

        except Exception as e:
            if verbose:
                print(f"[PrivySHA] OpenAI completion processing failed: {e}")
            return original_completion_create(*args, **kwargs)

    # Apply patches
    _store_original("openai:ChatCompletion.create", original_chat_create)
    openai.ChatCompletion.create = patched_chat_create
    if original_completion_create:
        _store_original("openai:Completion.create", original_completion_create)
        openai.Completion.create = patched_completion_create

    return {
        "success": True,
        "provider": "openai",
        "functions_patched": ["ChatCompletion.create"]
        + (["Completion.create"] if original_completion_create else []),
        "api_version": "legacy",
        "original_functions_preserved": True,
    }


def _patch_anthropic(
    privysha_process: Callable, verbose: bool = False
) -> Dict[str, Any]:
    """Patch Anthropic SDK Messages.create (v0.25+ client API)."""
    try:
        from anthropic.resources.messages import Messages
    except ImportError:
        return {"success": False, "error": "Anthropic SDK not installed"}

    original_create = Messages.create
    if getattr(original_create, "_privysha_patched", False):
        return {
            "success": True,
            "provider": "anthropic",
            "functions_patched": ["messages.create"],
            "already_patched": True,
        }

    _store_original("anthropic:Messages.create", original_create)

    @wraps(original_create)
    def patched_messages_create(self, *args, **kwargs):
        if not _privysha_enabled:
            return original_create(self, *args, **kwargs)

        messages = kwargs.get("messages", [])
        if not messages:
            return original_create(self, *args, **kwargs)

        try:
            kwargs = kwargs.copy()
            kwargs["messages"] = _process_anthropic_messages(
                messages, privysha_process, verbose
            )
            return original_create(self, *args, **kwargs)
        except Exception as e:
            if verbose:
                print(f"[PrivySHA] Anthropic processing failed: {e}")
            return original_create(self, *args, **kwargs)

    patched_messages_create._privysha_patched = True  # type: ignore[attr-defined]
    Messages.create = patched_messages_create

    return {
        "success": True,
        "provider": "anthropic",
        "functions_patched": ["messages.create"],
        "original_functions_preserved": True,
    }


def _process_anthropic_messages(
    messages: List[Any], privysha_process: Callable, verbose: bool
) -> List[Any]:
    """Process only the last user message in an Anthropic messages list."""
    processed_messages = []
    last_user_idx = None
    for idx, message in enumerate(messages):
        if isinstance(message, dict) and message.get("role") == "user":
            last_user_idx = idx

    for idx, message in enumerate(messages):
        if idx == last_user_idx and isinstance(message, dict) and "content" in message:
            content = message["content"]
            result = privysha_process(str(content), privacy=True, debug=verbose)
            processed_content = _coerce_processed(result, str(content))
            processed_message = message.copy()
            processed_message["content"] = processed_content
            processed_messages.append(processed_message)
        else:
            processed_messages.append(
                message.copy() if isinstance(message, dict) else message
            )
    return processed_messages


def _patch_google_generativeai(
    privysha_process: Callable, verbose: bool = False
) -> Dict[str, Any]:
    """Patch Google GenerativeAI SDK for automatic PrivySHA processing."""
    try:
        import google.generativeai as genai
    except ImportError:
        return {"success": False, "error": "Google GenerativeAI SDK not installed"}

    # Store original functions
    original_generate_content = getattr(
        genai.GenerativeModel, "generate_content", None)

    if not original_generate_content:
        return {
            "success": False,
            "error": "Google GenerativeAI SDK structure not recognized",
        }

    @wraps(original_generate_content)
    def patched_generate_content(*args, **kwargs):
        """Patched generate_content with PrivySHA processing."""
        if not _privysha_enabled:
            return original_generate_content(*args, **kwargs)

        # Extract prompt from kwargs
        prompt = kwargs.get("prompt", "")
        if not prompt:
            return original_generate_content(*args, **kwargs)

        try:
            # Process with PrivySHA
            result = privysha_process(prompt, privacy=True, debug=verbose)
            processed_prompt = _coerce_processed(result, prompt)

            # Replace prompt in kwargs
            kwargs = kwargs.copy()
            kwargs["prompt"] = processed_prompt

            if verbose:
                print(
                    f"[PrivySHA] Google GenerativeAI prompt processed: {len(prompt)} → {len(processed_prompt)} chars"
                )

            return original_generate_content(*args, **kwargs)

        except Exception as e:
            if verbose:
                print(f"[PrivySHA] Google GenerativeAI processing failed: {e}")
            return original_generate_content(*args, **kwargs)

    _store_original(
        "google:GenerativeModel.generate_content", original_generate_content
    )
    genai.GenerativeModel.generate_content = patched_generate_content

    return {
        "success": True,
        "provider": "google.generativeai",
        "functions_patched": ["GenerativeModel.generate_content"],
        "original_functions_preserved": True,
    }


def _patch_huggingface(
    privysha_process: Callable, verbose: bool = False
) -> Dict[str, Any]:
    """Patch Hugging Face transformers for automatic PrivySHA processing."""
    try:
        from transformers import pipeline as hf_pipeline
    except ImportError:
        return {"success": False, "error": "Hugging Face transformers not installed"}

    # Store original pipeline function
    original_call = getattr(hf_pipeline.Pipeline, "__call__", None)

    if not original_call:
        return {
            "success": False,
            "error": "Hugging Face Pipeline structure not recognized",
        }

    @wraps(original_call)
    def patched_call(self, *args, **kwargs):
        """Patched Pipeline call with PrivySHA processing."""
        if not _privysha_enabled:
            return original_call(self, *args, **kwargs)

        # Extract prompt from args/kwargs
        prompt = _extract_prompt_huggingface(args, kwargs)
        if not prompt:
            return original_call(self, *args, **kwargs)

        try:
            # Process with PrivySHA
            result = privysha_process(prompt, privacy=True, debug=verbose)
            processed_prompt = _coerce_processed(result, prompt)

            # Replace prompt in args
            if args:
                new_args = list(args)
                if new_args:
                    new_args[0] = processed_prompt
                    args = tuple(new_args)

            # Replace prompt in kwargs
            kwargs = kwargs.copy()
            if "prompt" in kwargs:
                kwargs["prompt"] = processed_prompt

            if verbose:
                original_prompt = args[0] if args else kwargs.get("prompt", "")
                print(
                    f"[PrivySHA] Hugging Face prompt processed: {len(original_prompt)} → {len(processed_prompt)} chars"
                )

            return original_call(self, *args, **kwargs)

        except Exception as e:
            if verbose:
                print(f"[PrivySHA] Hugging Face processing failed: {e}")
            return original_call(self, *args, **kwargs)

    _store_original("huggingface:Pipeline.__call__", original_call)
    hf_pipeline.Pipeline.__call__ = patched_call

    return {
        "success": True,
        "provider": "huggingface",
        "functions_patched": ["Pipeline.__call__"],
        "original_functions_preserved": True,
    }


def _extract_prompt_openai(kwargs: Dict[str, Any]) -> Optional[str]:
    """Extract prompt from OpenAI kwargs."""
    # Check for messages format
    messages = kwargs.get("messages")
    if messages and isinstance(messages, list) and messages:
        last_message = messages[-1] if messages else {}
        if isinstance(last_message, dict):
            return last_message.get("content")

    # Check for direct prompt
    return kwargs.get("prompt")


def _replace_prompt_openai(kwargs: Dict[str, Any], new_prompt: str) -> Dict[str, Any]:
    """Replace only the last user message content in OpenAI kwargs."""
    new_kwargs = kwargs.copy()

    messages = kwargs.get("messages")
    if messages and isinstance(messages, list) and messages:
        new_messages = []
        last_user_idx = None
        for idx, message in enumerate(messages):
            if isinstance(message, dict) and message.get("role") == "user":
                last_user_idx = idx

        for idx, message in enumerate(messages):
            if (
                idx == last_user_idx
                and isinstance(message, dict)
                and "content" in message
            ):
                new_message = message.copy()
                new_message["content"] = new_prompt
                new_messages.append(new_message)
            else:
                new_messages.append(
                    message.copy() if isinstance(message, dict) else message
                )
        new_kwargs["messages"] = new_messages

    if "prompt" in kwargs:
        new_kwargs["prompt"] = new_prompt

    return new_kwargs


def _extract_prompt_huggingface(args: tuple, kwargs: Dict[str, Any]) -> Optional[str]:
    """Extract prompt from Hugging Face args/kwargs."""
    # Check args first
    if args and len(args) > 0:
        return str(args[0])

    # Check kwargs
    return kwargs.get("prompt")


def _unpatch_all():
    """Remove all PrivySHA patches."""
    try:
        from openai.resources.chat.completions import Completions

        _restore_original("openai:Completions.create", Completions, "create")
    except ImportError:
        pass

    try:
        from anthropic.resources.messages import Messages

        _restore_original("anthropic:Messages.create", Messages, "create")
    except ImportError:
        pass

    try:
        import openai

        if "openai:ChatCompletion.create" in _original_functions:
            openai.ChatCompletion.create = _original_functions[
                "openai:ChatCompletion.create"
            ]
        if "openai:Completion.create" in _original_functions:
            openai.Completion.create = _original_functions["openai:Completion.create"]
    except ImportError:
        pass

    try:
        import google.generativeai as genai

        _restore_original(
            "google:GenerativeModel.generate_content",
            genai.GenerativeModel,
            "generate_content",
        )
    except ImportError:
        pass

    try:
        from transformers import pipeline as hf_pipeline

        pipeline_cls = getattr(hf_pipeline, "Pipeline", None)
        if pipeline_cls is not None:
            _restore_original(
                "huggingface:Pipeline.__call__", pipeline_cls, "__call__"
            )
    except ImportError:
        pass

    _patches_applied.clear()


def get_patch_status() -> Dict[str, Any]:
    """Get current patch status and statistics."""

    return {
        "enabled": _privysha_enabled,
        "active_patches": list(_patches_applied.keys()),
        "patch_details": _patches_applied.copy(),
        "total_patches_applied": len(_patches_applied),
    }


def disable_auto_patch():
    """Disable PrivySHA auto-patching temporarily."""
    global _privysha_enabled
    _privysha_enabled = False
    print("[PrivySHA] Auto-patch disabled")


def enable_auto_patch():
    """Re-enable PrivySHA auto-patching."""
    global _privysha_enabled
    _privysha_enabled = True
    print("[PrivySHA] Auto-patch enabled")
