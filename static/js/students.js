function handle(){

    $("button[event=upd]").on("click", (e)=>{

        $.ajax({
            url: "/jobs/students/info/",
            type: "GET",
            async: false,
            data:{
                id: $(e.target).attr("data"),
            },
            success: function(res){
                if(res.code == 0){
                    // 预填充表单数据
                    let data = res.data;
                    let $form = $("form[name=updForm]");

                    // 基本信息
                    $form.find("input[name=id]").val(data.id);
                    $form.find("input[name=userName]").val(data.userName);
                    $form.find("input[name=passWord]").val(data.passWord);
                    $form.find("input[name=name]").val(data.name);
                    $form.find(`input[name=gender][value=${data.gender}]`).prop("checked", true);
                    $form.find("input[name=age]").val(data.age);
                    $form.find("input[name=phone]").val(data.phone);
                    $form.find("input[name=address]").val(data.address);
                    $form.find("input[name=graduation_year]").val(data.graduation_year);

                    // 处理日期格式
                    if(data.birthday) {
                        try {
                            let date = new Date(data.birthday);
                            if (!isNaN(date.getTime())) {
                                let year = date.getFullYear();
                                let month = String(date.getMonth() + 1).padStart(2, '0');
                                let day = String(date.getDate()).padStart(2, '0');
                                let formattedDate = `${year}-${month}-${day}`;
                                $form.find("input[name=birthday]").val(formattedDate);
                            }
                        } catch (e) {
                            console.error("日期格式转换错误:", e);
                        }
                    }

                    // 选择框数据
                    $form.find("select[name=collegeId]").val(data.collegeId);
                    $form.find("select[name=majorId]").val(data.majorId);
                    $form.find("select[name=class_id]").val(data.classId);

                    // 清除所有错误状态
                    $(".updWin .fater-form-item").removeClass("error");

                    // 重置密码显示状态
                    $form.find("input[name=passWord]").attr('type', 'password');
                    $form.find('.toggle-password i').removeClass('fa-eye-slash').addClass('fa-eye');

                    $.model(".updWin");
                }else{
                    $.msg("error", res.msg);
                }
            }
        });
    });

    $("button[event=del]").on("click", (e)=>{

        $.confirm("确认要删除吗", () =>{

            $.ajax({
                url: "/jobs/students/del/",
                type: "POST",
                async: false,
                data:{
                    id: $(e.target).attr("data"),
                },
                success: function(res){
                    if(res.code == 0){
                        $.alert(res.msg, () =>{

                            window.location.reload();
                        });
                    }else{
                        $.msg("error", res.msg);
                    }
                }
            });
        });
    });
}

