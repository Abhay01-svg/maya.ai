import sys, traceback
sys.path.append(r'..\..\maya_ai')
try:
    from modules.brain import brain
    print('brain type', type(brain))
    res = brain.process_query('good morning Maya check weather the problem has been created and solve the issue')
    print('result', res)
except Exception as e:
    print('exception', repr(e))
    traceback.print_exc()
