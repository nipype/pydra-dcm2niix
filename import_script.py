import re
import subprocess as sp
import pprint


out = sp.check_output('dcm2niix -h', shell=True).decode('ascii')
lines = re.match(r'.*Options :\n(.*)Defaults file.*', out,
                 flags=re.MULTILINE | re.DOTALL).group(1).split('\n')
fields = []
for line in lines:
    if not line.strip():
        continue
    flag, desc, spec = re.match(r'\s*([^\s]+) : ([^\(]+)(.*)', line).groups()
    if match:= re.match(r'.*default ([0-9a-zA-Z]+)', spec):
        default = match.group(1)
        try:
            default = int(default)
        except ValueError:
            pass
    else:
        default = None
    if match:= re.match(r'\(([a-z0-9](?:/[a-z0-9])+).*', spec):
        choices = match.group(1).split('/')
    else:
        choices = None
    if match:= re.match(r'.*\[([^\]]+)\].*', spec):
        legend = match.group(1)
    else:
        legend = None
    name = '_'.join(desc.split()[:3]).lower()
    field = {
        'name': name,
        'type': type(default) if default is not None else bool,
        'metadata': {
            'argstr': flag,
            'help_string': desc + (' ' + legend if legend else '')}}
    field['default'] = default
    if choices is not None:
        field['metadata']['choices'] = choices
    fields.append(field)

for f in fields:
    print(f"""
    {f['name']}: ty.Optional[{f['type'].__name__}] = attr.ib(
        default={f['default']},
        metadata={pprint.pformat(f['metadata'])}))    
    """)
