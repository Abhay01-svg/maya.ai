import requests, time, sys
url='http://localhost:5001/health'
for i in range(12):
    try:
        r=requests.get(url, timeout=5)
        print('ok', r.status_code, r.text)
        sys.exit(0)
    except Exception as e:
        print('attempt', i+1, 'failed:', str(e))
        time.sleep(5)
print('timeout')
sys.exit(1)
