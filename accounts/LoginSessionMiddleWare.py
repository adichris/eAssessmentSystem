from django.contrib.sessions.models import Session


class LogInOutMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        user = request.user
        if user.is_authenticated:
            stored_session_key = user.session_key

            if stored_session_key and stored_session_key != request.session.session_key:
                try:
                    Session.objects.get(session_key=stored_session_key).delete()
                except Session.DoesNotExist:
                    pass

            user.session_key = request.session.session_key
            user.save()

        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response
