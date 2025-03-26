import json
import logging

logger = logging.getLogger("main.middleware")

class LogResponseMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        logger.info("LogResponseMiddleware initialized.")

    def __call__(self, request):
        response = self.get_response(request)

        # Try to pretty-print the response content if it's JSON
        try:
            if response.get("Content-Type", "").startswith("application/json"):
                response_content = json.dumps(
                    json.loads(response.content.decode("utf-8")),
                    indent=4,
                    ensure_ascii=False  # Allow Unicode characters
                )
            else:
                response_content = response.content.decode("utf-8")  # Fallback for non-JSON
        except Exception as e:
            response_content = f"[Error decoding content: {e}]"

        # Log or print the details
        # logger.info(
        #     "Method: %s | Path: %s | Status: %d | Response Size: %d bytes | Content:\n%s",
        #     request.method,
        #     request.path,
        #     response.status_code,
        #     len(response.content),
        #     response_content[:1000],  # Truncate for safety in production
        # )
        # print(
        #     f"Method: {request.method} | Path: {request.path} | Status: {response.status_code} | Response Size: {len(response.content)} bytes\nContent:\n{response_content}"
        # )

        return response
