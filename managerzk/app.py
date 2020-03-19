from flask import Flask, render_template
from .config import configs
from flask_bootstrap import Bootstrap
import logging
from logging.handlers import TimedRotatingFileHandler

def register_blueprints(app):
    from .handlers import front
    app.register_blueprint(front)

def set_log(config):
    log_path = configs.get(config).LOG_PATH
    # 设置日志的记录等级
    
    Debug = ['Debug', 'debug', 'DEBUG']
    Info = ['Info', 'info', 'INFO']
    if configs.get(config).LOG_LEVEL in Debug:
        level = 10
    elif configs.get(config).LOG_LEVEL in Info:
        level = 20
    else:
        level = 20
    
    logging.basicConfig(level=level)
    # 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
    file_log_handler = TimedRotatingFileHandler(filename=log_path + "/zookeeper-manager-info.log",  when='D', interval=1, backupCount=7, encoding="utf-8")
    # 创建日志记录的格式 日志等级 输入日志信息的文件名 行数 日志信息
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(filename)s:%(lineno)d %(message)s')
    # 为刚创建的日志记录器设置日志记录格式s
    file_log_handler.setFormatter(formatter)
    # 为全局的日志工具对象（flask app使用的）添加日志记录器
    logging.getLogger().addHandler(file_log_handler)


def create_app(config):
    "根据传入的config名称，加载不同环境的配置"
    set_log(config)
    app = Flask(__name__)
    bootstrap = Bootstrap(app)
    app.config.from_object(configs.get(config))
    register_blueprints(app)
    return app
    