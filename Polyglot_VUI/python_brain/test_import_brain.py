import sys, traceback
sys.path.append(r'..\..\maya_ai')
try:
    from modules.brain import brain
    print('brain ok', type(brain))
except Exception as e:
    print('import failed', repr(e))
    traceback.print_exc()
