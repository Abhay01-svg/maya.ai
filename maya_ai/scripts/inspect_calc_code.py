import re
s=open('maya_ai/test_coding_agent.py','r',encoding='utf-8').read()
m=re.search(r"calculator_code = '''(.*)'''", s, re.S)
if not m:
    print('not found')
else:
    code=m.group(1)
    print('FOUND, length=', len(code))
    print('--- tail start ---')
    print(code[-400:])
    print('--- tail end ---')
    # Validate extracted code using Maya validation engine
    import sys, os
    sys.path.insert(0, os.path.join(os.getcwd(), 'maya_ai'))
    from modules.validation_engine import validation_engine
    res = validation_engine.validate_code(code, 'python', 'calculator_from_string.py')
    print('\nValidation summary for extracted string:')
    print(res['summary'])
    print('Errors:', [e.to_dict() for e in res['errors']])
    print('Warnings:', [w.to_dict() for w in res['warnings']])
