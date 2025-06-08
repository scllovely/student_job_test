$(function () {
    // 初始化表格
    initTable();
    // 绑定搜索按钮事件
    $("#searchBtn").click(function () {
        initTable();
    });

    // 绑定删除按钮事件
    $(document).on('click', '.deleteBtn', function() {
        var id = $(this).data('id');
        deleteInfo(id);
    });

    // 绑定审核按钮事件
    $(document).on('click', '.auditBtn', function() {
        var id = $(this).data('id');
        showAuditWin(id);
    });

    // 绑定审核提交按钮事件
    $("#auditFormBtn").click(function () {
        var id = $("input[name='id']").val();
        var status = $(".auditWin select[name='status']").val();
        console.log("提交审核，ID:", id, "状态:", status);
        // 获取 CSRF 令牌
        var csrftoken = $('input[name=csrfmiddlewaretoken]').val();
        $.ajax({
            url: '/jobs/tripartite_info/audit/',
            type: 'POST',
            data: {
                id: id,
                status: status
            },
            // 设置请求头，携带 CSRF 令牌
            headers: {
                'X-CSRFToken': csrftoken
            },
            success: function (res) {
                if (res.code === 0) {
                    showAlert('审核成功');
                    $(".auditWin").addClass("fater-model-hidden");
                    initTable();
                } else {
                    showAlert(res.msg);
                }
            },
            error: function(xhr, status, error) {
                console.error("审核请求失败:", error);
                showAlert('审核失败，请重试');
            }
        });
    });
});

function initTable() {
    var collegeId = $("select[name='college_id']").val();
    var majorId = $("select[name='major_id']").val();
    var status = $("select[name='status']").val();
    var keyword = $("input[name='keyword']").val();
    var pageIndex = 1;
    var pageSize = 10;

    console.log("筛选条件:", {collegeId, majorId, status, keyword}); // 添加调试日志

    $.ajax({
        url: '/jobs/tripartite_info/page/',
        type: 'GET',
        data: {
            collegeId: collegeId,
            majorId: majorId,
            status: status,
            keyword: keyword,
            pageIndex: pageIndex,
            pageSize: pageSize
        },
        success: function (res) {
            if (res.code === 0) {
                var html = '<table class="fater-table">';
                html += '<thead><tr>';
                html += '<th>姓名</th>';
                html += '<th>学院</th>';
                html += '<th>专业</th>';
                html += '<th>公司名称</th>';
                html += '<th>公司所在地</th>';
                html += '<th>公司规模</th>';
                html += '<th>岗位名称</th>';
                html += '<th>岗位类别</th>';
                html += '<th>公司类别</th>';
                html += '<th>状态</th>';
                html += '<th>操作</th>';
                html += '</tr></thead>';
                html += '<tbody>';
                for (var i = 0; i < res.data.list.length; i++) {
                    var item = res.data.list[i];
                    html += '<tr>';
                    html += '<td>' + item.student_name + '</td>';
                    html += '<td>' + item.college_name + '</td>';
                    html += '<td>' + item.major_name + '</td>';
                    html += '<td>' + item.company_name + '</td>';
                    html += '<td>' + item.company_location + '</td>';
                    html += '<td>' + item.company_scale + '</td>';
                    html += '<td>' + item.position_name + '</td>';
                    html += '<td>' + item.position_category + '</td>';
                    html += '<td>' + item.company_category + '</td>';
                    html += '<td>' + item.status + '</td>';
                    html += '<td>';
                    html += '<button type="button" class="fater-btn fater-btn-info fater-btn-sm" onclick="viewDetail(' + item.id + ')">查看</button>';
                    html += '<button type="button" class="fater-btn fater-btn-danger fater-btn-sm deleteBtn" data-id="' + item.id + '">删除</button>';
                    if (item.status != '已通过') {
                        html += '<button type="button" class="fater-btn fater-btn-primary fater-btn-sm auditBtn" data-id="' + item.id + '">审核</button>';
                    }
                    html += '</td>';
                    html += '</tr>';
                }
                html += '</tbody></table>';
                $("#tableShow").html(html);
            }
        }
    });
}

function viewDetail(id) {
    window.location.href = '/jobs/tripartite_info/view/' + id + '/';
}

function deleteInfo(id) {
    showConfirm('确定要删除这条三方信息吗？', function() {
        // 获取 CSRF 令牌
        var csrftoken = $('input[name=csrfmiddlewaretoken]').val();
        $.ajax({
            url: '/jobs/tripartite_info/delete/',
            type: 'POST',
            data: {
                id: id
            },
            // 设置请求头，携带 CSRF 令牌
            headers: {
                'X-CSRFToken': csrftoken
            },
            success: function(res) {
                if (res.code === 0) {
                    showAlert('删除成功');
                    initTable();
                } else {
                    showAlert(res.msg);
                }
            }
        });
    });
}

function showAuditWin(id) {
    $("input[name='id']").val(id);
    $(".auditWin").removeClass("fater-model-hidden");
}
function showAlert(msg) {
    let content = `
        <div class="fater-model-alert">
            <div class="fater-model-alert-head">
                <span>系统提示</span>
                <span>×</span>
            </div>
            <div class="fater-model-alert-body">
                <div class="fater-model-alert-msg">
                    ${msg}
                </div>
                <div class="fater-model-alert-btns">
                    <button event="ok" type="button" class="fater-btn fater-btn-primary fater-btn-sm">
                        知道啦
                    </button>
                </div>
            </div>
        </div>
    `;
    // 将弹窗内容添加到页面中
    $('body').append(content);
    // 为关闭按钮添加点击事件
    $('.fater-model-alert-head span:last-child').on('click', function() {
        $('.fater-model-alert').remove();
    });
    // 为确定按钮添加点击事件
    $('.fater-model-alert-btns button[event="ok"]').on('click', function() {
        $('.fater-model-alert').remove();
    });
}

function showConfirm(msg, callback) {
    let content = `
        <div class="fater-model-alert">
            <div class="fater-model-alert-head">
                <span>系统提示</span>
                <span>×</span>
            </div>
            <div class="fater-model-alert-body">
                <div class="fater-model-alert-msg">
                    ${msg}
                </div>
                <div class="fater-model-alert-btns">
                    <button event="ok" type="button" class="fater-btn fater-btn-primary fater-btn-sm">
                        确定
                    </button>
                    <button event="cancel" type="button" class="fater-btn fater-btn-normal fater-btn-sm">
                        取消
                    </button>
                </div>
            </div>
        </div>
    `;
    // 将弹窗内容添加到页面中
    $('body').append(content);
    // 为关闭按钮添加点击事件
    $('.fater-model-alert-head span:last-child').on('click', function() {
        $('.fater-model-alert').remove();
    });
    // 为确定按钮添加点击事件
    $('.fater-model-alert-btns button[event="ok"]').on('click', function() {
        $('.fater-model-alert').remove();
        callback();
    });
    // 为取消按钮添加点击事件
    $('.fater-model-alert-btns button[event="cancel"]').on('click', function() {
        $('.fater-model-alert').remove();
    });
}
$(".fater-model-win-head span:last-child").click(function () {
    $(".auditWin").addClass("fater-model-hidden");
});