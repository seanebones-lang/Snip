#!/bin/bash
# Create account for Dom and Tom - Tom Tancredi

curl -X POST https://snip-production.up.railway.app/api/clients \
  -H "Content-Type: application/json" \
  -d '{"email":"tomtancredi@gmail.com","company_name":"Dom and Tom","tier":"premium"}'
