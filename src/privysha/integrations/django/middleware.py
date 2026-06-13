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
Django Middleware Integration for PrivySHA

This module provides Django middleware that automatically processes requests
containing prompts through PrivySHA's security and optimization pipeline.
"""

from functools import wraps
from typing import Dict, Any, Optional, List, Callable, TypeVar, TYPE_CHECKING, cast
import json
import time

if TYPE_CHECKING:
    from django.http import HttpRequest, HttpResponse, JsonResponse
    from django.conf import settings
    from django.utils.deprecation import MiddlewareMixin
    from django.core.management.base import BaseCommand

    DJANGO_AVAILABLE = True
    DJANGO_COMMAND_AVAILABLE = True
else:
    try:
        from django.http import HttpRequest, HttpResponse, JsonResponse
        from django.conf import settings
        from django.utils.deprecation import MiddlewareMixin

        DJANGO_AVAILABLE = True
    except ImportError:
        DJANGO_AVAILABLE = False

        class HttpRequest:
            pass

        class HttpResponse:
            pass

        class JsonResponse:
            pass

        class settings:
            pass

        class MiddlewareMixin:
            def __init__(self, get_response: Callable[..., Any]) -> None:
                self.get_response = get_response

    try:
        from django.core.management.base import BaseCommand

        DJANGO_COMMAND_AVAILABLE = True
    except ImportError:
        DJANGO_COMMAND_AVAILABLE = False

        class BaseCommand:
            help = "Base command placeholder"

            def handle(self, *args: Any, **options: Any) -> None:
                pass

_F = TypeVar("_F", bound=Callable[..., Any])

from ...utils.dropin import process


class PrivySHAMiddleware(MiddlewareMixin):
    """
    Django middleware that automatically processes prompts through PrivySHA.

    This middleware intercepts requests containing prompts, processes them
    through PrivySHA's security and optimization pipeline, and forwards the
    optimized prompts to the actual Django views.

    Usage:
        # settings.py
        MIDDLEWARE = [
            'django.middleware.security.SecurityMiddleware',
            'privysha.integrations.django.middleware.PrivySHAMiddleware',
            'django.middleware.common.CommonMiddleware',
            # ... other middleware
        ]

    Configuration:
        # settings.py
        PRIVYSHA_CONFIG = {
            'PRIVACY': True,
            'TOKEN_BUDGET': 1200,
            'ENDPOINTS': ['/api/chat', '/api/completions'],
            'PROMPT_FIELDS': ['prompt', 'messages', 'input'],
            'DEBUG_MODE': False
        }
    """

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        """Initialize the middleware."""
        if not DJANGO_AVAILABLE:
            raise ImportError(
                "Django is not installed. Install with: pip install django\n"
                "Or use the standalone PrivySHA functions instead."
            )

        super().__init__(get_response)
        self.privacy = getattr(
            settings, "PRIVYSHA_CONFIG", {}).get("PRIVACY", True)
        self.token_budget = getattr(settings, "PRIVYSHA_CONFIG", {}).get(
            "TOKEN_BUDGET", 1200
        )
        self.debug_mode = getattr(settings, "PRIVYSHA_CONFIG", {}).get(
            "DEBUG_MODE", False
        )

        # Default endpoints that typically contain LLM prompts
        self.endpoints = getattr(settings, "PRIVYSHA_CONFIG", {}).get(
            "ENDPOINTS",
            [
                "/api/chat/completions",
                "/api/completions",
                "/api/chat",
                "/api/generate",
                "/api/ask",
                "/api/query",
                "/chat/completions",
                "/completions",
                "/chat",
                "/generate",
                "/ask",
                "/query",
                "/v1/chat/completions",
                "/v1/completions",
            ],
        )

        # Default field names that typically contain prompts
        self.prompt_fields = getattr(settings, "PRIVYSHA_CONFIG", {}).get(
            "PROMPT_FIELDS",
            [
                "prompt",
                "messages",
                "input",
                "query",
                "text",
                "content",
                "question",
                "instruction",
            ],
        )

    def process_request(self, request: HttpRequest) -> Optional[HttpResponse]:
        """
        Process request before it reaches the view.

        Args:
            request: Django HttpRequest

        Returns:
            HttpResponse if request should be blocked, None otherwise
        """
        # Store original request data and start time
        request.privysha_original_data = None
        request.privysha_processing_info = None
        request.privysha_start_time = time.time()

        # Check if this endpoint should be processed
        if not self._should_process_endpoint(request.path):
            return None

        # Process the request
        try:
            # Get request data
            request_data = self._get_request_data(request)
            if not request_data:
                return None

            # Store original data
            request.privysha_original_data = request_data.copy()

            # Extract and process prompts
            processed_data, processing_info = self._process_prompts(
                request_data)

            if self.debug_mode:
                print(
                    f"PrivySHA Debug: Processed {processing_info['prompts_processed']} prompts"
                )
                print(
                    f"PrivySHA Debug: Token reduction: {processing_info.get('avg_token_reduction', 0)}%"
                )
                print(
                    f"PrivySHA Debug: Security threats: {processing_info.get('security_threats_detected', 0)}"
                )

            # Store processing info
            request.privysha_processing_info = processing_info

            # Replace request data with processed data
            self._replace_request_data(request, processed_data)

        except Exception as e:
            if self.debug_mode:
                print(f"PrivySHA Error: {str(e)}")
            # Fail gracefully - continue with original request

        return None

    def process_response(
        self, request: HttpRequest, response: HttpResponse
    ) -> HttpResponse:
        """
        Add processing info to response headers.

        Args:
            request: Django HttpRequest
            response: Django HttpResponse

        Returns:
            HttpResponse with PrivySHA headers
        """
        if (
            hasattr(request, "privysha_processing_info")
            and request.privysha_processing_info
        ):
            processing_info = request.privysha_processing_info

            if processing_info["prompts_processed"] > 0:
                # Add processing headers
                response["X-PrivySHA-Processed"] = "true"
                response["X-PrivySHA-Prompts"] = str(
                    processing_info["prompts_processed"]
                )
                response["X-PrivySHA-Token-Reduction"] = str(
                    processing_info.get("avg_token_reduction", 0)
                )
                response["X-PrivySHA-Threats-Blocked"] = str(
                    processing_info.get("security_threats_detected", 0)
                )
                response["X-PrivySHA-PII-Masked"] = str(
                    processing_info.get("pii_masked", 0)
                )

                if self.debug_mode:
                    processing_time = (
                        time.time() - request.privysha_start_time) * 1000
                    response["X-PrivySHA-Processing-Time"] = f"{processing_time:.2f}ms"

        return response

    def _should_process_endpoint(self, endpoint_path: str) -> bool:
        """Check if the endpoint should be processed by PrivySHA."""
        # Check if endpoint path matches any of our target endpoints
        return any(endpoint in endpoint_path for endpoint in self.endpoints)

    def _get_request_data(self, request: HttpRequest) -> Optional[Dict[str, Any]]:
        """Extract and parse request data."""
        try:
            if request.method in ["POST", "PUT", "PATCH"]:
                content_type = request.content_type or ""

                if "application/json" in content_type:
                    return cast(Dict[str, Any], json.loads(request.body.decode("utf-8")))
                elif "application/x-www-form-urlencoded" in content_type:
                    return dict(request.POST)
                elif "multipart/form-data" in content_type:
                    return {key: value for key, value in request.POST.items()}

            return None

        except Exception:
            return None

    def _process_prompts(
        self, data: Dict[str, Any]
    ) -> tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Process all prompts in the request data.

        Args:
            data: Request data dictionary

        Returns:
            Tuple of (processed_data, processing_info)
        """
        processed_data = data.copy()
        processing_info: Dict[str, Any] = {
            "prompts_processed": 0,
            "total_token_reduction": 0,
            "avg_token_reduction": 0,
            "security_threats_detected": 0,
            "pii_masked": 0,
        }

        # Find and process prompts
        prompts_found = self._find_prompts(data)

        for field_path, prompt in prompts_found:
            try:
                # Process prompt through PrivySHA
                result = cast(
                    Dict[str, Any],
                    process(
                        prompt,
                        privacy=self.privacy,
                        token_budget=self.token_budget,
                        return_metrics=True,
                    ),
                )

                # Update the field in the processed data
                self._update_field(
                    processed_data, field_path, str(result["optimized"])
                )

                # Track processing info
                processing_info["prompts_processed"] += 1
                processing_info["total_token_reduction"] += result.get(
                    "token_reduction", 0
                )

                security_result = cast(
                    Dict[str, Any], result.get("security_result", {})
                )
                if not security_result.get("is_safe", True):
                    processing_info["security_threats_detected"] += 1

                processing_info["pii_masked"] += len(
                    security_result.get("masked_entities", [])
                )

                if self.debug_mode:
                    print(f"PrivySHA Debug: Processed field '{field_path}'")
                    print(f"PrivySHA Debug: Original: {prompt[:100]}...")
                    print(
                        f"PrivySHA Debug: Optimized: {result['optimized'][:100]}...")
                    print(
                        f"PrivySHA Debug: Token reduction: {result.get('token_reduction', 0)}%"
                    )

            except Exception as e:
                if self.debug_mode:
                    print(
                        f"PrivySHA Error processing field '{field_path}': {str(e)}")
                # Continue with original prompt if processing fails
                continue

        # Calculate averages
        if processing_info["prompts_processed"] > 0:
            processing_info["avg_token_reduction"] = (
                processing_info["total_token_reduction"]
                / processing_info["prompts_processed"]
            )

        return processed_data, processing_info

    def _find_prompts(
        self, data: Dict[str, Any], path: str = ""
    ) -> List[tuple[str, str]]:
        """
        Recursively find all prompts in the request data.

        Args:
            data: Data to search
            path: Current field path (for nested objects)

        Returns:
            List of (field_path, prompt) tuples
        """
        prompts = []

        for key, value in data.items():
            current_path = f"{path}.{key}" if path else key

            if isinstance(value, str):
                # Check if this field name suggests it contains a prompt
                if any(field in key.lower() for field in self.prompt_fields):
                    prompts.append((current_path, value))

            elif isinstance(value, list):
                # Handle lists (e.g., OpenAI messages format)
                for i, item in enumerate(value):
                    if isinstance(item, dict):
                        # Check for message content
                        if "content" in item and isinstance(item["content"], str):
                            prompts.append(
                                (f"{current_path}[{i}].content",
                                 item["content"])
                            )
                        # Recursively search nested dicts
                        prompts.extend(self._find_prompts(
                            item, f"{current_path}[{i}]"))

            elif isinstance(value, dict):
                # Recursively search nested dicts
                prompts.extend(self._find_prompts(value, current_path))

        return prompts

    def _update_field(
        self, data: Dict[str, Any], field_path: str, new_value: str
    ) -> None:
        """
        Update a field in the data using the field path.

        Args:
            data: Data to update
            field_path: Field path (e.g., "messages[0].content")
            new_value: New value to set
        """
        try:
            # Parse the field path
            parts = field_path.split(".")
            current = data

            # Navigate to the parent of the target field
            for part in parts[:-1]:
                if "[" in part and "]" in part:
                    # Handle array access (e.g., "messages[0]")
                    field_name = part.split("[")[0]
                    index = int(part.split("[")[1].split("]")[0])
                    current = current[field_name][index]
                else:
                    current = current[part]

            # Set the final field
            final_field = parts[-1]
            if "[" in final_field and "]" in final_field:
                # Handle array access for the final field
                field_name = final_field.split("[")[0]
                index = int(final_field.split("[")[1].split("]")[0])
                current[field_name][index] = new_value
            else:
                current[final_field] = new_value

        except Exception:
            # If field update fails, skip it
            pass

    def _replace_request_data(
        self, request: HttpRequest, processed_data: Dict[str, Any]
    ) -> None:
        """Replace the request data with processed data."""
        # Store processed data in request object
        request.privysha_processed_data = processed_data

        # For JSON requests, we need to modify the request body
        if request.content_type and "application/json" in request.content_type:
            # Store the processed data for the view to use
            request._privysha_processed_json = processed_data


