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
logging.basicConfig(filename='logs/server-log.txt', level=logging.INFO)

# Função para registrar o serviço no Consul
def register_service():
    """
    Registra o serviço no Consul para que ele possa ser descoberto por outros clientes.
    O registro inclui informações como nome do serviço, endereço, porta e verificações de saúde.
    """
    url = "http://localhost:8500/v1/agent/service/register"
    payload = {
        "Name": "my-service",  # Nome do serviço
        "ID": "my-service-1",  # ID único do serviço
        "Address": "localhost",  # Endereço do serviço
        "Port": PORT,  # Porta do serviço
        "Check": {  # Configuração de health check
            "HTTP": f"https://localhost:{PORT}/health",  # URL para verificação de saúde
            "Method": "GET",  # Método HTTP usado para o health check
            "TLSSkipVerify": True,  # Ignorar verificação de certificado TLS
            "Interval": "10s",  # Intervalo entre verificações
            "Timeout": "5s"  # Tempo limite para a verificação
        }
    }
    try:
        # Envia o registro para o Consul
        response = requests.put(url, data=json.dumps(payload))
        response.raise_for_status()  # Levanta exceção para erros HTTP
        logging.info("Service registered with Consul.")
        print("Service registered with Consul.")
    except requests.exceptions.ConnectionError as e:
        logging.error(f"Erro de conexão ao registrar o serviço no Consul: {e}")
        print(f"Erro de conexão ao registrar o serviço no Consul: {e}")
    except requests.exceptions.HTTPError as e:
        logging.error(f"Erro HTTP ao registrar o serviço no Consul: {e}")
        print(f"Erro HTTP ao registrar o serviço no Consul: {e}")
    except Exception as e:
        logging.error(f"Erro inesperado ao registrar o serviço no Consul: {e}")
        print(f"Erro inesperado ao registrar o serviço no Consul: {e}")

# Classe que define o comportamento do servidor seguro
class SecureServer(BaseHTTPRequestHandler):
    """
    Classe que implementa um servidor HTTP seguro com autenticação básica.
    """
    def do_GET(self):
        """
        Lida com requisições GET. Verifica a autenticação e responde com uma mensagem.
        """
        auth_header = self.headers.get('Authorization')
        if auth_header is None or not self.authenticated(auth_header):
            self.send_401()
            self.wfile.write(b'Unauthorized')
            return
        
        logging.info(f"Acesso autorizado de {self.client_address}")
        self.send_response(200)
        self.end_headers()
        self.wfile.write("Servidor seguro diz: Olá cliente!".encode("utf-8"))
        logging.info(f"Resposta enviada para {self.client_address}")
        print(f"Resposta enviada para {self.client_address}")

    def authenticated(self, auth_header):
        """
        Verifica se o cabeçalho de autenticação contém credenciais válidas.
        """
        metodo, credenciais = auth_header.split(" ", 1)
        cred_decodificadas = base64.b64decode(credenciais).decode("utf-8")
        user, pwd = cred_decodificadas.split(":", 1)
        return user == USERNAME and pwd == PASSWORD

    def send_401(self):
        """
        Envia uma resposta 401 Unauthorized com cabeçalho de autenticação básica.
        """
        self.send_response(401)
        self.send_header('WWW-Authenticate', 'Basic realm=\"Acesso Restrito\"')
        self.end_headers()
        self.wfile.write(b"Autenticacao necessaria.")

if __name__ == "__main__":
    # Registra o serviço no Consul
    register_service()

    # Configura o contexto SSL
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile="certs/cert.pem", keyfile="certs/key.pem")

    # Cria o servidor seguro
    httpd = HTTPServer((HOST, PORT), SecureServer)
    httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
    
    print(f"Servidor seguro iniciado em https://{HOST}:{PORT}")
    logging.info(f"Servidor seguro iniciado em https://{HOST}:{PORT}")
    
    # Inicia o servidor
    httpd.serve_forever()

