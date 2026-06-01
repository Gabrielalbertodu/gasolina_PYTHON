import sqlite3, json, os
candidates=['projeto_gasolina/data/gasolina.sqlite3','data/gasolina.sqlite3']
for p in candidates:
    if os.path.exists(p):
        try:
            conn=sqlite3.connect(p)
            conn.row_factory=sqlite3.Row
            r=conn.execute('SELECT * FROM previsoes ORDER BY data_hora DESC LIMIT 1').fetchone()
            print('DB:',p)
            if r:
                print(json.dumps(dict(r), default=str, ensure_ascii=False, indent=2))
            else:
                print('Nenhuma previsão encontrada')
        except Exception as e:
            print('Erro lendo',p,e)
    else:
        print('Não existe',p)
