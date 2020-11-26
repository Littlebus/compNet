import sqlite3
import pandas as pd
import datetime as dt
import json
from pprint import pprint

ROWS = 396
IDSTART = 1
RECORDSTART = 1

info = pd.read_csv('member.csv', encoding='gbk', index_col=0, float_precision='round_trip')
table = info.head(ROWS)

unit_data = []
for i in range(ROWS):
    unit_data.append((
        IDSTART + i,          # id
        table['name'][i],     # name
        i + 1,                # member_id
        None,                 # age
        None,                 # height
        None,                 # weight
        dt.datetime.utcnow(), # timestamp
        1,                    # user_id
    ))

tag = ['name', 'Raise']
for word in tag:
    table = table.drop(word, axis=1)

record_data = []
for i in range(ROWS):
    metrics = {}
    for col in table.columns.values.tolist():
        metrics[col] = float(table[col][i])

    record_data.append((
        RECORDSTART + i,                         # id
        IDSTART + i,                             # unit_id
        1,                                       # user_id
        dt.datetime.utcnow(),                    # timestamp
        json.dumps(metrics, ensure_ascii=False), # metrics
        None,                                    # label
        None,                                    # up
    ))

conn = sqlite3.connect('data.db')
c = conn.cursor()
c.executemany('INSERT INTO unit VALUES (?,?,?,?,?,?,?,?)', unit_data)
c.executemany('INSERT INTO record VALUES (?,?,?,?,?,?,?)', record_data)
for row in c.execute('SELECT * FROM record'):
    pprint(row)
conn.commit()
