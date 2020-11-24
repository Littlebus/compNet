import sqlite3
import pandas as pd
import datetime as dt
import json

ROWS = 5
IDSTART = 1
RECORDSTART = 1

info = pd.read_csv('read_in.csv', encoding='gbk', index_col=0)
table = info.head(ROWS)

unit_data = []
for i in range(ROWS):
    unit_data.append((
        IDSTART + i,
        table['name'][i],
        i,
        18,
        175,
        70,
        dt.datetime.utcnow(),
        1
    ))

tag = ['name', 'Raise']
for word in tag:
    table = table.drop(word, axis=1)

record_data = []
for i in range(ROWS):
    metrics = {}
    label = ''
    for col in table.columns.values.tolist():
        metrics[col] = float(table[col][i])

    record_data.append((
        RECORDSTART + i,
        IDSTART + i,
        1,
        dt.datetime.utcnow(),
        json.dumps(metrics, ensure_ascii=False),
        '',
        ''
    ))

conn = sqlite3.connect('data.db')
c = conn.cursor()

c.executemany('INSERT INTO unit VALUES (?,?,?,?,?,?,?,?)', unit_data)

c.executemany('INSERT INTO record VALUES (?,?,?,?,?,?,?)', record_data)

for row in c.execute('SELECT * FROM record'):
    print(row)

conn.commit()