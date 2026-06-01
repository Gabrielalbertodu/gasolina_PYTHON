import requests
urls = [
    'https://query1.finance.yahoo.com/v7/finance/quote?symbols=BZ=F,CL=F',
    'https://query1.finance.yahoo.com/v8/finance/chart/BZ=F?range=5d&interval=1d',
    'https://query1.finance.yahoo.com/v8/finance/chart/CL=F?range=5d&interval=1d',
]
for url in urls:
    try:
        r = requests.get(url, timeout=15, headers={'User-Agent': 'Mozilla/5.0'})
        print('URL', url, 'status', r.status_code)
        print(r.text[:600].replace('\n',' '))
    except Exception as e:
        print('URL', url, 'error', e)
