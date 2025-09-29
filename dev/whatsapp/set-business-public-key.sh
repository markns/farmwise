#!/usr/bin/env bash

set -ex

set -a && source .env && set +a

echo $WHATSAPP_PHONE_ID
echo $WHATSAPP_TOKEN

# Get the absolute path of the directory containing this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
pem_content=$(< $SCRIPT_DIR/whatsapp_public.pem)

curl -X POST \
  https://graph.facebook.com/v23.0/$WHATSAPP_PHONE_ID/whatsapp_business_encryption \
  -H "Authorization: Bearer $WHATSAPP_TOKEN" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  --data-urlencode business_public_key="$pem_content"
