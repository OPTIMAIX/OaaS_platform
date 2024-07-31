# Get fixed OaaSNode QuerySet for mock

from oaasplatform.nocrud import info

async def get_oaas_nodes():
    mock_oaas_nodes = [
        {
            "ipAddressOrDns": "localhost",
            "ipPort": 5000,
            "name": "oaas-node-1",
            "description": "OaaS Node 1",
            "ownerInfo": "OaaS Platform",
            "computationResources": await info.get_cpu_ram_info()
        }
    ]
    return mock_oaas_nodes
    