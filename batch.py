import datetime, json, pandas, sqlite3
from pprint import pprint


ROWS = 100
START = 1

info = pandas.read_csv('member.csv', encoding='gbk', index_col=0, float_precision='round_trip')
table = info.head(ROWS)
columns = table.columns.values.tolist()
columns.remove('name')
columns.remove('Raise')
up = {'未升高': 0, '升高': 1}

data = []
for i in range(ROWS):
    metrics = {}
    for col in columns:
        metrics[col] = float(table[col][i])
    data.append((
        START + i,                               # id
        table['name'][i],                        # name
        datetime.datetime.utcnow(),              # timestamp
        json.dumps(metrics, ensure_ascii=False), # metrics
        None,                                    # label
        up.get(table['Raise'][i]),               # up
        1,                                       # user_id
    ))

conn = sqlite3.connect('data.db')
c = conn.cursor()
c.executemany('INSERT INTO record VALUES (?,?,?,?,?,?,?)', data)
for row in c.execute('SELECT * FROM record'):
    pprint(row)
conn.commit()
