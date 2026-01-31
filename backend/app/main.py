# ... existing imports ...
try:
    from .stripe_routes import router as stripe_router
except ImportError:
    stripe_router = APIRouter()
    print("Stripe routes disabled - missing stripe package or env vars")

app.include_router(stripe_router, prefix="/api", tags=["stripe"])
```

<xai:function_call name="StrReplace">
<parameter name="path">/Users/nexteleven/Desktop/voice chatbot snippet/Snip/backend/app/main.py