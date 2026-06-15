#!/bin/bash
set -e

CERT_DIR="$(dirname "$0")/certs"
mkdir -p "$CERT_DIR"

CN="${1:-telegram-proxy}"

openssl req -x509 -nodes -days 3650 -newkey rsa:2048 \
  -keyout "$CERT_DIR/key.pem" \
  -out "$CERT_DIR/cert.pem" \
  -subj "/C=RU/O=Telegram Proxy/CN=$CN" \
  -addext "subjectAltName=IP:$CN,DNS:$CN"

echo "Self-signed certificates generated in $CERT_DIR/"
echo "  CN: $CN"
echo "  cert.pem — public certificate"
echo "  key.pem  — private key"
