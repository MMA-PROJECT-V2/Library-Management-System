import consul
import logging

logger = logging.getLogger(__name__)

class ConsulClient:
    def __init__(self, host='127.0.0.1', port=8502):
        try:
            self.client = consul.Consul(host=host, port=port)
        except Exception as e:
            logger.error(f"Failed to connect to Consul agent at {host}:{port}: {e}")
            self.client = None

    def register_service(self, service_name, service_id, address, port, tags=None):
        if not self.client:
            logger.warning("Consul client not initialized. Skipping registration.")
            return False
            
        try:
            # Basic HTTP health check
            check = consul.Check.http(f'http://{address}:{port}/health/', interval='10s', timeout='5s')
            
            self.client.agent.service.register(
                name=service_name,
                service_id=service_id,
                address=address,
                port=port,
                tags=tags,
                check=check
            )
            logger.info(f"Successfully registered service {service_name} ({service_id}) with Consul.")
            return True
        except Exception as e:
            logger.error(f"Failed to register service {service_name} with Consul: {e}")
            return False

    def deregister_service(self, service_id):
        if not self.client:
            logger.warning("Consul client not initialized. Skipping deregistration.")
            return False

        try:
            self.client.agent.service.deregister(service_id)
            logger.info(f"Successfully deregistered service {service_id} from Consul.")
            return True
        except Exception as e:
            logger.error(f"Failed to deregister service {service_id} from Consul: {e}")
            return False

    def get_service_url(self, service_name):
        """
        Discover service URL from Consul.
        Returns the address:port of a healthy instance of the service.
        """
        if not self.client:
            logger.warning("Consul client not initialized. Cannot discover service.")
            return None

        try:
            # Get all services with the given name
            index, services = self.client.health.service(service_name, passing=True)
            
            if not services:
                logger.warning(f"No healthy instances found for service: {service_name}")
                return None
            
            # Simple load balancing: pick the first one (or random)
            # For now, just pick the first one
            service = services[0]['Service']
            address = service['Address']
            port = service['Port']
            
            # If address is empty (sometimes happens with agent registration), use node address
            if not address:
                address = services[0]['Node']['Address']
            
            return f"http://{address}:{port}"
            
        except Exception as e:
            logger.error(f"Failed to discover service {service_name}: {e}")
            return None
