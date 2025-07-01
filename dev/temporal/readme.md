https://blog.taigrr.com/blog/setting-up-a-production-ready-temporal-server/

- Temporal Server – runs Temporal’s core services (History, Matching) in one container. We will use the official
  temporalio/auto-setup image for convenience, which launches all services in one process and auto-initializes the
  database schema docs.temporal.io.
- Temporal Web UI – runs in a separate container (temporalio/ui image) to provide a web interface for viewing workflows,
  tasks, and Temporal namespaces
- PostgreSQL – a single Postgres instance as Temporal’s persistence store (keeping workflow state, history, etc.). I
  recommend using a managed database for this, like DigitalOcean (Disclaimer: this is my personal RefLink to
  DigitalOcean) to ensure uptime and reliability.
- NGINX – runs on the host as a reverse proxy. It will terminate TLS (HTTPS), forwarding requests to the Temporal WebUI
  container, and provide Basic Auth support.

### Install docker & docker compose
```bash
# Add Docker's official GPG key:
sudo apt-get update
sudo apt-get install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# Add the repository to Apt sources:
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/debian \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update


sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

### Install other dependencies
```bash
apt install nginx python3-certbot-nginx apache2-utils golang
go install github.com/fullstorydev/grpcurl/cmd/grpcurl@latest
curl -L 'https://temporal.download/cli/archive/latest?platform=linux&arch=amd64' > x.tar.gz
mv temporal /usr/bin
rm LICENSE x.tar.gz
```

### Create temporal databases. 

```sql
CREATE DATABASE temporal;
CREATE DATABASE temporal_visibility;

-- create user on Google cloud sql 

-- Connect to the temporal database first:
\c temporal

GRANT CONNECT ON DATABASE temporal TO temporal;
GRANT USAGE ON SCHEMA public TO temporal;
GRANT CREATE ON SCHEMA public TO temporal;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO temporal;

\c temporal_visibility

GRANT CONNECT ON DATABASE temporal_visibility TO temporal;
GRANT USAGE ON SCHEMA public TO temporal;
GRANT CREATE ON SCHEMA public TO temporal;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO temporal;
```

```bash
mkdir certs && cd certs
openssl genrsa -out rootCA.key 2048
openssl req -x509 -new -nodes -key rootCA.key -sha256 -days 3650 -out rootCA.pem
#You can adjust the expiration time or keysize as you wish.

#Create a client and server key:

openssl genrsa -out client.key 2048
openssl genrsa -out server.key 2048
#Now, using our RootCA, we’ll mint some certificates. Let’s start by creating some Certificicate Signing Request (.csr) files:

openssl req -new -key server.key -out server.csr -config server.cnf
```