import requests
import json

def clean_server(node_url: str, skip_delete: bool = False, skip_stop: bool = False):
    """ Metodo para eliminar todo el contenido dentro del protipo de la plataforma de OaaS Node.
    
    Steps: 
    1. Comprobar si hay instancias en la plataforma
    2. Parar todas las instancias que estan "running"
    3. Borrar todas las instancias.
    4. Comprobar si hay repositorios de algoritmos en la plataforma
    5. Borrar todos los repositorios de algoritmos.
    6. Ultima comprobación de que todo se ha borrado correctamente
    
    Parameters:
        node_url (str): URL del nodo de la plataforma
        skip_delete (bool): Flag para saltar el borrado de instancias
        skip_stop (bool): Flag para saltar el stop de instancias
        
    Raises:
        Exception: _description_
        Exception: _description_
    """
    
    # 1. Comprobar si hay instancias en la plataforma
    try: 
        response = requests.get(node_url + '/instances')

        if response.status_code == 200:
            data = response.json()  # Parse JSON data into a dictionary
            print(json.dumps(data, indent=4))  # Pretty-print the JSON data
        else:
            raise Exception("Failed to retrieve data")
        
        ## Check field "items" size in the response. If it is 0, nothing to do, if it is > 0, we can continue wipping
        if len(data['items']) > 0:
                # 2. Parar todas las instancias que estan "running"
                for item in data['items']:
                    if item['status'] == 'running':
                        # DELETE /instances/{instance_id}/stop
                        if not skip_stop:
                            response = requests.delete(node_url + '/instances/' + str(item['instanceId']) + '/stop')
                        
                            if response.status_code == 200:
                                print("Instance " + str(item['instanceId']) + " stopped")
                            else:
                                raise Exception("Failed to stop instance " + str(item['instanceId']))
                        else:
                            print("Instance " + str(item['instanceId']) + " skipped to stop")
                        
                        # 3. Borrar todas las instancias.
                        # DELETE /instances/{instance_id}
                        if not skip_delete:
                            response = requests.delete(node_url + '/instances/' + str(item['instanceId']) + '/delete')
                        
                            if response.status_code == 200:
                                print("Instance " + str(item['instanceId']) + " deleted")
                            else:
                                raise Exception("Failed to delete instance " + str(item['instanceId']))
                        else:
                            print("Instance " + str(item['instanceId']) + " skipped to delete")
    except Exception as e:
        print(e)
        return
    
    # 4. Comprobar si hay repositorios de algoritmos en la plataforma
    try:
        response = requests.get(node_url + '/images')

        if response.status_code == 200:
            data = response.json()  # Parse JSON data into a dictionary
            print(json.dumps(data, indent=4))  # Pretty-print the JSON data
        else:
            raise Exception("Failed to retrieve data")
        
        ## Check field "items" size in the response. If it is 0, nothing to do, if it is > 0, we can continue wipping
        if len(data['items']) > 0:
             for item in data['items']:
                # 5. Borrar todos los repositorios de algoritmos.
                # DELETE /algorithmRepositories
                if not skip_delete:
                    url = node_url + '/images/' + str(item['imageId'])
                    print("Deleting algorithm repositories: " + url)
                    response = requests.delete(url)

                    if response.status_code == 200:
                        print("Algorithm repositories deleted")
                    else:
                        print("Error: " + str(response.status_code) + " - " + str(response))
                        raise Exception("Failed to delete algorithm repositories")
                else:
                    print(f"Algorithm {str(item['imageId'])} repositories skipped to delete")
        print("Server cleaned")
    except Exception as e:
        print(e)
        return
    
def init_repositories_and_instances_for_use_cases(node_url: str):
    """ For both use cases, create each repository and instance needed for the use case to run.
    * Network Operation: NDT 
    * Network Planning: Edge Planning algorithm
    """
    
    try:
        # 1. NDT
        print("Creating NDT repository and instance")
        # Damos de alta el NDT como repositorio de tipo general (no algoritmos inside)
        req = {
            "name": "NDT Repository - test",
            "description": "Network Digital Twin based in Net2Plan",
            "imageUrl": "elighthouse-ndt",
            "type": "java"
        }
        #print(req)

        # Sent a POST to /algorithmRepository
        response = requests.post(node_url + '/images', json=req)

        if response.status_code == 200 or response.status_code == 201:
            data = response.json()  # Parse JSON data into a dictionary
            print(json.dumps(data, indent=4))  # Pretty-print the JSON data
        else:
            data = response.json()
            print(json.dumps(data, indent=4))
            raise Exception("Failed to retrieve data")

        repository_ndt_id = data['imageId']

        # Creamos una nueva instancia del NDT
        req = {
            "name": "NDT Repository Instance - test",
            "description": "Network Digital Twin based in Net2Plan",
            "quotaInformation": {
                "cpu": "1 core",
                "diskSpace": "10GB",
                "networkBandwidth": "100Mbps",
                "ram": "512MB"
            },
            "image_id": repository_ndt_id
        }
        #print(req)

        # Sent a POST to /algorithmRepository
        response = requests.post(node_url + '/instances', json=req)

        if response.status_code == 200 or response.status_code == 201:
            data = response.json()  # Parse JSON data into a dictionary
            print(json.dumps(data, indent=4))  # Pretty-print the JSON data
        else:
            data = response.json()
            print(json.dumps(data, indent=4))
            raise Exception("Failed to retrieve data")

        # Autommatically start the instance... nothing to do
        print("NDT Repository and Instance created")
        
        # 2. Edge Planning algorithm
        print("Creating EDGE Planning repository and instance")
        # Damos de alta el algoritmo de EDGE Planning
        req = {
            "name": "EDGE Planning - test",
            "description": "Algorithm repository for EDGE Planning",
            "imageUrl": "optimaix/micro-nfplaning",
            "type": "matlab"
        }
        #print(req)

        # Sent a POST to /algorithmRepository
        response = requests.post(node_url + '/images', json=req)

        if response.status_code == 200 or response.status_code == 201:
            data = response.json()  # Parse JSON data into a dictionary
            print(json.dumps(data, indent=4))  # Pretty-print the JSON data
        else:
            data = response.json()
            print(json.dumps(data, indent=4))
            raise Exception("Failed to retrieve data")

        repository_algorithm_id = data['imageId']

        # Creamos una nueva instancia del EDGE Planning
        req = {
            "name": "Algorithm edge planning use case - test",
            "description": "algorithm for edge planning use case",
            "quotaInformation": {
                "cpu": "1 core",
                "diskSpace": "10GB",
                "networkBandwidth": "100Mbps",
                "ram": "512MB"
            },
            "image_id": repository_algorithm_id
        }
        #print(req)
        
        # Sent a POST to /algorithmRepository
        response = requests.post(node_url + '/instances', json=req)

        if response.status_code == 200 or response.status_code == 201:
            data = response.json()  # Parse JSON data into a dictionary
            print(json.dumps(data, indent=4))  # Pretty-print the JSON data
        else:
            data = response.json()
            print(json.dumps(data, indent=4))
            raise Exception("Failed to retrieve data")

        print("EDGE Planning Repository and Instance created")
    except Exception as e:
        print(e)
        return
    
if __name__ == "__main__":
    URL = 'http://localhost:5000'
    
    print("Cleaning server")
    clean_server(URL, skip_delete=False, skip_stop=False)
    print("Init repositories and instances for use cases")
    init_repositories_and_instances_for_use_cases(URL)
    print("End of script")
    