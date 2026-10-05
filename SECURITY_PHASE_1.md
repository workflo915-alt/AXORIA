# AXORIA — Security Phase 1

This branch introduces the first security hardening step without changing the public design yet.

## What changed

- Added `admin.html`, which uses **Supabase Auth (email + password)** instead of a password embedded in the storefront JavaScript.
- Added `supabase/security_phase_1.sql`, which removes broad anonymous write/read policies and protects orders/customer data with RLS.
- Public visitors keep read access only to storefront keys (`axoria_products`, `axoria_categories`, `axoria_reviews`).
- Public visitors may create orders, but cannot list/read/update/delete orders.
- Authenticated admin sessions may manage catalog data and orders.
- The old `axoria_admin_pin` and `axoria_admin_recovery` rows are deleted by the SQL migration.

## Rollout order — important

Do **not** apply the SQL migration before the admin Supabase Auth account exists.

1. In Supabase Dashboard → Authentication → Users, create the AXORIA owner/admin user manually.
2. In Supabase Authentication settings, disable public/self-service email sign-ups. In this Phase 1 model, every authenticated account has admin data privileges, so only the owner account must exist.
3. Open the branch version of `admin.html` and verify the Supabase email/password login works.
4. Run `supabase/security_phase_1.sql` in Supabase SQL Editor.
5. Re-test:
   - storefront loads products/categories;
   - a visitor can submit an order;
   - a visitor cannot read `orders`;
   - `admin.html` can read products/orders after login;
   - product edits and order status changes work only while authenticated.
6. Only after these checks, merge the branch and then remove the legacy inline PIN/recovery UI from `index.html`.

## Important limitations still open

- Checkout totals are still supplied by the browser. Phase 2 should validate product prices server-side before accepting an order.
- Reviews are still stored as one JSON value. Public review submission should later move to a dedicated moderated reviews table.
- Product images are still stored as URLs/data URLs in the product JSON. Phase 2/3 should move uploads to Supabase Storage.
- The public `index.html` still contains the legacy PIN/recovery code on this branch for compatibility during rollout. Once RLS is applied it no longer grants database privileges, but it should be removed from the storefront in the next commit.

## Rollback

If the migration is applied before the new admin flow is ready, do not re-enable broad anonymous policies. Instead, fix the authenticated admin login or temporarily manage data directly in Supabase Dashboard.
