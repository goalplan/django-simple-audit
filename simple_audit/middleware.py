# threadlocals middleware
from django.utils.deprecation import MiddlewareMixin
from django.utils.functional import SimpleLazyObject

from .models import AuditRequest
from . import settings


def get_actual_user(request):
    if request.user.is_authenticated:
        return request.user


class TrackingRequestOnThreadLocalMiddleware(MiddlewareMixin):
    """Middleware that gets various objects from the
    request object and saves them in thread local storage."""

    def _get_ip(self, request):
        # get real ip
        if "x-forwarded-for" in request.headers:
            ip = request.headers["x-forwarded-for"]
        elif 'HTTP_X_FORWARDED_FOR' in request.META:
            ip = request.META['HTTP_X_FORWARDED_FOR']
        elif "Client-IP" in request.META:
            ip = request.META["Client-IP"]
        else:
            ip = request.META["REMOTE_ADDR"]
        ip = ip.split(",")[0]
        return ip

    def process_request(self, request):
        if request.method == "GET":
            return

        if not request.user.is_anonymous:
            ip = self._get_ip(request)
            user = SimpleLazyObject(lambda: get_actual_user(request))
            AuditRequest.new_request(request.get_full_path(), user, ip)
        else:
            if settings.DJANGO_SIMPLE_AUDIT_REST_FRAMEWORK_AUTHENTICATOR:
                user_auth_tuple = settings.DJANGO_SIMPLE_AUDIT_REST_FRAMEWORK_AUTHENTICATOR().authenticate(
                    request
                )

                if user_auth_tuple is not None:
                    user, token = user_auth_tuple
                    ip = self._get_ip(request)
                    AuditRequest.new_request(request.get_full_path(), user, ip)

    def process_response(self, request, response):
        AuditRequest.cleanup_request()
        return response
