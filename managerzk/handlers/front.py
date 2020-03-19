from flask import Blueprint, render_template, current_app, abort, flash, jsonify, json, request, make_response, send_file
from ..models import zookeeper
from flask import request
from ..forms import  ZkForm
import kazoo, hashlib, logging, time
from werkzeug.utils import secure_filename

front = Blueprint('route', 'index', __name__)
@front.route('/', methods=['GET', 'POST'])
def index():
    env_list = []
    for env in current_app.config["ZK_ENV_LIST"]:
        env_list.append((env, env))
    counts = {}
    counts['env_list'] = env_list

    form = ZkForm()
    form.env.choices = env_list
    return  render_template('index.html', form=form, counts=counts)

@front.route('/envdata', methods=['POST'])
def env_data():
    env_list = []
    for env in current_app.config["ZK_ENV_LIST"]:
        env_list.append((env, env))
    counts = {}
    counts['env_list'] = env_list

    form = ZkForm()
    form.env.choices = env_list
    try:
        if form.validate_on_submit():
            env = form.env.data
            node = form.node.data
            version = form.version.data

            counts['env'] = env
            counts['node'] =  node
            counts['version'] =  version
            counts['group_data'] = form.get_data
            counts['password_check'] = form.password_check
            form.zk_close
            return  render_template('zookeeper/index.html', form=form, counts=counts)
        else:
            form.zk_close
            return  render_template('index.html', form=form, counts=counts)
    except kazoo.handlers.threading.KazooTimeoutError:
        flash('连接{}环境的zookeeper超时，请联系管理员。'.format(env), 'danger')
        return  render_template('error.html', form=form, counts=counts, error='')
    

@front.route('/create/node', methods=['POST'])
def create_node():
    env = request.form.get('env')
    node = request.form.get('node')
    version = request.form.get('version')
    password = hashlib.sha1(request.form.get('password').encode("utf-8")).hexdigest()
    try:
        zk = zookeeper(env)
        zk.create_property(node,password)
        if version !='':
            path = node + '/' + version
            zk.create_property(path,password)
    except:
        zk.close()
        logging.info('{} environment node:{} create fail.'.format(env, node))
        return  {},500
    zk.close()
    logging.info('{} environment node:{} create success.'.format(env, node))
    return {},200

@front.route('/create/version', methods=['POST'])
def create_version():
    env = request.form.get('env')
    node = request.form.get('node')
    version = request.form.get('version')
    path = node + '/' + version
    try:
        zk = zookeeper(env)
        zk.create_group(path)
    except:
        zk.close()
        logging.info('{} environment create version: {} fail.'.format(env, version))
        return  {},500
    zk.close()
    logging.info('{} environment create version: {} success.'.format(env, version))
    return {},200

@front.route('/data', methods=['GET', 'POST'])
def group_data():
    env = request.form.get('env')
    path = request.form.get('node') + '/' + request.form.get('version')  + '/' + request.form.get('group')

    zk = zookeeper(env)
    group_data = {}

    for key in zk.children(path):
        group_data[key] = zk.search(path + '/' + key )

    zk.close()
    return jsonify(group_data=(group_data))

@front.route('/edit/property', methods=['POST'])
def edit_property():
    env = request.form.get('env')
    path = request.form.get('node') + '/' + request.form.get('version')  + '/' + request.form.get('group')
    oldkey = request.form.get('oldkey')
    oldvalue = request.form.get('oldvalue')
    newkey = request.form.get('newkey')
    newvalue = request.form.get('newvalue')
    print('edit ：{} {} {} {} {} {}'.format(env, path, oldkey, oldvalue, newkey, newvalue))
    zk =  zookeeper(env)
    zk.set_property(path, newkey, newvalue, oldkey, oldvalue)
    zk.close()
    return 'success'

@front.route('/create/group', methods=['POST'])
def add_group():
    env = request.form.get('env')
    path = request.form.get('node') + '/' + request.form.get('version')  + '/' + request.form.get('group')
    zk = zookeeper(env)
    zk.create_group(path)
    zk.close()
    return 'success'