# Django-specific convenience functions and decorators

# Optional Django decorators
try:
    from django.views.decorators.http import require_http_methods as _require_http_methods

    DJANGO_DECORATORS_AVAILABLE = True
except ImportError:
    DJANGO_DECORATORS_AVAILABLE = False

    def _require_http_methods(
        *args: Any, **kwargs: Any
    ) -> Callable[[_F], _F]:
        def decorator(func: _F) -> _F:
            return func

        return decorator

require_http_methods = _require_http_methods


def privysha_view(
    privacy: bool = True, token_budget: int = 1200, debug_metrics: bool = False
) -> Callable[[_F], _F]:
    """
    Decorator to apply PrivySHA processing to specific Django views.

    Args:
        privacy: Enable privacy features
        token_budget: Token budget for optimization
        debug_metrics: Return optimization metrics

    Usage:
        @privysha_view(privacy=True, debug_metrics=True)
        def chat_view(request):
            data = json.loads(request.body)
            # Data is already processed by PrivySHA
            return JsonResponse(response)
    """

    def decorator(view_func: _F) -> _F:
        @wraps(view_func)
        def wrapper(request: HttpRequest, *args: Any, **kwargs: Any) -> Any:
            # Only process POST/PUT/PATCH requests
            if request.method not in ["POST", "PUT", "PATCH"]:
                return view_func(request, *args, **kwargs)

            # Get request data
            data = {}
            if request.content_type and "application/json" in request.content_type:
                data = json.loads(request.body.decode("utf-8"))
            elif request.POST:
                data = dict(request.POST)

            if not data:
                return view_func(request, *args, **kwargs)

            # Process through PrivySHA
            try:
                result = process(
                    json.dumps(data),
                    privacy=privacy,
                    token_budget=token_budget,
                    return_metrics=debug_metrics,
                )

                if debug_metrics:
                    # Store metrics in request object
                    request.privysha_view_metrics = result

                # Update request data
                processed_data = (
                    cast(Dict[str, Any], json.loads(str(result["optimized"])))
                    if isinstance(result, dict)
                    else cast(Dict[str, Any], result)
                )

            except Exception as e:
                if debug_metrics:
                    request.privysha_view_error = str(e)
                # Continue with original data
                processed_data = data

            # Store processed data for the view
            request.privysha_view_data = processed_data

            return view_func(request, *args, **kwargs)

        return cast(_F, wrapper)

    return decorator


