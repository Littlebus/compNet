#!/bin/bash

getopts g GUNICORN
DIR=$(cd $(dirname "${BASH_SOURCE[0]}") && pwd)
DB=$DIR"/data.db"
LOGS=$DIR"/logs/"
MIGRATIONS=$DIR"/migrations/"

# 创建.db文件
if [ ! -f $DB ]; then
  touch $DB
fi

# 创建logs文件夹
if [ ! -d $LOGS ]; then
  mkdir $LOGS
fi

# 初始化数据库
if [ ! -d $MIGRATIONS ]; then
  flask db init
fi

# 更新数据库表
flask db stamp head
flask db migrate -m "xxx"
flask db upgrade heads

# 启动模式
if [ $GUNICORN = "g" ]; then
  gunicorn -w 4 -b 127.0.0.1:8000 app:app
else
  python dev_start.py
fi
