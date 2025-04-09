$(document).ready(function() {
    var pageIndex = 1;
    var pageSize = 10;

    function loadData() {
        var collegeId = $('select[name="collegeId"]').val();
        var majorId = $('select[name="majorId"]').val();
        var keyword = $('input[name="keyword"]').val();

        $.ajax({
            url: "/jobs/tripartiteInfo/page/",
            type: "GET",
            data: {
                pageIndex: pageIndex,
                pageSize: pageSize,
                collegeId: collegeId,
                majorId: majorId,
                keyword: keyword
            },
            success: function(res) {
                if (res.code == 0) {
                    var data = res.data;
                    var html = '<table class="fater-table">';
                    html += '<thead><tr><th>学生姓名</th><th>企业名称</th><th>所属学院</th><th>所学专业</th><th>状态</th><th>操作</th></tr></thead>';
                    html += '<tbody>';
                    for (var i = 0; i < data.list.length; i++) {
                        var item = data.list[i];
                        html += '<tr>';
                        html += '<td>' + item.student_name + '</td>';
                        html += '<td>' + item.company_name + '</td>';
                        html += '<td>' + item.college_name + '</td>';
                        html += '<td>' + item.major_name + '</td>';
                        html += '<td>' + item.status + '</td>';
                        html += '<td><button data-id="' + item.id + '" class="auditBtn">审核</button></td>';
                        html += '</tr>';
                    }
                    html += '</tbody></table>';
                    $('#tableShow').html(html);

                    var paginationHtml = '';
                    for (var i = 1; i <= data.totalPage; i++) {
                        if (i == pageIndex) {
                            paginationHtml += '<span class="active">' + i + '</span>';
                        } else {
                            paginationHtml += '<span onclick="changePage(' + i + ')">' + i + '</span>';
                        }
                    }
                    $('#pagination').html(paginationHtml);
                }
            }
        });
    }

    $('#searchBtn').on('click', function() {
        pageIndex = 1;
        loadData();
    });

    function changePage(index) {
        pageIndex = index;
        loadData();
    }

    $(document).on('click', '.auditBtn', function() {
        var id = $(this).data('id');
        var status = prompt('请输入审核状态（通过/不通过）');
        if (status) {
            $.ajax({
                url: "/jobs/tripartiteInfo/audit/",
                type: "POST",
                data: {
                    id: id,
                    status: status
                },
                success: function(res) {
                    if (res.code == 0) {
                        $.alert(res.msg, function() {
                            loadData();
                        });
                    } else {
                        $.msg("error", res.msg);
                    }
                }
            });
        }
    });

    loadData();
});