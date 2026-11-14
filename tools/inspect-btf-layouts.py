"""Extract named structure sizes and flattened anonymous-member bit offsets."""
import json
from pathlib import Path
import struct
import sys

data = Path(sys.argv[1]).read_bytes()
magic, version, flags, header, toff, tlen, soff, slen = struct.unpack_from('<HBBIIIII', data)
assert magic == 0xeb9f and version == 1
assert header + toff + tlen <= len(data) and header + soff + slen <= len(data)
strings = data[header + soff:header + soff + slen]
def name(offset):
    assert offset < len(strings)
    end = strings.index(b'\0', offset)
    return strings[offset:end].decode()

types = [None]
pos, end = header + toff, header + toff + tlen
while pos < end:
    noff, info, size = struct.unpack_from('<III', data, pos)
    kind, count, kflag = (info >> 24) & 31, info & 65535, info >> 31
    pos += 12
    members = []
    if kind in (4, 5):
        for i in range(count):
            n, typ, offset = struct.unpack_from('<III', data, pos + i * 12)
            members.append(dict(name=name(n), type=typ,
                                offset=offset & 0xffffff if kflag else offset,
                                bits=offset >> 24 if kflag else 0))
    if kind in (4, 5, 15, 19): extra = 12 * count
    elif kind in (6, 13): extra = 8 * count
    elif kind == 3: extra = 12
    elif kind in (1, 14, 17): extra = 4
    else:
        assert kind in (2, 7, 8, 9, 10, 11, 12, 16, 18), kind
        extra = 0
    pos += extra
    assert pos <= end
    types.append(dict(name=name(noff), kind=kind, size=size, members=members))
assert pos == end

def flatten(typ, base=0, depth=0):
    assert depth < 32
    result = {}
    for member in types[typ]['members']:
        offset = base + member['offset']
        if member['name']:
            assert member['name'] not in result
            result[member['name']] = dict(offset_bits=offset, bitfield_size=member['bits'])
        else:
            for key, value in flatten(member['type'], offset, depth + 1).items():
                assert key not in result
                result[key] = value
    return result

wanted = {'task_struct', 'mm_struct', 'module', 'net_device', 'sk_buff',
          'sock', 'file', 'page', 'super_block', 'usb_device'}
result = {}
for i, typ in enumerate(types[1:], 1):
    if typ['kind'] == 4 and typ['name'] in wanted:
        record = dict(size=typ['size'], members=flatten(i))
        assert typ['name'] not in result or result[typ['name']] == record
        result[typ['name']] = record
assert result.keys() == wanted, wanted - result.keys()
Path(sys.argv[2]).write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({key: value['size'] for key, value in result.items()}, sort_keys=True))
