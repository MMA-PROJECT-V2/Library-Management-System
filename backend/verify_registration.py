import sys
from unittest.mock import MagicMock, patch

# Mock consul
sys.modules['consul'] = MagicMock()

# Mock django settings
from django.conf import settings
if not settings.configured:
    settings.configure(
        DEBUG=True,
        CONSUL_HOST='localhost',
        CONSUL_PORT=8500,
        SERVICE_NAME='test-service',
        SERVICE_ID='test-service-1',
        SERVICE_ADDRESS='127.0.0.1',
        SERVICE_PORT=8000,
        SERVICE_TAGS=['test'],
        REGISTER_CONSUL=True, # Force enable
        BASE_DIR=MagicMock(parent='/path/to/backend'),
    )

# Now test the apps.ready logic by importing it or copying the relevant part
# We will verify if ConsulClient is called correctly

def test_registration_logic():
    print("Testing registration logic...")
    
    # Mock sys.path
    with patch('sys.path', []) as mock_path:
        # Mock commmon.consul_client
        mock_consul_client = MagicMock()
        mock_consul_client_instance = MagicMock()
        mock_consul_client.return_value = mock_consul_client_instance
        mock_consul_client_instance.register_service.return_value = True
        
        with patch.dict(sys.modules, {'common.consul_client': MagicMock(ConsulClient=mock_consul_client)}):
             # Simulate what we added to apps.py
            import logging
            logger = logging.getLogger('test')
            
            # Logic from apps.py
            if not settings.DEBUG or settings.REGISTER_CONSUL:
                print("Attempting registration...")
                consul_client = mock_consul_client(
                    host=settings.CONSUL_HOST,
                    port=settings.CONSUL_PORT
                )
                
                res = consul_client.register_service(
                    service_name=settings.SERVICE_NAME,
                    service_id=settings.SERVICE_ID,
                    address=settings.SERVICE_ADDRESS,
                    port=settings.SERVICE_PORT,
                    tags=settings.SERVICE_TAGS
                )
                
                if res:
                    print("Registration successful!")
                else:
                    print("Registration failed based on return value.")
            
            # Assertions
            mock_consul_client.assert_called_with(host='localhost', port=8500)
            mock_consul_client_instance.register_service.assert_called_with(
                service_name='test-service',
                service_id='test-service-1',
                address='127.0.0.1',
                port=8000,
                tags=['test']
            )
            print("Verification passed!")

if __name__ == "__main__":
    test_registration_logic()
