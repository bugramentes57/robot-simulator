INSTALLED_APPS = [
    # ... diğer uygulamalar ...
    'corsheaders',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # En üstte olmalı
    # ... diğer middleware'ler ...
]

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
]

CORS_ALLOW_CREDENTIALS = True 