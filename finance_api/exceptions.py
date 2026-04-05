from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    """Custom exception handler for better error responses"""
    response = exception_handler(exc, context)

    if response is not None:
        # Add custom error format
        if hasattr(response, "data"):
            if isinstance(response.data, dict):
                response.data = {
                    "success": False,
                    "error": response.data,
                    "status_code": response.status_code,
                }

    return response
