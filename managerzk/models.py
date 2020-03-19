from kazoo.client import KazooClient, KazooState
from flask import current_app, flash
import time, os, kazoo, hashlib, logging

class zookeeper(object):
    def __init__(self, zkenv):
        self.zkenv = zkenv + '_host'
        zk_dict = current_app.config["ZK_DICT"]
        logging.info('Began to link {} zookeeper'.format(zkenv))
        self.zkhost = zk_dict[self.zkenv]
        self.zk = KazooClient(hosts=self.zkhost)
        self.zk.start()
        self.zk.add_listener(self.check_connect)
        self.exportPath = current_app.config["EXPORT_PATH"]

    def check_connect(self, state):
        if state == KazooState.LOST:
            print('链接丢失')
        elif state == KazooState.SUSPENDED:
            print('链接断开')
        else:
            print('建立链接')

    def search(self, zkpath):
        if self.zk.exists(zkpath):
            data, stat = self.zk.get(zkpath)
            print('data: {}, stat: {}'.format(data, stat))
            return data.decode('utf-8')
        else:
            print('{}路径不存在，请检查。'.format(zkpath))

    def children(self, zkpath):
        children = self.zk.get_children(zkpath)
        logging.info('get {} children'.format(zkpath))
        logging.debug('{} children: {}'.format(zkpath, children))
        return children

    def check_node(self, path):
        if self.zk.exists(path):
            logging.info('{} exists'.format(path))
            return True
        else:
            logging.info('{} is not exists'.format(path))
            return False

    def create_property(self, path, value):
        if self.zk.exists(path):
            return '{}已经存在'.format(path)
        else:
            value=value.encode('utf-8')
            self.zk.create(path, value=value, makepath=True)
            logging.info('create property, path: {}, value: {}'.format(path, value))
            return True

    def create_group(self, path):
        if self.zk.exists(path):
            return '{}已经存在'.format(path)
        else:
            self.zk.create(path, makepath=True)
            logging.info('create group, path: {}'.format(path))
            return True

    def update(self, path, value):
        self.zk.set(path, value.encode('utf-8'))
        logging.info('update zookeeper, path: {}, value: {}'.format(path, value))

    def set_property(self, path, newkey, newvalue, oldkey, oldvalue):
        logging.info('update property')
        if newkey == oldkey:
            print(type(newkey))
            logging.info('There were no changes in the key. old key: {}, new key: {}'.format(oldkey, newkey))
            #print('key无变化')
            if newvalue == oldvalue:
                logging.info('There were no changes in the value. old value: {}, new value: {}'.format(oldvalue, newvalue))
                #print('value 无变化')
            else:
                #print('value更新:{}'.format(newvalue))
                alertpath = path + '/' + oldkey
                #print('路径：{}'.format(alertpath))
                self.zk.set(alertpath, newvalue.encode('utf-8'))
                logging.info('Will be {} to {}'.format(alertpath, newvalue))
                return '修改完成'
        else:
            print('key更新')
            oldpath = path + '/' + oldkey
            newpath = path + '/' + newkey
            print('oldpath: {}'.format(oldpath))
            logging.info('Will be {} to {}'.format(oldpath, newpath))
            self.zk.create(newpath, newvalue.encode('utf-8'))
            self.delete_property(oldpath)
            logging.info('Delete old path: {}'.fotmat(oldpath))
            return '更新完成'

    def delete_property(self, path):
        self.zk.delete(path, recursive=True)

    def export_group(self, node, version, group):
        now = str(int(time.time()))
        path = node + '/' + version + '/' + group 
        exportPath = self.exportPath + '/' + now + '/'
        filename = group + '.propertry.txt'
        os.makedirs(exportPath)
        exportFile = exportPath +  filename
        property_data = {}
        childrens = self.zk.get_children(path)

        with open(exportFile, 'w+') as file:
            file.write('# export Zookeeper property '+'\r\n')
            file.write('# node:: '+node+'\r\n# version:: '+version+'\r\n# group:: '+group+'\r\n')

            for children in childrens:
                property_data[children] = self.search(path + '/' + children)

            property_dict = 'property='+str(property_data) 
            file.write(property_dict+'\r\n')
        return  exportFile, filename

    def copy_group(self, node, version, group, newgroup):
        path = node + '/' + version + '/' + group 
        newpath = node + '/' + version + '/' + newgroup 

        self.create_group(newpath)
        childrens = self.zk.get_children(path)
        for children  in childrens:
            ckey = newpath + '/' + children
            cvalue = self.search(path + '/' + children)
            self.zk.create(ckey, cvalue.encode('utf-8'))

    def close(self):
        self.zk.stop()

    def env_data(self, node, password, version):
        groups = self.children(node + '/' + version)
        auth_key = ['key','password','pass']
        print()
        group_data = {}
        for group in groups:
            property_data = {}
            path =  node + '/' + version + '/' + group
            childrens = self.children(path)
            if self.password_check(node, password):
                check = True
                logging('Password authentication, enter the administrator mode')
            else:
                print('Password authentication failed, into read-only mode')
                check = False
            for children in childrens:
                # 对password,auth,key等敏感字段做处理
                if check:
                    print(str(self.password_check))
                    property_data[children] = self.search(path + '/' + children)
                else:
                    logging.info('Read only mode, processing keywords')
                    if 'key' in children.lower():
                        property_data[children] = '*********'
                    elif 'password' in children.lower():
                        property_data[children] = '*********'
                    elif 'pass' in children.lower():
                        property_data[children] = '*********'
                    elif 'auth' in children.lower():
                        property_data[children] = '*********'
                    else:
                        property_data[children] = self.search(path + '/' + children)
            group_data[group] = property_data
        return group_data

    def password_check(self, node, password):
        zkpass = self.search(node)
        mypass = password
        if zkpass != hashlib.sha1(mypass.encode("utf-8")).hexdigest():
            logging.info('Password check fail.')
            return False
        logging.info('Password check success.')
        return True
