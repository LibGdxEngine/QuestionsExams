from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponse

class CorsMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.method == "OPTIONS":
            origin = request.headers.get("Origin")
            if origin:
                response = HttpResponse()
                response["Access-Control-Allow-Origin"] = origin
                response["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
                response["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
                response["Access-Control-Max-Age"] = "3600"  # Optional: How long the results of a preflight request can be cached
                return response
        return None

    def process_response(self, request, response):
        origin = request.headers.get("Origin")
        response["Access-Control-Allow-Origin"] = origin if origin else ""
        response["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        response["Vary"] = "Origin"  # Important for caching
        return response

from django.http import HttpResponseForbidden
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from collections import defaultdict
import time


class DDosMiddleware(MiddlewareMixin):
    def __init__(self, get_response=None):
        super().__init__(get_response)
        self.requests = defaultdict(list)

    def process_request(self, request):
        # Get the client's IP address
        ip_address = request.META.get('REMOTE_ADDR')

        # If the IP address has made too many requests in a short time, block it
        if ip_address in self.requests:
            request_times = self.requests[ip_address]
            current_time = time.time()

            # Remove requests older than the allowed time window
            self.requests[ip_address] = [t for t in request_times if t > current_time - settings.DDOS_TIME_WINDOW]

            # If the number of requests exceeds the threshold, block the IP
            if len(self.requests[ip_address]) > settings.DDOS_REQUEST_THRESHOLD:
                return HttpResponseForbidden("Too many requests")

        # Add the current request time to the list
        self.requests[ip_address].append(time.time())

        return None
