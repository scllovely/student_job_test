$(document).ready(function() {
    $('#updateBtn').on('click', function() {
        var company_name = $('input[name="company_name"]').val();
        $.ajax({
            url: "/jobs/tripartiteInfo/student/update/",
            type: "POST",
            data: {
                company_name: company_name
            },
            success: function(res) {
                if (res.code == 0) {
                    $.alert(res.msg, function() {
                        location.reload();
                    });
                } else {
                    $.msg("error", res.msg);
                }
            }
        });
    });

    $('#submitBtn').on('click', function() {
        $.ajax({
            url: "/jobs/tripartiteInfo/student/submit/",
            type: "POST",
            success: function(res) {
                if (res.code == 0) {
                    $.alert(res.msg, function() {
                        location.reload();
                    });
                } else {
                    $.msg("error", res.msg);
                }
            }
        });
    });
});