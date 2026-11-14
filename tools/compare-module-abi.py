"""Compare captured vendor-module imports to a built kernel's symbol CRCs."""
import argparse
import json
from pathlib import Path

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('symvers', type=Path)
p.add_argument('modules', nargs='+', type=Path)
p.add_argument('--output', type=Path, required=True)
a = p.parse_args()
symbols = {}
for line in a.symvers.read_text().splitlines():
    fields = line.split()
    if len(fields) >= 3:
        symbols[fields[1]] = int(fields[0], 16)
vendor_exports = {}
modules = []
for path in a.modules:
    value = json.loads(path.read_text())
    modules.extend(value if isinstance(value, list) else [value])
for module in modules:
    for name, value in module['exported_crc_symbols'].items():
        if value['section'] == 65521:
            vendor_exports[name.removeprefix('__crc_')] = value['value']
results = []
for module in modules:
    missing, mismatch, matched = [], [], 0
    for name, expected in module['imported_symbol_crcs'].items():
        actual = symbols.get(name, vendor_exports.get(name))
        if actual is None:
            missing.append(name)
        elif actual != int(expected, 16):
            mismatch.append(dict(symbol=name, expected=expected, actual=f'{actual:08x}'))
        else:
            matched += 1
    results.append(dict(module=module['info'].get('name', module['file']),
                        matched=matched, missing=missing, mismatch=mismatch))
report = dict(symvers=str(a.symvers), results=results,
              passed=all(not r['missing'] and not r['mismatch'] for r in results),
              limitation='CRC agreement alone does not prove CFI, layout, or runtime compatibility.')
a.output.write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report, indent=2))
raise SystemExit(0 if report['passed'] else 1)
