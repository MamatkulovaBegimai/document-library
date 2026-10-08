class ContentSecurityPolicyMiddleware:
    """Базалык CSP: XSS жана сырткы контентти чектөө.

    Google Fonts интерфейсте колдонулат, ал эми PDF Cloudflare R2 аркылуу
    iframe ичинде ачылышы мүмкүн, ошондуктан тиешелүү HTTPS булактарына
    так уруксат берилет.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        response['Content-Security-Policy'] = (
            "default-src 'self'; "
            "base-uri 'self'; "
            "form-action 'self'; "
            "frame-ancestors 'none'; "
            "object-src 'none'; "
            "script-src 'self'; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com data:; "
            "img-src 'self' data: https:; "
            "frame-src 'self' https:; "
            "connect-src 'self'; "
            "upgrade-insecure-requests"
        )
        return response
