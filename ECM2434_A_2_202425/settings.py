import os
from pathlib import Path

# 1️⃣ Base Directory
BASE_DIR = Path(__file__).resolve().parent.parent

# 2️⃣ Security Settings
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'your-secret-key')
DEBUG = True # Change to False in production


ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', '*').split(',')
TIME_ZONE = 'Europe/London'

# 3️⃣ Installed Apps
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',
    'debug_toolbar',

    # Third-party apps
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',

    # Your Django apps
    'bingo',
]

# 4️⃣ Middleware
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware', 
    'django.middleware.security.SecurityMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware', # Allow frontend requests
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# 5️⃣ CORS Settings (Allow Frontend to Access Backend)
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3002",  
    "http://127.0.0.1:3002",
    "http://localhost:3000",  
    "http://127.0.0.1:3000",
    "http://localhost:3001",  
    "http://127.0.0.1:3001",
    "http://localhost:3003",  
    "http://127.0.0.1:3003"

]


CORS_ALLOW_ALL_ORIGINS = True  # Temporarily allow all origins
CORS_ALLOW_METHODS = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
CORS_ALLOW_HEADERS = ["*"]


CORS_ALLOWED_ALL_ORGINS = True

# 6️⃣ Django REST Framework Config
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication', 
        'rest_framework.authentication.TokenAuthentication',  # If using token-based auth
        'rest_framework.authentication.SessionAuthentication',  # If using session-based auth
          # Use JWT tokens
    ),
}

# 7️⃣ Database Setup (Default: SQLite)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        #'NAME': BASE_DIR / "db.sqlite3",
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# 8️⃣ Password Validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
        'OPTIONS': {
            'user_attributes': ('username', 'email', 'first_name', 'last_name'),
            'max_similarity': 0.7,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
    {
        'NAME': 'bingo.validators.CustomPasswordValidator',
    },
]

AUTH_USER_MODEL = 'bingo.User' 

# 9️⃣ Static & Media Files
STATIC_URL = '/static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

INTERNAL_IPS = [
    "127.0.0.1",
]

# 🔟 Default Auto Field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# 1️⃣1️⃣ JWT Token Expiry
from datetime import timedelta
# Update the JWT settings to include role in the token payload
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': False,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    'JTI_CLAIM': 'jti',
    'USER_AUTHENTICATION_RULE': 'ECM2434_A_2_202425.auth_utils.custom_user_authentication_rule',
}

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],  # You can modify this if needed
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES':(
        'ECM2434_A_2_202425.auth_utils.CustomJWTAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    )
}

ROOT_URLCONF = 'ECM2434_A_2_202425.urls'
print(f"Database location: {os.path.join(BASE_DIR, 'db.sqlite3')}")
print(f"Does database file exist: {os.path.exists(os.path.join(BASE_DIR, 'db.sqlite3'))}")

AUTHENTICATION_BACKENDS = [
    'bingo.backends.SpecialUserBackend',  # Change 'bingo' to your app name
    'django.contrib.auth.backends.ModelBackend',  # Keep the default backend as fallback
]

SSTATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),  # This path needs to match the directory you created
]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')  # For collected static files


# Email settings for development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'noreply@yourgame.com'