$(function () {
    // 添加密码显示切换功能
    $('.toggle-password').on('click', function() {
        const passwordInput = $(this).siblings('input');
        const icon = $(this).find('i');

        if (passwordInput.attr('type') === 'password') {
            passwordInput.attr('type', 'text');
            icon.removeClass('fa-eye').addClass('fa-eye-slash');
        } else {
            passwordInput.attr('type', 'password');
            icon.removeClass('fa-eye-slash').addClass('fa-eye');
        }
    });

    // 确保表格初始化和事件绑定在 DOM 加载完成后执行
    let tableView = {
        el: "#tableShow",
        url: "/jobs/students/page/",
        method: "GET",
        where: {
            pageIndex: 1,
            pageSize: 10
        },
        page: true,
        cols: [
            {
                field: "id",
                title: "学号",
                align: "center",
            },
            {
                field: "name",
                title: "姓名",
                align: "center",
            },
            {
                field: "gender",
                title: "性别",
                align: "center",
            },
            {
                field: "age",
                title: "年龄",
                align: "center",
            },
            {
                field: "phone",
                title: "电话",
                align: "center",
            },
            {
                field: "address",
                title: "籍贯",
                align: "center",
            },
            {
                field: "birthday",
                title: "出生日期",
                align: "center",
            },
            {
                field: "collegeName",
                title: "所属学院",
                align: "center",
            },
            {
                field: "majorName",
                title: "专业",
                align: "center",
            },
            {
                field: "className",
                title: "班级",
                align: "center",
            },
            {
                title: "学生状态",
                align: "center",
                template: (d) => {
                    return d.status == 0 ? '待业' : '就业'
                }
            },
            {
                title: "操作",
                template: (d) => {
                    return `
                            <button type="button" event="upd" data="${d.id}" class="fater-btn fater-btn-primary fater-btn-sm">
                                <span data="${d.id}" class="fa fa-edit"></span>
                            </button>
                            <button type="button" event="del" data="${d.id}" class="fater-btn fater-btn-danger fater-btn-sm">
                                <span data="${d.id}" class="fa fa-trash"></span>
                            </button>
                            `;
                }
            }
        ],
        binds: (d) => {
            handle();
        }
    };
    $.table(tableView);

    $(".fater-btn-form-qry").on("click", () => {
        tableView.where["userName"] = $("[name=para1]").val();
        tableView.where["name"] = $("[name=para2]").val();
        tableView.where["phone"] = $("[name=para3]").val();
        tableView.where["collegeId"] = $("[name=para4]").val();
        tableView.where["majorId"] = $("[name=para5]").val();
        tableView.where["classId"] = $("[name=para6]").val();

        $.table(tableView);
    });

    $("button[event=add]").on("click", () => {
        $.model(".addWin");
    });

    // 表单验证
    function validateForm(formData) {
        let isValid = true;
        const $form = $(".addWin form");
        
        // 验证毕业年份
        const graduationYear = $form.find("input[name='graduation_year']").val();
        if (!graduationYear) {
            $form.find("input[name='graduation_year']").next(".error-message").text("请输入毕业年份").show();
            isValid = false;
        } else if (!/^\d{4}$/.test(graduationYear)) {
            $form.find("input[name='graduation_year']").next(".error-message").text("毕业年份必须是4位数字").show();
            isValid = false;
        } else {
            $form.find("input[name='graduation_year']").next(".error-message").hide();
        }

        // 验证其他必填字段
        $form.find("input[required]").each(function() {
            const $input = $(this);
            if (!$input.val()) {
                $input.next(".error-message").show();
                isValid = false;
            } else {
                $input.next(".error-message").hide();
            }
        });

        return isValid;
    }

    // 添加学生信息
    $("#addFormBtn").on("click", function() {
        const $form = $(".addWin form");
        if (!validateForm()) {
            return;
        }

        const formData = {
            userName: $form.find("input[name='userName']").val(),
            passWord: $form.find("input[name='passWord']").val(),
            name: $form.find("input[name='name']").val(),
            gender: $form.find("input[name='gender']").val(),
            age: $form.find("input[name='age']").val(),
            phone: $form.find("input[name='phone']").val(),
            type: $form.find("input[name='type']").val(),
            id: $form.find("input[name='id']").val(),
            address: $form.find("input[name='address']").val(),
            birthday: $form.find("input[name='birthday']").val(),
            status: $form.find("input[name='status']").val(),
            collegeId: $form.find("select[name='collegeId']").val(),
            majorId: $form.find("select[name='majorId']").val(),
            classId: $form.find("select[name='classId']").val(),
            graduation_year: parseInt($form.find("input[name='graduation_year']").val())
        };

        $.ajax({
            url: "/jobs/students/add/",
            type: "POST",
            data: formData,
            success: function(res) {
                if (res.code === 0) {
                    $.alert("添加成功", () => {
                        window.location.reload();
                    });
                } else {
                    $.msg("error", res.msg);
                }
            },
            error: function(xhr) {
                $.msg("error", "添加失败：" + xhr.responseText);
            }
        });
    });

    // 添加实时验证
    $(".fater-form input, .fater-form select").on("input change", function() {
        let $field = $(this).closest('.fater-form-item');
        let value = $(this).val();
        let fieldName = $(this).attr('name');

        if (value) {
            let isValid = true;
            let errorMessage = '';

            // 特殊字段格式验证
            switch(fieldName) {
                case 'id':
                    if (!/^\d{1,16}$/.test(value)) {
                        isValid = false;
                        errorMessage = '学号必须为不超过16位的数字';
                    }
                    break;
                case 'phone':
                    if (!/^\d{11}$/.test(value)) {
                        isValid = false;
                        errorMessage = '请输入11位手机号码';
                    }
                    break;
                case 'age':
                    if (!/^\d{1,2}$/.test(value) || parseInt(value) > 99) {
                        isValid = false;
                        errorMessage = '年龄必须为不超过2位的数字';
                    }
                    break;
            }

            if (isValid) {
                $field.removeClass("error");
            } else {
                $field.addClass("error");
                $field.find('.error-message').text(errorMessage);
            }
        }
    });

    $("#updFormBtn").on("click", () => {
        let formVal = $.getFrom("updForm");
        let isValid = true;
        
        // 清除所有错误状态
        $(".updWin .fater-form-item").removeClass("error");

        // 检查必填字段
        let requiredFields = {
            'id': '学生学号',
            'userName': '学生账号',
            'passWord': '学生密码',
            'name': '学生姓名',
            'gender': '学生性别',
            'age': '学生年龄',
            'phone': '联系电话',
            'address': '学生籍贯',
            'collegeId': '所属学院',
            'majorId': '所学专业',
            'class_id': '所在班级',
            'graduation_year': '毕业年份'
        };

        // 验证每个字段
        for (let field in requiredFields) {
            let value;
            let $field = $(`[name="${field}"]`).closest('.fater-form-item');
            
            // 特殊处理数字类型输入
            if (field === 'graduation_year') {
                value = $(".updWin input[name='graduation_year']").val();
                console.log("毕业年份值:", value); // 调试日志
            } else {
                value = formVal[field];
            }

            if (!value) {
                $field.addClass("error");
                $field.find('.error-message').text(`请输入${requiredFields[field]}`);
                isValid = false;
            } else {
                // 特殊字段格式验证
                switch(field) {
                    case 'id':
                        if (!/^\d{1,16}$/.test(value)) {
                            $field.addClass("error");
                            $field.find('.error-message').text('学号必须为不超过16位的数字');
                            isValid = false;
                        }
                        break;
                    case 'phone':
                        if (!/^\d{11}$/.test(value)) {
                            $field.addClass("error");
                            $field.find('.error-message').text('请输入11位手机号码');
                            isValid = false;
                        }
                        break;
                    case 'age':
                        if (!/^\d{1,2}$/.test(value) || parseInt(value) > 99) {
                            $field.addClass("error");
                            $field.find('.error-message').text('年龄必须为不超过2位的数字');
                            isValid = false;
                        }
                        break;
                    case 'graduation_year':
                        if (!/^\d{4}$/.test(value)) {
                            $field.addClass("error");
                            $field.find('.error-message').text('请输入4位数字的毕业年份');
                            isValid = false;
                        }
                        break;
                    case 'address':
                        if (!/^[\u4e00-\u9fa5a-zA-Z]+$/.test(value)) {
                            $field.addClass("error");
                            $field.find('.error-message').text('籍贯只能包含中文和英文字母');
                            isValid = false;
                        }
                        break;
                    default:
                        $field.removeClass("error");
                }
            }
        }

        if (!isValid) {
            return;
        }

        // 确保毕业年份被包含在提交数据中
        formVal.graduation_year = $(".updWin input[name='graduation_year']").val();
        console.log("提交的表单数据:", formVal); // 调试日志

        $.ajax({
            url: "/jobs/students/upd/",
            type: "POST",
            data: formVal,
            success: function (res) {
                if (res.code == 0) {
                    $.alert(res.msg, () => {
                        window.location.reload();
                    });
                } else {
                    $.msg("error", res.msg);
                }
            }
        });
    });

    // 为修改表单添加实时验证
    $(".updWin .fater-form input, .updWin .fater-form select").on("input change", function() {
        let $field = $(this).closest('.fater-form-item');
        let value = $(this).val();
        let fieldName = $(this).attr('name');

        if (value) {
            let isValid = true;
            let errorMessage = '';

            // 特殊字段格式验证
            switch(fieldName) {
                case 'id':
                    if (!/^\d{1,16}$/.test(value)) {
                        isValid = false;
                        errorMessage = '学号必须为不超过16位的数字';
                    }
                    break;
                case 'phone':
                    if (!/^\d{11}$/.test(value)) {
                        isValid = false;
                        errorMessage = '请输入11位手机号码';
                    }
                    break;
                case 'age':
                    if (!/^\d{1,2}$/.test(value) || parseInt(value) > 99) {
                        isValid = false;
                        errorMessage = '年龄必须为不超过2位的数字';
                    }
                    break;
                case 'address':
                    if (!/^[\u4e00-\u9fa5a-zA-Z]+$/.test(value)) {
                        isValid = false;
                        errorMessage = '籍贯只能包含中文和英文字母';
                    }
                    break;
            }

            if (isValid) {
                $field.removeClass("error");
            } else {
                $field.addClass("error");
                $field.find('.error-message').text(errorMessage);
            }
        }
    });
});

