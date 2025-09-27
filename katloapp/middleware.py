from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse

class AdminBusinessSeparationMiddleware:
    """
    Middleware to handle admin and business user separation
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if user is accessing business areas while being superuser
        if (request.user.is_authenticated and 
            request.user.is_superuser and 
            request.path.startswith('/dashboard')):
            
            messages.info(
                request, 
                'You are logged in as an admin. Consider using a separate business account for better experience.'
            )

        response = self.get_response(request)
        return response