import pandas as pd

df = pd.read_csv('member.csv', index_col=0)
df.to_csv('read_in.csv', encoding='gbk')