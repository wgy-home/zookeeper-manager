from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, ValidationError
from wtforms.validators import DataRequired, Length, Email, AnyOf, DataRequired
from flask import current_app, flash
from .models import zookeeper
import hashlib

# 同步zk组至其它环境的表单
class SyncZkForm(FlaskForm):
    env = SelectField(
        label = '环境选择:  ',
        render_kw={ 'class': 'form-control' },
        validators=[DataRequired('环境必须选择')]
    )
    password = PasswordField(
        u'password 不写密码则为只读模式: ', 
        render_kw={ 'class': 'form-control' }
    )
    submit = SubmitField('Submit')

    @property
    def password_check(self):
        zkpass = self.zk.search()
        mypass = self.password.data
        if zkpass != hashlib.sha1(mypass.encode("utf-8")).hexdigest():
            return False
        return True


# 节点选择form表单
class ZkForm(FlaskForm):
    env = SelectField(
        label = '环境选择:  ',
        render_kw={ 'class': 'form-control' },
        validators=[DataRequired('环境必须选择')]
    )
    node = StringField(
        u'node: ',
        render_kw={ 'class': 'form-control' },
        validators=[DataRequired('Node不能为空'), 
        Length(1, 128)]
    )
    password = PasswordField(
        u'password 不写密码则为只读模式: ', 
        render_kw={ 'class': 'form-control' }
    )
    version =  StringField(
        u'version: ',
        render_kw={'class': 'form-control'},
        validators=[DataRequired('versioon不能为空'),
        Length(1, 30)]
    )
    submit = SubmitField('Submit')

    def validate_node(self, field):
        print('validate_node')
        self.zk = zookeeper(self.env.data)
        if not self.zk.check_node(self.node.data):
            flash('{} node不存在。'.format(self.node.data), 'danger')
            raise  ValidationError('{}node节点不存在'.format(self.node.data))
    
    def validate_version(self, field):
        if not self.zk.check_node(self.node.data + '/' + self.version.data):
            flash('{} version不存在。'.format(self.version.data), 'danger')
            print('validate_version')
            raise  ValidationError('{}version节点不存在'.format(self.version.data))
    
    def validate_password(self, field):
        zkpass = self.zk.search(self.node.data)
        mypass = self.password.data
        if zkpass != hashlib.sha1(mypass.encode("utf-8")).hexdigest():
            flash('密码错误, 只读模式', 'warning')
    
    @property
    def password_check(self):
        zkpass = self.zk.search(self.node.data)
        mypass = self.password.data
        if zkpass != hashlib.sha1(mypass.encode("utf-8")).hexdigest():
            return False
        return True

    @property
    def get_data(self):
        groups = self.zk.children(self.node.data + '/' + self.version.data)
        auth_key = ['key','password','pass']
        print()
        group_data = {}
        for group in groups:
            property_data = {}
            path =  self.node.data + '/' + self.version.data + '/' + group
            childrens = self.zk.children(path)
            for children in childrens:
                # 对password,auth,key等敏感字段做处理
                if self.password_check:
                    print(str(self.password_check))
                    print('密码验证正常')
                    property_data[children] = self.zk.search(path + '/' + children)
                else:
                    print('密码验证不正常')
                    if 'key' in children.lower():
                        property_data[children] = '*********'
                    elif 'password' in children.lower():
                        property_data[children] = '*********'
                    elif 'pass' in children.lower():
                        property_data[children] = '*********'
                    elif 'auth' in children.lower():
                        property_data[children] = '*********'
                    else:
                        property_data[children] = self.zk.search(path + '/' + children)
            group_data[group] = property_data
        return group_data

    @property
    def zk_close(self):
        self.zk.close()
        return True