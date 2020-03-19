
function toggle(id){
var tb=document.getElementById(id);
if(tb.style.display=='none') tb.style.display='block';
else tb.style.display='none';
}

var AlertEnv="";
var AlertNode="";
var AlertVersion="";
var AlertGroup="";
var AlertKey="";
var AlertValue="";
var OldKey="";
var OldValue="";
var IndexNum="";
var CetGroupValue="";

function PostGroup(env, node, version, group ) {
    $.ajax({
        url: "/data",
        type: "POST",
        data: {
            'env': env,
            'node': node,
            'version': version,
            'group': group
        },
        success: function (msg) {
            //console.log(msg.group_data)

            var _h='';

            for ( var item in msg.group_data){
                //console.log(item);
                //console.log(msg.group_data[item]);
                
                _h+='<tr>';
                _h+='<td style="table-layout: fixed;word-break:break-all; word-wrap:break-all; margin-bottom: 50px;" id="key">'+item+'</td>';
                _h+='<td style="table-layout: fixed;word-break:break-all; word-wrap:break-all; margin-bottom: 50px;" id="value">'+msg.group_data[item]+'</td>';
                _h+='<td margin-bottom: 50px;"><div class="btn-group" role="group"><a href="#" type="button" class="btn btn-default" title="删除"><span class="glyphicon glyphicon-trash" title="删除" aria-hidden="true"></span></a></div></td>';
                _h+='<td margin-bottom: 50px;"><div class="btn-group" role="group"><a href="#" type="button" class="btn btn-default" title="编辑"><span class="glyphicon glyphicon-pencil" title="编辑" aria-hidden="true"> </span></a></div></td>';
                _h+='</tr>';
            }

            $("#kv").html(_h);
        }
    })
}

function CreateProperty(env, node, version, group) {
    var key = $("#"+group+"_ckey").val();//获取表单的输入值;
    var value = $("#"+group+"_cvalue").val();//获取表单的输入值;
    var TableName=document.getElementById(group + 'Table')

    $.ajax({
        url: "/create/property",
        type: "POST",
        data: {
            'env' :  env,
            'node' : node,
            'version' : version,
            'group' : group,
            'key' : key,
            'value' : value
        },

        success: function (msg) {
            alert('添加成功')
            //location.reload();
            console.log(key, value, CetGroupValue)
            var tableRow=TableName.insertRow(1)

            var cell_0=tableRow.insertCell(0);
            //cell_0.innerHTML='<div class="btn-group" role="group"><a onclick=AlertTable('+'"'+env+'"'+','+'"'+node+'"'+','+'"'+version+'"'+','+'"'+CetGroupValue+'"'+',this,this.parentNode.parentNode.parentNode.rowIndex) type="button" class="btn btn-default btn-sm" title="编辑" data-key='+key+' data-value='+value+'> <span class="glyphicon glyphicon-pencil" title="编辑" aria-hidden="true"> </span></a> <a class="btn btn-default btn-sm" title="删除" onclick="DeleteProperty('+'"'+env+'"'+','+'"'+node+'"'+','+'"'+version+'"'+','+'"'+CetGroupValue+'"'+', this.parentNode.parentNode.parentNode.rowIndex)"> <span class="glyphicon glyphicon-trash" title="删除" aria-hidden="true"></span></a></div>'
            cell_0.innerHTML='<div class="btn-group" role="group"><a type="button" class="btn btn-default btn-sm" title="编辑" data-key='+key+' data-value='+value+'> <span class="glyphicon glyphicon-pencil" title="编辑" aria-hidden="true"> </span></a> <a class="btn btn-default btn-sm" title="删除" > <span class="glyphicon glyphicon-trash" title="删除" aria-hidden="true"></span></a></div>'
            //cell_0.innerHTML='<a onclick=DeleteProperty('+'"'+env+'"'+','+'"'+node+'"'+','+'"'+version+'"'+','+'"'+CetGroupValue+'"'+',"'+key+'"'+',this.parentNode.parentNode.parentNode.rowIndex) type="button" class="btn btn-default btn-sm" title="删除" > <span class="glyphicon glyphicon-trash" title="删除" aria-hidden="true"></span></a>'
            cell_0.className="dataOperating";

            var cell_1=tableRow.insertCell(1);
            cell_1.innerHTML=key
            cell_1.className="dataKey"

            var cell_2=tableRow.insertCell(2);
            cell_2.innerHTML=value
            cell_2.className="dataValue"

        }
    })
}


CopyEnv=''
CopyNode=''
CopyVersion=''
CopyGroup=''

