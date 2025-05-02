$(document).ready(function() {
    var pageIndex = 1;
    var pageSize = 10;

    function loadData() {
        var collegeId = $('select[name="college_id"]').val();
        var majorId = $('select[name="major_id"]').val();
        var keyword = $('input[name="keyword"]').val();

        $.ajax({
            url: "/jobs/tripartite_info/page/",
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
                    html += '<thead>' +
                        '<tr>' +
                        '<th>姓名</th>' +
                        '<th>学院</th>' +
                        '<th>专业</th>' +
                        '<th>公司名称</th>' +
                        '<th>公司所在地</th>' +
                        '<th>公司规模</th>' +
                        '<th>薪资</th>' +
                        '<th>岗位名称</th>' +
                        '<th>岗位类别</th>' +
                        '<th>公司类别</th>' +
                        '<th>状态</th>' +
                        '<th>操作</th>' +
                        '</tr></thead>';
                    html += '<tbody>';
                    for (var i = 0; i < data.list.length; i++) {
                        var item = data.list[i];
                        html += '<tr>';
                        html += '<td>' + item.student_name + '</td>';
                        html += '<td>' + item.college_name + '</td>';
                        html += '<td>' + item.major_name + '</td>';
                        html += '<td>' + item.company_name + '</td>';
                        html += '<td>' + item.company_location + '</td>';
                        html += '<td>' + item.company_scale + '</td>';
                        html += '<td>' + item.salary + '</td>';
                        html += '<td>' + item.position_name + '</td>';
                        html += '<td>' + item.position_category + '</td>';
                        html += '<td>' + item.company_category + '</td>';
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
        $('.auditWin').removeClass('fater-model-hidden');
        $('input[name="id"]').val(id);
    });

    $('#auditFormBtn').on('click', function() {
        var id = $('input[name="id"]').val();
        var status = $('select[name="status"]').val();
        $.ajax({
            url: "/jobs/tripartite_info/audit/",
            type: "POST",
            data: {
                id: id,
                status: status
            },
            success: function(res) {
                if (res.code == 0) {
                    $.alert(res.msg, function() {
                        $('.auditWin').addClass('fater-model-hidden');
                        loadData();
                    });
                } else {
                    $.msg("error", res.msg);
                }
            }
        });
    });

    loadData();
});