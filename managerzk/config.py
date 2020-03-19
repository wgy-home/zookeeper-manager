from configparser import ConfigParser
import os 

conf = ConfigParser()
config_file = os.getcwd() + '/managerzk/config.ini'
conf.read(config_file , encoding='UTF-8')


class BaseConfig(object):
    """ 配置基类 """
    SECRET_KEY = conf.get('global', 'secret_key')
    EXPORT_PATH = conf.get('global', 'data_path')
    LOG_PATH = conf.get('global', 'log_path')
    LOG_LEVEL = conf.get('global', 'log_level')

    if not os.path.exists(EXPORT_PATH):
        os.makedirs(EXPORT_PATH)
    
    if not os.path.exists(LOG_PATH):
        os.makedirs(LOG_PATH)
    DEBUG = False

class DevelopmentConfig(BaseConfig):
    """ 开发环境 """
    DEBUG = True

class ProductionConfig(BaseConfig):
    """ 生产环境 """
    env_list = [ env for env in conf.options('zookeeper') if 'host' in env ]
    ZK_ENV_LIST = []
    for num in range(len(env_list)):
        env = env_list[num].split('_')[0]
        ZK_ENV_LIST.append(env)
    ZK_DICT = dict(conf.items('zookeeper'))

configs = {
    'dev' : DevelopmentConfig,
    'release' : ProductionConfig
}
