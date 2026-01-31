# White-label URL changes – rollback

Embed snippet and docs now use **white-label URLs** (no Railway/Vercel in customer-facing snippet). The **API** URL in the snippet is `backend_public_url` (default `https://snip.mothership-ai.com`). The **widget** script URL stays on the current CDN default so existing installs keep working.

## If something breaks

1. **Roll back this change (one commit):**
   ```bash
   git log -1 --oneline   # note the commit hash, e.g. abc1234
   git revert abc1234 --no-edit
   git push origin main
   ```

2. **Or roll back to previous commit:**
   ```bash
   git reset --hard HEAD~1
   git push origin main --force
   ```
   (Only use if no one else has pulled; otherwise prefer `git revert`.)

3. **Override without code change:**  
   On Railway, set env vars:
   - `BACKEND_PUBLIC_URL` = your public API URL (e.g. `https://snip.mothership-ai.com`)
   - `WIDGET_CDN_URL` = your widget script URL (default remains current Vercel URL)

## What was changed

- **Backend:** Embed snippet uses `settings.backend_public_url` instead of hardcoded Railway URL.
- **Config:** Added `backend_public_url` (default snip.mothership-ai.com); `widget_cdn_url` default unchanged so widget keeps loading.
- **Dashboard:** Help and fallback snippets reference snip.mothership-ai.com for API; widget URL unchanged in examples so pasted code still works.
