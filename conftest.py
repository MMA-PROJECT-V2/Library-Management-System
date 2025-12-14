import sys
import os

# Add the backend service directory to sys.path so that 'library_notifications_service' 
# can be imported as a top-level module (matching DJANGO_SETTINGS_MODULE)
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend', 'library_notifications_service'))
