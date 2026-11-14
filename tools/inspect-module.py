"""Read ELF64 module ABI metadata without loading the module."""
import pathlib, struct, json, sys
p=pathlib.Path(sys.argv[1]);b=p.read_bytes()
assert b[:6]==b'\x7fELF\x02\x01', 'Expected little-endian ELF64'
off=struct.unpack_from('<Q',b,40)[0];stride,count,strings=struct.unpack_from('<HHH',b,58)
headers=[struct.unpack_from('<IIQQQQIIQQ',b,off+i*stride) for i in range(count)]
def content(h):
    assert h[4]+h[5]<=len(b)
    return b[h[4]:h[4]+h[5]]
def cstr(s,n):return s[n:s.find(b'\0',n)].decode(errors='replace')
shnames=content(headers[strings]);sections={cstr(shnames,h[0]):h for h in headers}
versions={}
if '__versions' in sections:
    data=content(sections['__versions']);assert len(data)%64==0
    for i in range(0,len(data),64):versions[cstr(data,i+8)]=f'{struct.unpack_from("<Q",data,i)[0]:08x}'
info={};info_values={}
if '.modinfo' in sections:
    for item in content(sections['.modinfo']).split(b'\0'):
        if b'=' in item:
            k,v=item.split(b'=',1);key=k.decode();value=v.decode(errors='replace');info[key]=value
            info_values.setdefault(key,[]).append(value)
crcs={}
for name,h in sections.items():
    if h[1]!=2:continue
    names=content(headers[h[6]]);tab=content(h)
    for i in range(0,len(tab),h[9]):
        n,typ,other,index,value,size=struct.unpack_from('<IBBHQQ',tab,i);n=cstr(names,n)
        if n.startswith('__crc_'):crcs[n]=dict(value=value,section=index)
result={'file':str(p),'bytes':len(b),'info':info,'info_values':info_values,'imported_symbol_crcs':versions,'exported_crc_symbols':crcs}
target=pathlib.Path(sys.argv[2]) if len(sys.argv)>2 else p.with_suffix('.abi.json');target.write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps({'file':str(p),'name':info.get('name'),'vermagic':info.get('vermagic'),'imports':len(versions),'export_crc_symbols':len(crcs),'sections':list(sections)[-12:],'saved':str(target)},indent=2))