function copyGroupLead(env, node, version, group){
    CopyEnv=env;
    CopyNode=node;
    CopyVersion=version;
    CopyGroup=group;
    $('#copyGroup').modal('show')
}

function syncGroup(obj){
    var newGroup = $("#inputCopyGroup").val();
    $.ajax({
        url: "/copy/group",
        type: "GET",
        data: {
            'env': CopyEnv,
            'node': CopyNode,
            'version': CopyVersion,
            'group': CopyGroup,
            'newgroup': newGroup
        },
        success: function(msg){
            console.log('success');
            location.reload();
        }
    })
}


function DeleteProperty(env, node, version, group, key, rowIndex){
    var rowHtml=document.getElementById(group + 'Table');
    var r=confirm('请确认是否要删除？');
    if (r==true){
        $.ajax({
            url: '/delete/property',
            type: 'POST',
            data:{
                'env' :  env,
                'node' : node,
                'version' : version,
                'group' : group,
                'key' : key,
            },
            success: function(msg) {
                alert('删除成功')
                rowHtml.deleteRow(rowIndex)
            }
        })
    }else {
        return;
    }

}

function AlertTable(env, node, version, group, obj, rowIndex){ 

    var key=$(obj).closest("tr").find(".dataKey").data("key");
    var value=$(obj).closest("tr").find(".dataValue").data("value");
    console.log(key)
    IndexNum=rowIndex

    AlertEnv=env;
    AlertNode=node;
    AlertVersion=version;
    AlertGroup=group;
    OldKey=key;
    OldValue=value

    var _ah='';

    _ah+='<p>'
    _ah+='key: <input type="text" class="form-control alertKey" value='+OldKey+'>'
    _ah+='</p>'
    _ah+='<p>'
    _ah+='value: <input type="text" class="form-control alertValue" value='+OldValue+'>'
    _ah+='</p>'
    _ah+='<p>'
    _ah+='<input type="button" value="修改" class="btn btn-default " onclick="AlertProperty(this)" data-dismiss="modal">'
    _ah+='</p>'
    $("#alertKV").html(_ah);
    $('#alertProperty').modal('show')

}

function AlertProperty(obj){
    AlertKey = $(obj).closest("div").find(".alertKey").get(0).value;
    AlertValue = $(obj).closest("div").find(".alertValue").get(0).value;
    var  rowHtml=document.getElementById(AlertGroup + 'Table').rows[IndexNum]
    
    $.ajax({
        url: "/edit/property",
        type: "POST",
        data: {
            'env' :  AlertEnv,
            'node' : AlertNode,
            'version' : AlertVersion,
            'group' : AlertGroup,
            'newkey' : AlertKey,
            'newvalue' : AlertValue,
            'oldkey' : OldKey,
            'oldvalue' : OldValue
        },

        success: function (msg) {
            alert('修改成功')
            rowHtml.cells[1].innerHTML = '<td style="table-layout: fixed;word-break:break-all; word-wrap:break-all; margin-bottom: 60px;" class="dataKey" data-key="'+AlertKey+'">'+AlertKey+'</td>'
            rowHtml.cells[2].innerHTML = '<td style="table-layout: fixed;word-break:break-all; word-wrap:break-all; margin-bottom: 60px;" class="dataValue" data-value="'+AlertValue+'">'+AlertValue+'</td>'
        }
    })

}



function addZkGroup(env, node, version){
    var NewGroup = $("#GroupInput").val()
    var _addGroup = ''
    $.ajax({
        url: "/create/group",
        type: "POST",
        data: {
            'env': env,
            'node': node,
            'version': version,
            'group': NewGroup
        },

        success: function(msg){
            location.reload();
        }
    })
}


function deleteGroup(env,node,version,group){
    var delGroup = group + 'Div'
    var r=confirm('请注意，确认后组内对应的值都将删除，并且无法恢复，请谨慎操作！！确认将"'+group+'"组删除么？');
    if (r==true){
    $.ajax({
        url: "/delete/group",
        type: "POST",
        data: {
            'env': env,
            'node': node,
            'version': version,
            'group': group
        },

        success: function(msg){
            var delDiv = document.getElementById(delGroup)
            delDiv.parentNode.removeChild(delDiv)
            console.log(delDiv)
        }
    })}
}

