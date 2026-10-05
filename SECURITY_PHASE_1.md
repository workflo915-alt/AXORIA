# AXORIA — Security Phase 1

This branch introduces the first security hardening step without changing the public design.

## Completed

- Added `admin.html` using Supabase Auth (email + password).
- Disabled public self-service sign-ups in Supabase.
- Applied RLS so anonymous visitors can create orders but cannot read or modify customer orders.
- Re-created a clean `axoria_store` for the current AXORIA catalog with authenticated admin write access.
- Added a cleanup script at `scripts/phase1_cleanup.py` to remove the obsolete PIN/recovery/admin panel from the public `index.html`.

## Next branch action

Run the cleanup script on `security-phase-1`, verify the storefront and admin page, then merge the pull request.

The cleanup script also moves public review submission away from shared catalog JSON and expects a dedicated `review_submissions` table with insert-only anonymous access.

## Still open after Phase 1

- Validate checkout prices server-side before order insert.
- Move product images to Supabase Storage instead of data URLs.
- Add review moderation to `admin.html`.
- Split the single large `index.html` into maintainable CSS/JS modules.
- Add Meta Pixel/CAPI after checkout logic is hardened.
