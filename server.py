from http.server import HTTPServer, BaseHTTPRequestHandler
import ssl
import base64
import logging
import requests
import json

# Configurações do servidor
HOST = '0.0.0.0'  # O servidor estará acessível em todas as interfaces de rede
PORT = 4443       # Porta onde o servidor estará escutando
USERNAME = 'admin'  # Nome de utilizador para autenticação básica
PASSWORD = 'admin'  # Senha para autenticação básica

# Configuração de logs
logging.basicConfig(filename='logs/server-log.txt', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Função para registrar o serviço no Consul
def register_service():
    """
    Registra o serviço no Consul para que ele possa ser descoberto por outros clientes.
    O registro inclui informações como nome do serviço, endereço, porta e verificações de saúde.
    """
    url = "http://localhost:8500/v1/agent/service/register"
    payload = {
        "Name": "secure-server",  # Nome do serviço
        "ID": "secure-server-service",  # ID único do serviço
        "Address": "127.0.0.1",  # Endereço do serviço
        "Port": PORT,  # Porta do serviço
        "Check": {
            "HTTP": f"https://host.docker.internal:{PORT}/health",  # Use host.docker.internal
            "Method": "GET",
            "TLSSkipVerify": True,  # Ignorar verificação de certificado TLS
            "Interval": "10s",
            "Timeout": "5s"
        }
    }
    try:
        # Valida o payload antes de enviar
        logging.info("Payload enviado para o Consul: %s", json.dumps(payload, indent=4))
        
        # Envia o registro para o Consul
        response = requests.put(url, data=json.dumps(payload))
        response.raise_for_status()  # Levanta exceção para erros HTTP
        logging.info("Resposta do Consul: %s", response.text)
        print("Service registered with Consul.")
    except requests.exceptions.ConnectionError as e:
        logging.error("Erro de conexão ao registrar o serviço no Consul: %s", e)
    except requests.exceptions.HTTPError as e:
        logging.error("Erro HTTP ao registrar o serviço no Consul: %s", e)
    except Exception as e:
        logging.error("Erro inesperado ao registrar o serviço no Consul: %s", e)

# Classe que define o comportamento do servidor seguro
class SecureServer(BaseHTTPRequestHandler):
    """
    Classe que implementa um servidor HTTP seguro com autenticação básica.
    """
    def do_GET(self):
        """
        Lida com requisições GET. Verifica a autenticação e responde com uma mensagem.
        """
        logging.info("Requisição recebida: %s", self.path)
        if self.path == "/health":
            # Responde com status 200 para o health check
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")
            logging.info("Health check respondido com sucesso.")
            return

        auth_header = self.headers.get('Authorization')
        if auth_header is None or not self.authenticated(auth_header):
            logging.warning("Autenticação falhou para o cliente: %s", self.client_address)
            self.send_401()
            self.wfile.write(b'Unauthorized')
            return
        
        logging.info("Acesso autorizado de %s", self.client_address)
        self.send_response(200)
        self.end_headers()
        self.wfile.write("Servidor seguro diz: Olá cliente!".encode("utf-8"))
        logging.info("Resposta enviada para %s", self.client_address)

    def authenticated(self, auth_header):
        """
        Verifica se o cabeçalho de autenticação contém credenciais válidas.
        """
        try:
            metodo, credenciais = auth_header.split(" ", 1)
            cred_decodificadas = base64.b64decode(credenciais).decode("utf-8")
            user, pwd = cred_decodificadas.split(":", 1)
            return user == USERNAME and pwd == PASSWORD
        except Exception as e:
            logging.error("Erro ao processar autenticação: %s", e)
            return False

    def send_401(self):
        """
        Envia uma resposta 401 Unauthorized com cabeçalho de autenticação básica.
        """
        self.send_response(401)
        self.send_header('WWW-Authenticate', 'Basic realm=\"Acesso Restrito\"')
        self.end_headers()
        logging.info("Resposta 401 enviada para o cliente.")

if __name__ == "__main__":
    # Registra o serviço no Consul
    register_service()

    # Configura o contexto SSL
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile="certs/cert.pem", keyfile="certs/key.pem")

    # Cria o servidor seguro
    httpd = HTTPServer((HOST, PORT), SecureServer)
    httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
    
    logging.info("Servidor seguro iniciado em https://%s:%s", HOST, PORT)
    print(f"Servidor seguro iniciado em https://{HOST}:{PORT}")
    
    # Inicia o servidor
    httpd.serve_forever()