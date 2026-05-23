import os, re, sys
s=open('maya_ai/test_coding_agent.py','r',encoding='utf-8').read()
m=re.search(r"calculator_code = '''(.*)'''", s, re.S)
if not m:
    print('calculator_code not found')
    sys.exit(1)
code=m.group(1)
# Write calculator.py as test does
with open('calculator.py','w',encoding='utf-8') as f:
    f.write(code)
print('Wrote calculator.py (len=', len(code),')')
# Validate the written file using Maya validation engine
sys.path.insert(0, os.path.join(os.getcwd(),'maya_ai'))
from modules.validation_engine import validation_engine
res = validation_engine.validate_code(code, 'python', 'calculator.py')
print('Validation summary:', res['summary'])
print('Errors:', [e.to_dict() for e in res['errors']])
print('Warnings:', [w.to_dict() for w in res['warnings']])
