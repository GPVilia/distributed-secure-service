from http.server import HTTPServer, BaseHTTPRequestHandler
import ssl
import base64
import logging
import requests
import json

# Config
HOST = '0.0.0.0'
PORT = 4443
USERNAME = 'admin'
PASSWORD = 'admin'

# Logs
logging.basicConfig(filename='logs/server-log.txt', level=logging.INFO)


# Registar o serviço no Consul
def register_service():
    url = "http://localhost:8500/v1/agent/service/register"
    payload = {
        "Name": "my-service",
        "ID": "my-service-1",
        "Address": "localhost",
        "Port": PORT,
        "Check": {
            "HTTP": f"https://localhost:{PORT}/health",
            "Method": "GET",
            "TLSSkipVerify": True,
            "Interval": "10s",
            "Timeout": "5s"
        }
    }
    requests.put(url, data=json.dumps(payload))
    logging.info("Service registered with Consul.")
    print("Service registered with Consul.")

class SecureServer(BaseHTTPRequestHandler):
    def do_GET(self):
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
        metodo, credenciais = auth_header.split(" ", 1)
        cred_decodificadas = base64.b64decode(credenciais).decode("utf-8")
        user, pwd = cred_decodificadas.split(":", 1)
        return user == USERNAME and pwd == PASSWORD

    def send_401(self):
        self.send_response(401)
        self.send_header('WWW-Authenticate', 'Basic realm=\"Acesso Restrito\"')
        self.end_headers()
        self.wfile.write(b"Autenticacao necessaria.")

if __name__ == "__main__":
    # Registar o serviço no Consul
    register_service()

    # Criar o contexto SSL
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile="certs/cert.pem", keyfile="certs/key.pem")

    # Criar o servidor seguro
    httpd = HTTPServer((HOST, PORT), SecureServer)
    httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
    
    print(f"Servidor seguro iniciado em https://{HOST}:{PORT}")
    logging.info(f"Servidor seguro iniciado em https://{HOST}:{PORT}")
    
    # Iniciar o servidor
    httpd.serve_forever()

