import requests
from requests.auth import HTTPBasicAuth
import logging
import urllib3
import json

# Desativar warnings de certificado self-signed
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configurações do cliente
CONSUL_URL = "http://localhost:8500/v1/catalog/service/secure-server"  # URL para buscar o serviço no Consul
USERNAME = 'admin'  # Nome de usuário para autenticação básica
PASSWORD = 'admin'  # Senha para autenticação básica

# Configuração de logs
logging.basicConfig(filename='logs/client-log.txt', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Função para obter o endereço do servidor via Consul
def find_server():
    """
    Consulta o Consul para obter o endereço do serviço registrado.
    Retorna o endereço completo (URL) do servidor ou None se o serviço não for encontrado.
    """
    try:
        logging.info("Consultando o Consul para obter o serviço.")
        resposta = requests.get(CONSUL_URL)
        resposta.raise_for_status()
        dados = resposta.json()
        logging.info("Resposta do Consul: %s", json.dumps(dados, indent=4))
        if not dados:
            logging.warning("Serviço não encontrado no Consul.")
            return None
        ip = dados[0].get("ServiceAddress") or dados[0].get("Address")
        porta = dados[0]["ServicePort"]
        return f"https://{ip}:{porta}"
    except requests.exceptions.RequestException as e:
        logging.error("Erro ao contactar o Consul: %s", e)
        return None
    
# Função para contactar o servidor com autenticação básica
def contact_server(url):
    """
    Envia uma requisição GET ao servidor usando autenticação básica.
    Exibe e registra a resposta do servidor.
    """
    try:
        logging.info("Enviando requisição para o servidor: %s", url)
        resposta = requests.get(url, auth=HTTPBasicAuth(USERNAME, PASSWORD), verify=False)
        if resposta.status_code == 200:
            logging.info("Resposta do servidor: %s", resposta.text)
            print("Resposta do servidor:", resposta.text)
        else:
            logging.warning("Erro ao contactar o servidor: %s %s", resposta.status_code, resposta.text)
            print("Erro ao contactar o servidor:", resposta.status_code, resposta.text)
    except Exception as e:
        logging.error("Erro ao contactar o servidor: %s", e)
        print("Erro ao contactar o servidor:", e)

if __name__ == "__main__":
    # Obter o endereço do servidor
    server_url = find_server()
    if server_url:
        logging.info("Endereço do servidor encontrado: %s", server_url)
        print("Endereço do servidor:", server_url)
        # Contactar o servidor
        contact_server(server_url)
    else:
        logging.warning("Não foi possível encontrar o servidor.")
        print("Não foi possível encontrar o servidor.")