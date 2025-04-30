import requests
from requests.auth import HTTPBasicAuth
import logging
import urllib3
import json

# Desativar warnings de certificado self-signed
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configurações
CONSUL_URL = "http://localhost:8500/v1/catalog/service/my-service"
USERNAME = 'admin'
PASSWORD = 'admin'

# Config de logging
logging.basicConfig(filename='logs/client-log.txt', level=logging.INFO)

# Obter endereço do serviço via Consul
def find_server():
    try:
        resposta = requests.get(CONSUL_URL)
        dados = resposta.json()
        if not dados:
            print("Serviço não encontrado no Consul.")
            return None
        ip = dados[0]["ServiceAddress"] or dados[0]["Address"]
        porta = dados[0]["ServicePort"]
        return f"https://{ip}:{porta}"
    except Exception as e:
        print("Erro ao contactar o Consul:", e)
        return None
    
# Contactar o servidor com autenticação básica
def contact_server(url):
    try:
        resposta = requests.get(url, auth=HTTPBasicAuth(USERNAME, PASSWORD), verify=False)
        if resposta.status_code == 200:
            print("Resposta do servidor:", resposta.text)
            logging.info(f"Resposta do servidor: {resposta.text}")
        else:
            print("Erro ao contactar o servidor:", resposta.status_code, resposta.text)
            logging.error(f"Erro ao contactar o servidor: {resposta.status_code} {resposta.text}")
    except Exception as e:
        print("Erro ao contactar o servidor:", e)
        logging.error(f"Erro ao contactar o servidor: {e}")

if __name__ == "__main__":
    # Obter o endereço do servidor
    server_url = find_server()
    if server_url:
        print("Endereço do servidor:", server_url)
        logging.info(f"Endereço do servidor: {server_url}")
        # Contactar o servidor
        contact_server(server_url)
    else:
        print("Não foi possível encontrar o servidor.")