function exportGroup(env, node, version, group){
    $.ajax({
        url: "/export/group",
        type: "POST",
        data: {
            'env': env,
            'node': node,
            'version': version,
            'group': group
        },
        complete: function(xhr, result, data){
            /*
            console.log(xhr.responseText)
            console.log(result)
            console.log(data)
            */
            var content = xhr.responseText;
            var aTag = document.createElement('a');
            var blob = new Blob([content]); 
            var headerName = xhr.getResponseHeader("Content-disposition").split("filename=")[1];
            //var fileName = decodeURIComponent(headerName).substring(20);
            aTag.download = headerName;
            aTag.href = URL.createObjectURL(blob);
            aTag.click();
            URL.revokeObjectURL(blob);
        }
    })
}

SyncEnv=''
SyncNode=''
SyncVersion=''
SyncGroup=''

function syncGroupLead(env, node, version, group){
    SyncEnv=env;
    SyncNode=node;
    SyncVersion=version;
    SyncGroup=group;
    $('#syncOtherGroupModel').modal('show')
}

function syncOhterGroup(){
    var syncEnv=$("#syncEnv option:selected").val()
    var password=$("#inputGroupPass").val()

    var r=confirm('请注意\r\n    此操作将此组内容以覆盖方式同步到指定环境，指定环境内已有配置会被覆盖，并且覆盖内容无法恢复，请谨慎操作！！\r\n    请确认是否同步？');
    if (r==true){
    $.ajax({
        url: "/sync/group",
        type: "GET",
        data:{
            'env' : SyncEnv,
            'node' : SyncNode,
            'version' : SyncVersion,
            'group' : SyncGroup,
            'syncEnv': syncEnv,
            'password': password
        },
        success: function(data){
            console.log(data);
            location.reload();
        }
    })
    }

}


function submitEnv(){
    var env=$("#useEnvModal option:selected").val()
    var node=$("#inputEnvNode").val()
    var password=$("#inputEnvPass").val()
    var version=$("#inputEnvVersion").val()
    console.log(env,node,password,version)
    $.ajax({
        url: "/envdata",
        type: "POST",
        data:{
            'env' : env,
            'node' : node,
            'password' : password,
            'version' : version
        },
        success: function(data){
            console.log(data)
            if (data='danger'){location.reload();}
        }
    })
}

$(document).ready(function () {
    $("#input-b9").fileinput({
        showPreview: false,
        showUpload: false,
        elErrorContainer: '#kartik-file-errors',
        allowedFileExtensions: ["text", "txt", "zip"],
        enctype:'multipart/form-data',
        uploadUrl: '/import/group'
    });
});

function addNode(){
    $('#addNodeModal').modal('show')
}

function addVersionModel(){
    $('#addVersionModal').modal('show')
}

function addVersionSubmit(){
    var version=$('#addVersionVersion').val()
    var env=document.getElementById('nowEnv').innerHTML
    var node=document.getElementById('nowNode').innerHTML
    $.ajax({
        url: '/create/version',
        type: 'POST',
        data:{
            'env': env,
            'node': node,
            'version': version
        },
        success: function(data){
            alert('添加成功')
        }
    })
}

function addNodeSubmit(){
    var env=$("#addNodeEnv option:selected").val()
    var node=$("#inputAddNode").val()
    var password=$('#inputAddNodePass').val()
    var version=$('#inputAddNodeVersion').val()
    $.ajax({
        url: '/create/node',
        type: 'POST',
        data:{
            'env' : env,
            'node' : node,
            'password' : password,
            'version' : version
        },
        success: function(data){
            alert('添加成功')
        }
    })
}

function importGroupModel(group){
    var group=group;
    var env=document.getElementById('nowEnv').innerHTML
    var node=document.getElementById('nowNode').innerHTML
    var version=document.getElementById('nowVersion').innerHTML
    $('#importGroupModal').modal('show')
    $("#importGroupValue").fileinput({
        language : 'zh',//设置文中文
        uploadUrl : "/import/group",//文件上传的url，我这里对应的是后台struts配置好的的action方法
        showCaption : true,//显示标题
        showRemove : true, //显示移除按钮
        uploadAsync : true,//默认异步上传
        textEncoding : "UTF-8",//文本编码
        allowedFileExtensions : ['text', 'txt'],//接收的文件后缀
        enctype: 'multipart/form-data',
        uploadExtraData:{
            "env": env,
            "node": node,
            "group": group,
            "version": version
        }
    }).on('filepreupload', function(event, data, previewId, index) {     //上传中
        var form = data.form, files = data.files, extra = data.extra,
        response = data.response, reader = data.reader;
        console.log('文件正在上传');
    }).on("fileuploaded", function (event, data, previewId, index) {    //一个文件上传成功
        console.log('文件上传成功！');
    }).on('fileerror', function(event, data, msg) {  //一个文件上传失败
        console.log('文件上传失败！'+data.id);
    })
}