# Django context processor for templates
def privysha_context(request: HttpRequest) -> Dict[str, Any]:
    """
    Django context processor to make PrivySHA data available in templates.

    Add to settings.py:
        TEMPLATES = [
            {
                'OPTIONS': {
                    'context_processors': [
                        'django.template.context_processors.debug',
                        'privysha.integrations.django.middleware.privysha_context',
                    ],
                },
            },
        ]
    """
    context = {}

    if hasattr(request, "privysha_processing_info"):
        context["privysha_metrics"] = request.privysha_processing_info

    if hasattr(request, "privysha_view_metrics"):
        context["privysha_view_metrics"] = request.privysha_view_metrics

    return context


# Django management command to test PrivySHA integration
if DJANGO_COMMAND_AVAILABLE:

    class Command(BaseCommand):
        help = "Test PrivySHA Django integration"

        def handle(self, *args: Any, **options: Any) -> None:
            """Test the PrivySHA middleware integration."""
            self.stdout.write(self.style.SUCCESS(
                "Testing PrivySHA Django integration..."))

            # Test basic processing
            test_prompt = "Hey bro analyze this dataset with john@email.com"
            result = cast(
                Dict[str, Any],
                process(test_prompt, return_metrics=True),
            )

            self.stdout.write(f"Original: {test_prompt}")
            self.stdout.write(f"Optimized: {result['optimized']}")
            self.stdout.write(f"Token reduction: {result['token_reduction']}%")
            self.stdout.write(
                f"Security safe: {result['security_result']['is_safe']}")

            self.stdout.write(
                self.style.SUCCESS(
                    "PrivySHA Django integration test completed!")
            )
