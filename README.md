
# Mini Sistema Distribuído com Descoberta de Serviço e Comunicação Segura

## Descrição
**Trabalho de faculdade** que implementa um sistema distribuído com **comunicação segura via SSL/TLS** e **autenticação básica**. O serviço é registrado no **Consul**, permitindo que o cliente localize dinamicamente o servidor e se conecte de forma segura.

### Arquitetura
- **Servidor**: Um servidor HTTP simples protegido por SSL/TLS com autenticação básica.
- **Cliente**: Um cliente que consulta o Consul para descobrir o endereço do servidor e fazer uma requisição HTTPS autenticada.
- **Consul**: Usado para registrar o serviço e permitir que o cliente o localize dinamicamente.

## Tecnologias Usadas
- **Python**: Linguagem utilizada para implementar o servidor e cliente.
- **Consul**: Para registrar e descobrir serviços dinamicamente.
- **SSL/TLS (Self-signed Certificate)**: Para proteger a comunicação entre cliente e servidor.
- **Requests (Python Library)**: Para fazer requisições HTTP de maneira simples no cliente.

## Estrutura do Projeto
```
/projeto-consul
│
├── certs/
│   ├── cert.pem
│   └── key.pem
├── servidor.py
├── cliente.py
├── logs/
│   ├── server-log.txt
│   └── client-log.txt
├── Dockerfile
└── README.md
```

## Como Executar o Sistema

### 1. Instalar dependências
Certifique-se de ter as bibliotecas necessárias instaladas:

```bash
pip install requests
```

### 2. Gerar Certificados SSL (Windows)
Se você estiver no **Windows**, siga os passos abaixo para gerar os certificados necessários para comunicação segura:

#### Passos:
1. **Instalar o OpenSSL**:
   - Baixe o **OpenSSL** [aqui](https://slproweb.com/products/Win32OpenSSL.html) e instale o pacote adequado para o seu sistema (versão 32 ou 64 bits).
   - Adicione o **OpenSSL** ao seu **path de ambiente** do sistema.

2. **Gerar os Certificados**:
   Abra o **Prompt de Comando** no Windows (ou **PowerShell**) e execute o seguinte comando:

   ```bash
   openssl req -x509 -newkey rsa:4096 -nodes -keyout certs/key.pem -out certs/cert.pem -days 365 -subj "/CN=localhost"
   ```

   Isso criará os arquivos `cert.pem` (certificado) e `key.pem` (chave privada) dentro da pasta `certs/`.

### 3. Rodar o Consul
Inicie o Consul com o seguinte comando no Docker:

```bash
docker run -d -p 8500:8500 --name consul consul:1.15.4
```

A interface web do Consul estará disponível em [http://localhost:8500](http://localhost:8500).

### 4. Iniciar o Servidor
No terminal, execute o servidor Python:

```bash
python servidor.py
```

O servidor irá registrar-se no Consul e ficará acessível via HTTPS (com um certificado self-signed) na URL `https://localhost:4443`.

### 5. Iniciar o Cliente
Em um terminal separado, execute o cliente:

```bash
python cliente.py
```

O cliente irá consultar o Consul para localizar o servidor, fazer uma requisição HTTPS com autenticação básica e exibir a resposta do servidor.

### 6. Verificando os Logs
O servidor irá registrar as interações no arquivo `logs/server-log.txt` e o cliente em `logs/client-log.txt`. Você pode verificar os logs para monitorar a comunicação entre o cliente e o servidor.

## Logs de Execução

### Servidor:
O servidor gera logs das interações com os clientes e registra os acessos autenticados no arquivo `server-log.txt`.

### Cliente:
O cliente gera logs da resposta do servidor e do processo de descoberta do servidor no Consul em `client-log.txt`.

## Conclusão
Este sistema implementa uma comunicação segura entre cliente e servidor utilizando SSL/TLS e autenticação básica. A descoberta dinâmica de serviços é gerida pelo Consul, e os logs das interações são mantidos para auditoria.

---

## Melhorias Futuras
- **Escalabilidade**: Integrar múltiplas instâncias do servidor com Consul para balanceamento de carga.
- **Melhoria de Autenticação**: Implementação de autenticação baseada em tokens ou OAuth.
- **Resiliência**: Adicionar verificações de saúde para garantir a disponibilidade contínua do serviço.

