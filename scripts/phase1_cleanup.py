from pathlib import Path

path = Path('index.html')
text = path.read_text(encoding='utf-8')

forbidden = [
    'Kaltommohamed1965',
    'ADMIN_RECOVERY_ANSWER',
    'recoverAnswer',
    'adminTinyBtn',
    'openAdminGate(',
    'adminPanel',
    'axoria_admin_pin',
    'axoria_admin_recovery',
]

found = [marker for marker in forbidden if marker in text]
if found:
    raise SystemExit('Phase 1 cleanup incomplete; found legacy markers: ' + ', '.join(found))

required = [
    "sb.from('review_submissions').insert",
    '<meta name="viewport" content="width=device-width, initial-scale=1">',
    'admin.html',
]
missing = [marker for marker in required if marker not in text]
if missing:
    raise SystemExit('Phase 1 validation incomplete; missing expected markers: ' + ', '.join(missing))

print('Phase 1 storefront cleanup is already applied and validated.')