function handle() {
    $("button[event=upd]").on("click", (e) => {
        $.ajax({
            url: "/jobs/students/info/",
            type: "GET",
            async: false,
            data: {
                id: $(e.target).attr("data"),
            },
            success: function (res) {
                if (res.code == 0) {
                    // 预填充表单数据
                    let data = res.data;
                    let $form = $("form[name=updForm]");

                    // 基本信息
                    $form.find("input[name=id]").val(data.id);
                    $form.find("input[name=userName]").val(data.userName);
                    $form.find("input[name=passWord]").val(data.passWord);
                    $form.find("input[name=name]").val(data.name);
                    $form.find(`input[name=gender][value=${data.gender}]`).prop("checked", true);
                    $form.find("input[name=age]").val(data.age);
                    $form.find("input[name=phone]").val(data.phone);
                    $form.find("input[name=address]").val(data.address);
                    $form.find("input[name=graduation_year]").val(data.graduation_year);

                    // 处理日期格式
                    if(data.birthday) {
                        try {
                            let date = new Date(data.birthday);
                            if (!isNaN(date.getTime())) {
                                let year = date.getFullYear();
                                let month = String(date.getMonth() + 1).padStart(2, '0');
                                let day = String(date.getDate()).padStart(2, '0');
                                let formattedDate = `${year}-${month}-${day}`;
                                $form.find("input[name=birthday]").val(formattedDate);
                            }
                        } catch (e) {
                            console.error("日期格式转换错误:", e);
                        }
                    }

                    // 选择框数据
                    $form.find("select[name=collegeId]").val(data.collegeId);
                    $form.find("select[name=majorId]").val(data.majorId);
                    $form.find("select[name=class_id]").val(data.classId);

                    // 清除所有错误状态
                    $(".updWin .fater-form-item").removeClass("error");

                    // 重置密码显示状态
                    $form.find("input[name=passWord]").attr('type', 'password');
                    $form.find('.toggle-password i').removeClass('fa-eye-slash').addClass('fa-eye');

                    $.model(".updWin");
                } else {
                    $.msg("error", res.msg);
                }
            }
        });
    });

    $("button[event=del]").on("click", (e) => {
        $.confirm("确认要删除吗", () => {
            $.ajax({
                url: "/jobs/students/del/",
                type: "POST",
                async: false,
                data: {
                    id: $(e.target).attr("data"),
                },
                success: function (res) {
                    if (res.code == 0) {
                        $.alert(res.msg, () => {
                            window.location.reload();
                        });
                    } else {
                        $.msg("error", res.msg);
                    }
                }
            });
        });
    });
}