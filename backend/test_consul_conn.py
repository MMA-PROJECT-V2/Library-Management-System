import consul
import sys

try:
    c = consul.Consul(host='127.0.0.1', port=8502)
    agent_info = c.agent.self()
    print(f"Successfully connected to Consul agent: {agent_info['Config']['NodeName']}")
    print(f"Member status: {agent_info['Member']['Status']}")
except Exception as e:
    print(f"Failed to connect to Consul: {e}")
    sys.exit(1)
