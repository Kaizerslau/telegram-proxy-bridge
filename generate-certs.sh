#!/bin/bash
set -e

CERT_DIR="$(dirname "$0")/certs"
mkdir -p "$CERT_DIR"

if [ -f "$CERT_DIR/cert.pem" ] && [ -f "$CERT_DIR/key.pem" ]; then
    echo "Certificates already exist in $CERT_DIR/"
    exit 0
fi

openssl req -x509 -nodes -days 3650 -newkey rsa:2048 \
  -keyout "$CERT_DIR/key.pem" \
  -out "$CERT_DIR/cert.pem" \
  -subj "/C=RU/O=Telegram Proxy/CN=telegram-proxy"

echo "Self-signed certificates generated in $CERT_DIR/"
echo "  cert.pem — public certificate"
echo "  key.pem  — private key"
