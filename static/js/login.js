$(document).ready(function() {
    // 检查是否有记住的密码
    if (localStorage.getItem('rememberMe') === 'true') {
        $('input[name="userName"]').val(localStorage.getItem('userName'));
        $('input[name="passWord"]').val(localStorage.getItem('passWord'));
        $('#rememberMe').prop('checked', true);
    }

    // 点击登录按钮
    $('#loginFormBtn').click(function() {
        var userName = $('input[name="userName"]').val();
        var passWord = $('input[name="passWord"]').val();

        // 检查是否勾选记住密码
        if ($('#rememberMe').is(':checked')) {
            localStorage.setItem('rememberMe', 'true');
            localStorage.setItem('userName', userName);
            localStorage.setItem('passWord', passWord);
        } else {
            localStorage.removeItem('rememberMe');
            localStorage.removeItem('userName');
            localStorage.removeItem('passWord');
        }

        // 发送登录请求
        $.ajax({
            url: "/jobs/login/",  // 确保URL以斜杠结尾
            type: "POST",
            data: {
                "userName": userName,
                "passWord": passWord
            },
            success: function (data) {
                console.log('登录响应:', data); // 添加调试日志
                if (data.code == 0) {  // 判断条件
                    // 根据用户类型决定跳转页面
                    if (data.type == 0) {  // 管理员
                        window.location.href = "/jobs/graduate_employment_analysis/show/";
                    } else {  // 学生或其他用户
                        window.location.href = "/jobs/show/";
                    }
                } else {
                    showError(data.msg || '用户名或密码错误');
                }
            },
            error: function (xhr, status, error) {
                console.error('登录错误:', error); // 添加错误日志
                showError('登录失败，请稍后重试');
            }
        });
    });
});

function showError(message) {
    // 添加错误提示元素（如果不存在）
    if (!$('.error-message').length) {
        $('input[name="passWord"]').after('<div class="error-message">' + message + '</div>');
    }
    
    // 显示错误提示
    $('.error-message').text(message).addClass('show');
    $('input[name="passWord"]').parent().addClass('error');
    
    // 3秒后移除错误提示
    setTimeout(function() {
        $('.error-message').removeClass('show');
        $('input[name="passWord"]').parent().removeClass('error');
    }, 3000);
}