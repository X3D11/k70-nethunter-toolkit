"""Reject size or existing-member offset changes in captured platform structures."""
import argparse
import json
from pathlib import Path

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('stock', type=Path)
p.add_argument('candidate', type=Path)
p.add_argument('--output', type=Path, required=True)
p.add_argument('--sysvipc', action='store_true')
a = p.parse_args()
stock, candidate = (json.loads(path.read_text()) for path in (a.stock, a.candidate))
assert len(stock) == 10 and stock.keys() == candidate.keys()
issues, additions = [], {}
for name, original in stock.items():
    updated = candidate[name]
    if original['size'] != updated['size']:
        issues.append(dict(structure=name, issue='size', stock=original['size'], candidate=updated['size']))
    for member, layout in original['members'].items():
        if updated['members'].get(member) != layout:
            issues.append(dict(structure=name, member=member, issue='offset or bitfield changed',
                               stock=layout, candidate=updated['members'].get(member)))
    new = set(updated['members']) - original['members'].keys()
    if new:
        additions[name] = sorted(new)
        allowed = {'sysvsem', 'sysvshm'} if a.sysvipc and name == 'task_struct' else set()
        if new - allowed:
            issues.append(dict(structure=name, issue='unexpected members', members=sorted(new - allowed)))
report = dict(passed=not issues, structures=len(stock), issues=issues, additions=additions)
a.output.write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report, indent=2))
raise SystemExit(0 if report['passed'] else 1)
