#!/bin/bash
# Create customer account - run this script

curl -X POST https://snip-production.up.railway.app/api/clients \
  -H "Content-Type: application/json" \
  -d '{"email":"customer@example.com","company_name":"Customer Company","tier":"premium"}'
