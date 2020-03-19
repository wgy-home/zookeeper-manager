# zookeeper manager

在很多公司中都使用zookeeper做为分布式应用的配置中心，那么在公司中不同环境之间的zookeeper配置的同步，创建，更新等等都要通过命令行去操作，但很多情况下对于不熟悉或者没有权限的人员都不方便操作或查看，因此根据自己的需求开发一个管理界面，方便同事及自己使用。

# 安装

```shell
# git clone 
# pip3 install -r requirements.txt
```

# 配置

```text
[global]
# 自行修改
secret_key = '\x8d\xb4\x17Z\xf4\x98\xa7\xa2\xf9\xd1\xd9\xd3\xfa}\xdd\xa5\xc0\xdd\xebC\xcc\x07\xe2\xbb'
# 日志及数据临时目录
data_path = /Users/wgy/scripts/zookeeper-manager/data
log_path = /Users/wgy/scripts/zookeeper-manager/logs
# 日志级别
log_level = INFO

[zookeeper]
# zookeeper不同环境的地址，格式为： environmentName_host = ip:port，例子如下：
dev_host = 127.0.0.1:2182   # 此行意思为 dev环境的zookeeper地址为  127.0.0.1:2182
hotfix_host = 127.0.0.1:2181
```

# 启动
```shell
# export FLASK_APP=manage.py 
# flask run --host='0.0.0.0'  -p '5000'
```

