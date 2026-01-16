#!/bin/bash
# Add PostgreSQL database to Railway project
# This requires Railway CLI to be authenticated

cd "$(dirname "$0")"

echo "Adding PostgreSQL database to Railway project..."

# Link to project if not already linked
railway link --project 02602f57-7c35-468a-abb3-678af0f43fe1

# Add PostgreSQL database
railway add --database postgres

echo "Checking for DATABASE_URL variable..."
railway variables | grep -i DATABASE_URL

echo "Done! If DATABASE_URL is not visible, the database may need a moment to provision."
echo "Check Railway dashboard to verify the database service was created."
