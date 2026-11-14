"""Check a repacked v4 boot image contains exactly the reviewed raw ARM64 Image."""
from pathlib import Path
import hashlib
import json
import struct
import sys

stock, candidate, kernel, report = map(Path, sys.argv[1:])
old, new, raw = (p.read_bytes() for p in (stock, candidate, kernel))
assert old[:8] == new[:8] == b'ANDROID!'
assert struct.unpack_from('<I', old, 40)[0] == struct.unpack_from('<I', new, 40)[0] == 4
oldsize, newsize = struct.unpack_from('<I', old, 8)[0], struct.unpack_from('<I', new, 8)[0]
assert newsize == len(raw) and new[4096:4096 + newsize] == raw
assert raw[56:60] == b'ARM\x64'
mapped_size = struct.unpack_from('<Q', raw, 16)[0]
# ARM64 image_size includes zero-initialized BSS, which is absent from the file.
assert len(raw) <= mapped_size <= 512 * 1024 * 1024
assert old[12:1584] == new[12:1584], 'Unexpected boot header/ramdisk/signature changes'
assert struct.unpack_from('<I', new, 12)[0] == 0, 'Expected separate init_boot ramdisk'
assert len(new) <= 201326592, 'Exceeds backed-up actual boot partition size'
result = dict(passed=True, stock=str(stock), candidate=str(candidate), kernel=str(kernel),
              old_kernel_bytes=oldsize, new_kernel_bytes=newsize, image_bytes=len(new),
              kernel_mapped_bytes=mapped_size,
              kernel_sha256=hashlib.sha256(raw).hexdigest(),
              boot_sha256=hashlib.sha256(new).hexdigest(),
              limitation='Structural validation only; does not prove bootability or hardware compatibility.')
report.write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
