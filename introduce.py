import sqlite3
import pandas as pd
import datetime as dt
import json

ROWS = 50
IDSTART = 1
RECORDSTART = 1

path = r'./labeled.csv'
info = pd.read_csv(path, encoding='gbk', index_col=0)
table = info.head(ROWS)

unit_data = []
for i in range(ROWS):
    unit_data.append((
        IDSTART + i,
        table['NAME'][i],
        int(table['编号'][i]),
        int(table['AGE'][i]),
        float(table['HEIGHT'][i]),
        float(table['WEIGHT'][i]),
        dt.datetime.utcnow(),
        1
    ))

tag = ['NAME', '编号', 'AGE', 'HEIGHT', 'WEIGHT']
for word in tag:
    table = table.drop(word, axis=1)

record_data = []
for i in range(ROWS):
    metrics = {}
    label = ''
    for col in table.columns.values.tolist():
        if col == 'AGE':
            metrics[col] = int(table[col][i])
        elif col == 'LABEL':
            label = int(table[col][i])
        else:
            metrics[col] = float(table[col][i])
    record_data.append((
        RECORDSTART + i,
        IDSTART + i,
        1,
        dt.datetime.utcnow(),
        json.dumps(metrics),
        label
    ))

conn = sqlite3.connect('data.db')
c = conn.cursor()

c.executemany('INSERT INTO unit VALUES (?,?,?,?,?,?,?,?)', unit_data)

c.executemany('INSERT INTO record VALUES (?,?,?,?,?,?)', record_data)

for row in c.execute('SELECT * FROM record'):
    print(row)

conn.commit()