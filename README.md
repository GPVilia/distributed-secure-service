
# Mini Sistema Distribuído com Descoberta de Serviço e Comunicação Segura

## Descrição da Atividade

Este projeto consiste na implementação de um **sistema distribuído simples** com descoberta de serviço e comunicação segura. O sistema é composto por dois serviços principais:

- **Cliente**: O cliente descobre dinamicamente o endereço do servidor via **Consul**.
- **Servidor**: O servidor exige autenticação básica (utilizando **utilizador** e **senha**) e protege a comunicação utilizando **SSL/TLS** (certificados autoassinados).

A comunicação entre cliente e servidor é feita via **HTTPS**, garantindo segurança. A descoberta do serviço é feita por meio de um **registro de serviço** no **Consul**.

## Tecnologias Usadas

- **Linguagem**: Python
- **Bibliotecas**: 
  - `http.server` para o servidor
  - `requests` para a interação com o Consul
  - `ssl` para a proteção via SSL/TLS
- **Consul**: Utilizado para a descoberta do serviço.
- **Certificados SSL**: Autoassinados, criados para garantir a comunicação segura entre cliente e servidor.
- **Docker**: Para execução do Consul (opcional).

## Como Executar o Sistema

### 1. **Instalar o Docker**:

Se não tiver o **Docker** instalado, siga as instruções do [site oficial](https://docs.docker.com/get-docker/) para instalar o Docker na sua máquina.

### 2. **Gerar os Certificados SSL**:

Para garantir a comunicação segura via **HTTPS**, será necessário gerar os certificados **SSL**. Para isso, execute o seguinte comando no seu terminal (com **OpenSSL** instalado):

```bash
openssl req -x509 -newkey rsa:4096 -keyout certs/key.pem -out certs/cert.pem -days 365 -nodes
```

Este comando cria dois ficheiros **PEM** (`key.pem` e `cert.pem`) que serão usados para proteger a comunicação entre o cliente e o servidor. Certifique-se de que o diretório `certs` existe antes de executar este comando.

### 3. **Rodar o Consul**:

O **Consul** será usado para registar e descobrir os serviços. Para isso, execute o seguinte comando para iniciar o Consul no Docker:

2 Opções de script:


Hashicorp/consul:1.15.4
```bash
docker run -d --name consul -p 8500:8500 -p 8600:8600 -p 8300:8300 -p 8301:8301 -p 8302:8302 -p 8600:8600/udp hashicorp/consul:1.15.4
```

Consul (Caso já tenha a imagem 1.15.4 instalada):
```bash
docker run -d --name consul -p 8500:8500 -p 8600:8600 -p 8300:8300 -p 8301:8301 -p 8302:8302 -p 8600:8600/udp consul:1.15.4
```

Depois de correr o comando, aceda à interface web do **Consul** em **[http://localhost:8500](http://localhost:8500)**.

### 4. **Rodar o Servidor Seguro**:

Com o Consul em execução, pode iniciar o **servidor** com o seguinte comando:

```bash
python servidor.py
```

Este servidor está protegido com **SSL/TLS** e exige autenticação básica para permitir o acesso.

### 5. **Rodar o Cliente**:

Com o servidor a funcionar, agora pode executar o **cliente** com o seguinte comando:

```bash
python cliente.py
```

O cliente irá descobrir dinamicamente o endereço do servidor via **Consul** e estabelecer uma comunicação segura.

### 6. **Verificar os Logs**:

O servidor mantém um ficheiro de **logs** (`server-log.txt`) onde é registado todo o processo de interação entre o cliente e o servidor. Certifique-se de verificar os logs para garantir que tudo está a funcionar como esperado.

### 7. **Verificar o Serviço no Consul**:

Aceda à interface do **Consul** em **[http://localhost:8500](http://localhost:8500)** e confirme que o serviço `my-service` foi registado corretamente. Na página de serviços, o serviço deve aparecer como **ativo**.

## Estrutura do Projeto

```
.
├── certs/
│   ├── cert.pem        # Certificado SSL
│   └── key.pem         # Chave privada SSL
├── logs/
│   ├── server-logs.txt # Logs do servidor
│   └── client-logs.txt # Logs do cliente
├── cliente.py          # Código do cliente
├── servidor.py         # Código do servidor
├── Dockerfile          # Ficheiro de configuração do Docker (se necessário)
└── README.md           # Este ficheiro
```

## Licença

Este código é parte de um **trabalho de faculdade** e está disponível para fins acadêmicos. Não deverá ser usado para outros fins sem a permissão adequada.

## Possíveis Erros e Soluções

1. **O Consul não está a iniciar**:
   - Certifique-se de que o **Docker** está a funcionar corretamente.
   - Verifique as portas que o Consul está a utilizar (8500, 8600, etc.) para garantir que não há conflitos.

2. **O cliente não consegue encontrar o servidor**:
   - Verifique se o Consul está a funcionar corretamente e se o serviço está registado.
   - Confirme se o cliente está a tentar aceder ao serviço correto.

3. **Erros ao executar os comandos SSL**:
   - Certifique-se de que o OpenSSL está instalado corretamente no seu sistema.
   - Verifique as permissões do diretório onde está a gerar os certificados.

---

⭐ Trabalho desenvolvido por: Gustavo Vília - 202327134 - GSC
