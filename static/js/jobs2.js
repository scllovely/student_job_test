function handle(){

	$("button[event=upd]").on("click", (e)=>{

        $.ajax({
            url: "/jobs/jobs/info/",
            type: "GET",
            async: false,
            data:{
                id: $(e.target).attr("data"),
            },
            success: function(res){
                if(res.code == 0){

                    $.initForm("updForm", res.data);
                    $.model(".updWin");
                }else{
                    $.msg("error", res.msg);
                }
            }
        });
    });

    $("button[event=sned]").on("click", (e)=>{

        $.ajax({
            url: "/jobs/sendLogs/add/",
            type: "POST",
            async: false,
            data:{
                status: 0,
                jobId: $(e.target).attr("data"),
            },
            success: function(res){
                if(res.code == 0){

                    $.alert('投递成功', () =>{

                        window.location.reload();
                    });
                }else{
                    $.msg("error", res.msg);
                }
            }
        });
    });

    $("button[event=del]").on("click", (e)=>{

        $.confirm("确认要删除吗", () =>{

            $.ajax({
                url: "/jobs/jobs/del/",
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

$(function (){



    $(".fater-btn-form-qry").on("click", ()=>{

        tableView.where["name"] = $("[name=para1]").val();
        tableView.where["companyId"] = $("[name=para2]").val();

        $.table(tableView);
    });

    $("button[event=add]").on("click", ()=>{

        $.model(".addWin");
    });

    $("#addFormBtn").on("click", ()=>{

        let formVal = $.getFrom("addForm");

        $.ajax({
            url: "/jobs/jobs/add/",
            type: "POST",
            data: formVal,
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

    $("#updFormBtn").on("click", ()=>{

        let formVal = $.getFrom("updForm");

        $.ajax({
            url: "/jobs/jobs/upd/",
            type: "POST",
            data: formVal,
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