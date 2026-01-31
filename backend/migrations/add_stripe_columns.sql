-- Add Stripe columns to clients table
ALTER TABLE clients ADD COLUMN stripe_customer_id TEXT UNIQUE;
ALTER TABLE clients ADD COLUMN stripe_subscription_id TEXT UNIQUE;
ALTER TABLE clients ADD COLUMN stripe_subscription_status TEXT DEFAULT 'active';