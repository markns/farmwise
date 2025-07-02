echo TEMPORAL_ADDRESS=temporal:7233  >> .env.ui
echo TEMPORAL_TLS_CA_DATA=$(cat certs/rootCA.pem | base64 -w0) > .env.ui
echo TEMPORAL_TLS_CERT_DATA=$(cat certs/client.crt | base64 -w0) >> .env.ui
echo TEMPORAL_TLS_KEY_DATA=$(cat certs/client.key | base64 -w0) >> .env.ui

