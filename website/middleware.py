from django.conf import settings
from django.shortcuts import render


class SecurityHeadersMiddleware:
    """Apply security headers only in production (when DEBUG is False)."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Do nothing in development
        if settings.DEBUG:
            return response

        # Strict-Transport-Security (if served over HTTPS by the host)
        response.setdefault('Strict-Transport-Security', 'max-age=31536000; includeSubDomains; preload')

        # Clickjacking protection
        response.setdefault('X-Frame-Options', 'DENY')

        # MIME sniffing protection
        response.setdefault('X-Content-Type-Options', 'nosniff')

        # Referrer policy
        response.setdefault('Referrer-Policy', 'same-origin')

        # Basic Content Security Policy (allow self, and Google reCAPTCHA in prod)
        csp = (
            "default-src 'self'; "
            "script-src 'self' https://www.google.com/recaptcha/ https://www.gstatic.com/; "
            "frame-src 'self' https://www.google.com/recaptcha/; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "connect-src 'self'; "
            "object-src 'none'"
        )
        response.setdefault('Content-Security-Policy', csp)

        return response


class FriendlyErrorMiddleware:
    """
    Gantikan halaman error Django default dengan tampilan ramah (404/500)
    bahkan saat DEBUG=True. Diterapkan di akhir MIDDLEWARE.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            response = self.get_response(request)
        except Exception:
            # Tangkap error tak tertangani sebagai 500
            return render(request, 'errors/500.html', status=500)

        # Lewati file statis/media agar tidak memblokir debug asset
        path = request.path or ''
        if settings.STATIC_URL and path.startswith(settings.STATIC_URL):
            return response
        if settings.MEDIA_URL and path.startswith(settings.MEDIA_URL):
            return response

        # Jika 404, render template kita
        if response.status_code == 404:
            return render(request, 'errors/404.html', {'path': path}, status=404)

        # Jika 500 dari view (jarang sampai sini), tetap render 500
        if response.status_code == 500:
            return render(request, 'errors/500.html', status=500)

        return response
