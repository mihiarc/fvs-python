import os
import yaml
import json

SPECIES_DIR = 'cfg/species'
COEFFS_PATH = 'docs/sn_height_diameter_coefficients.json'

with open(COEFFS_PATH, 'r') as f:
    coeffs = json.load(f)

updated = []
skipped = []

for fname in os.listdir(SPECIES_DIR):
    if not fname.endswith('.yaml'):
        continue
    path = os.path.join(SPECIES_DIR, fname)
    with open(path, 'r') as f:
        try:
            data = yaml.safe_load(f)
        except Exception as e:
            skipped.append((fname, f'YAML parse error: {e}'))
            continue
    code = data.get('metadata', {}).get('code')
    if not code:
        skipped.append((fname, 'No species code in metadata'))
        continue
    coeff = coeffs.get(code)
    if not coeff:
        skipped.append((fname, f'No coefficients for code {code}'))
        continue
    # Update height_diameter section
    hd = data.get('height_diameter', {})
    if 'curtis_arney' in hd:
        hd['curtis_arney']['p2'] = coeff['P2']
        hd['curtis_arney']['p3'] = coeff['P3']
        hd['curtis_arney']['p4'] = coeff['P4']
        hd['curtis_arney']['dbw'] = coeff['Dbw']
    if 'wykoff' in hd:
        hd['wykoff']['b1'] = coeff['Wykoff_B1']
        hd['wykoff']['b2'] = coeff['Wykoff_B2']
    data['height_diameter'] = hd
    with open(path, 'w') as f:
        yaml.dump(data, f, sort_keys=False)
    updated.append(fname)

print('Update summary:')
print('Updated files:')
for fname in updated:
    print('  -', fname)
if skipped:
    print('Skipped files:')
    for fname, reason in skipped:
        print(f'  - {fname}: {reason}') 