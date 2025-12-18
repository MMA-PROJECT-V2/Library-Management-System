
import os
import sys
import logging
from decouple import config
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add backend directory to sys.path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from common.consul_client import ConsulClient

def verify_service_discovery():
    try:
        # Load Consul config from env or defaults
        host = config('CONSUL_HOST', default='127.0.0.1')
        port = config('CONSUL_PORT', default=8502, cast=int)
        
        logger.info(f"Connecting to Consul at {host}:{port}")
        consul = ConsulClient(host=host, port=port)
        
        services_to_check = [
            'books-service',
            'user-service',
            'loans-service',
            'notification-service'
        ]
        
        results = {}
        
        for service_name in services_to_check:
            logger.info(f"Resolving service: {service_name}")
            url = consul.get_service_url(service_name)
            
            if url:
                logger.info(f"✅ Found {service_name}: {url}")
                results[service_name] = url
            else:
                logger.error(f"❌ Could not find {service_name}")
                results[service_name] = None
                
        # Report
        print("\n--- Service Discovery Verification Report ---")
        all_found = True
        for name, url in results.items():
            status = "✅ FOUND" if url else "❌ MISSING"
            url_str = f"-> {url}" if url else ""
            print(f"{status} | {name} {url_str}")
            if not url:
                all_found = False
        
        if all_found:
            print("\n🎉 All services discovered successfully via Consul!")
        else:
            print("\n⚠️ Some services are missing. Make sure they are running and registered.")
            
    except Exception as e:
        logger.error(f"Verification failed: {e}")

if __name__ == "__main__":
    verify_service_discovery()