@front.route('/create/property', methods=['POST'])
def add_property():
    env = request.form.get('env')
    path = request.form.get('node') + '/' + request.form.get('version')  + '/' + request.form.get('group') + '/' + request.form.get('key')
    value = request.form.get('value')
    zk = zookeeper(env)
    zk.create_property(path, value)
    zk.close()
    return 'success'

@front.route('/delete/property', methods=['POST'])
def delete_property():
    env = request.form.get('env')
    path = request.form.get('node') + '/' + request.form.get('version')  + '/' + request.form.get('group') + '/' + request.form.get('key')
    zk = zookeeper(env)
    zk.delete_property(path)
    zk.close()
    return 'success'

@front.route('/delete/group', methods=['POST'])
def delete_group():
    env = request.form.get('env')
    path = request.form.get('node') + '/' + request.form.get('version')  + '/' + request.form.get('group')
    zk = zookeeper(env)
    zk.delete_property(path)
    zk.close()
    return 'success'

@front.route('/export/group', methods=['POST'])
def export_group():
    env = request.form.get('env')
    node = request.form.get('node')
    version = request.form.get('version')
    group = request.form.get('group')

    zk = zookeeper(env)
    file, filename = zk.export_group(node, version, group)
    print(filename)
    zk.close()
    downloadfile = send_file(file, as_attachment=True)
    #downloadfile.headers['Content-Disposition'] += "; filename="+filename+""
    return downloadfile

@front.route('/copy/group', methods=['GET'])
def copy_group():
    env = request.args.get('env')
    node = request.args.get('node')
    version = request.args.get('version')
    group = request.args.get('group')
    newgroup = request.args.get('newgroup')

    zk = zookeeper(env)
    zk.copy_group(node, version, group, newgroup)
    zk.close()
    return 'success'

@front.route('/import/group', methods=['POST'])
def import_group():
    env = request.form.get('env')
    node = request.form.get('node')
    version = request.form.get('version')
    group = request.form.get('group')
    try:
        zk = zookeeper(env)
        file = request.files['iGroupName']
        filename = secure_filename(file.filename) + '.' + str(int(time.time()))
        fileContent = request.files.get('iGroupName').read().decode("utf-8")
        proertyDict=eval(fileContent.split('property=')[1])
        #file.save(filename)
    except:
        zk.close()
        logging.info('请检查导入文件格式是否正常')
        return '请检查导入文件的格式',500
    for k, v in proertyDict.items():
        path = node + '/' + version + '/' + group + '/' + k
        print(path)
        zk.create_property(path, v)
    zk.close()
    return {},200

@front.route('/sync/group', methods=['GET'])
def sync_group():
    env = request.args.get('env')
    node = request.args.get('node')
    version = request.args.get('version')
    group = request.args.get('group')
    syncEnv = request.args.get('syncEnv')
    jspassword = request.args.get('password')
    password  = hashlib.sha1(jspassword.encode("utf-8")).hexdigest()
    path = node + '/' + version + '/' + group 
    property_data = {}
     
    zk = zookeeper(env)
    syncZk = zookeeper(syncEnv)
    print('env:{}, node:{}, version:{}, group:{}, syncEnv:{}'.format(env, node, version, group, syncEnv))

    # 检查需要同步zk环境中是否有对应的节点
    if syncZk.check_node(path):
        print('节点存在，检查节点密码是否正确。')
        zkpass = syncZk.search(node)
        if zkpass  != password:
            flash('节点存在，但密码验证失败，未进行同步。', 'danger')
            zk.close()
            return 'danger'
    else:
        print('节点不存在，正在创建节点')
        syncZk.create_property(node, password)
        

    print('开始获取原group内的数据')
    # 获取原zk组中的数据
    group_data = {}
    childrens = zk.children(path)
    for children in childrens:
        property_data[children] = zk.search(path + '/' + children)
    print('同步数据至新的环境')
    print(property_data)
    for key, value in property_data.items():
        propertyKey = path + '/' + key
        syncZk.create_property(propertyKey, value)

    zk.close()
    syncZk.close()
    flash('节点同步完成', 'info')
    return 'info'



@front.errorhandler(404)
def not_fount(error):
    env_list = []
    for env in current_app.config["ZK_ENV_LIST"]:
        env_list.append((env, env))

    form = ZkForm()
    form.env.choices = env_list
    return render_template('404.html',  counts='')