# Database Setup Clarification

## Answer: You Need ONLY ONE PostgreSQL Database

### The Three Pricing Tiers Do NOT Need Separate Databases

The pricing cards on your dashboard show three subscription tiers:
- **Basic** - $25/month
- **Standard** - $50/month  
- **Advanced** - $100/month

**These are subscription tiers, NOT separate databases.**

### How It Works

All clients share **ONE PostgreSQL database**. The subscription tier is stored in the `tier` column of the `clients` table:

```python
# From app/models.py - Client model
tier = Column(SQLEnum(TierEnum), default=TierEnum.BASIC, nullable=False)
```

Tier values: `"basic"`, `"premium"` (which maps to Standard/Advanced)

### Database Architecture

- **ONE** PostgreSQL database service on Railway
- **ALL** clients (Basic, Standard, Advanced) use the **SAME** database
- **ONE** `DATABASE_URL` environment variable for the backend service
- Tier features are enforced in **application code**, not separate databases

### What You Should See

- **ONE** PostgreSQL service in Railway
- **ONE** `DATABASE_URL` environment variable in your backend service
- **ONE** database connection string

### If You See Multiple Databases

If there are multiple PostgreSQL services in your Railway project:

1. Delete the extra ones through Railway dashboard
2. Keep only ONE PostgreSQL service
3. Ensure the backend service has `DATABASE_URL` set (Railway should auto-inject it)

---

**Bottom Line: One database for everyone. Tier is just a column in the table, not separate databases.**
