import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ECM2434_A_2_202425.settings')
application = get_wsgi_application()
