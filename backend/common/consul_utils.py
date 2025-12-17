import socket
from decouple import config
from .consul_client import ConsulClient

def get_ip_address():
    """Get the local IP address of the machine"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

def get_service(service_name):
    """
    Get service URL from Consul.
    Returns the address:port string or None if not found.
    """
    try:
        consul_host = config('CONSUL_HOST', default='consul')
        consul_port = config('CONSUL_PORT', default=8500, cast=int)
        
        client = ConsulClient(host=consul_host, port=consul_port)
        url = client.get_service_url(service_name)
        return url
    except Exception:
        return None

if __name__ == "__main__":
    print(f"IP: {get_ip_address()}")

