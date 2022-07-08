$(document).ready(function() {
    console.log("api endpoints funcs!");

    
    $("#loader").show()
    $("#loader").css("opacity", 1);
    $("#mainbody").css("opacity", .35);

    $("#vicidial_button").hide()
    $("#create_sms_lists_button").hide()
    $("#email_lists_button").hide()
    $("#vmdrop_push").hide()

    var selected_ds = "";
    var row_count = 0;

    $.ajax({
        type: "POST",
        url: "get_datasets",
        data: {},
        contentType: "application/json; charset=utf-8",
        dataType: 'json',
        success: function(result) {
            $("#loader").hide()
            $("#mainbody").css("opacity", 1);

            $.each( result, function( key, value ) {
                $("#datasets").append("<option value='"+value.DATASET_ID+"'>"+value.DATASET_ID+"</option>")
            });
        } 
    });
    
    $("#datasets").change(function() {
        $("#loader").show()
        $("#loader").css("opacity", 1);
        $("#mainbody").css("opacity", .35);

        var ds = $("#datasets").val();

        $.ajax({
            type: "POST",
            url: "get_dataset_details",
            data: JSON.stringify({'dataset':ds}),
            contentType: "application/json; charset=utf-8",
            dataType: 'json',
            success: function(result) {
                $("#loader").hide()
                $("#mainbody").css("opacity", 1);

                console.log(result)
                selected_ds = result['DATASET_ID']
                var CREATION_DATE = result['CREATION_DATE']
                var DATASET_ID = result['DATASET_ID']
                var ROW_COUNT = result['ROW_COUNT']
                var SQL_QUERY = result['SQL_QUERY']
                row_count = result['ROW_COUNT']

                $("#dataset_details").empty()
                $("#vicidial_button").show()
                $("#create_sms_lists_button").show()
                $("#email_lists_button").show()
                $("#vmdrop_push").show()
                $("#dataset_details").append("<br>Creation date: <b>"+CREATION_DATE+"</b><br>Record count: <b>"+ROW_COUNT+"</b><br><b>"+SQL_QUERY+"</b>");
            } 
        });        
    });

    $("#push_to_vicidial").click(function() {
        console.log("PUSH TO VICIDIAL")
        $("#vici_push_output").empty()

        var ds = $("#datasets").val();

        $.ajax({
            type: "POST",
            url: "push_to_vicidial",
            data: JSON.stringify({'dataset' : ds}),
            contentType: "application/json; charset=utf-8",
            dataType: 'json',
            beforeSend: function () { 
                console.log("beforeSend")
                $("#mainbody").css("opacity", .35);
                $("#loader").css("opacity", 1);
                $("#loader").show()
            },
            success: function(result) {
                console.log("success")
                $("#vici_push_output").append(result['MSG']+"<br>")
                $("#vici_push_output").append("Errors: "+result['ERROR']+"<br>")
                $("#vici_push_output").append("Successes: "+result['SUCCESS']);
            },
            complete: function(result) {
                $("#loader").hide();
                $("#mainbody").css("opacity", 1);
            }
        });        
    });


    $("#create_sms_lists").click(function() {
        console.log("CREATE SMS LISTS")
        $("#sms_push_output").empty()

        var ds = $("#datasets").val();
        var check_sms_agent_list = new Array()
        var checked_agents = $('.sms_agent:checkbox:checked').map(function() { return this.value; }).get();
        

        var sms_template_time = $("#sms_template_time").val();

        if (checked_agents.length == 0 || !sms_template_time){
            alert("Please select agents and template time.")
        }else{
            alert("Starting SMS list and campaign procedure.")
            $.ajax({
                type: "POST",
                url: "create_sms_lists",
                data: JSON.stringify({'sms_agents' : checked_agents, 'ds': selected_ds, 'row_count': row_count, 'part_of_day': sms_template_time}),
                contentType: "application/json; charset=utf-8",
                dataType: 'json',
                beforeSend: function () { 
                    $("#mainbody").css("opacity", .35);
                    $("#loader").css("opacity", 1);
                    $("#loader").show()
                },
                success: function(result) {
                    $("#loader").hide();
                    $("#mainbody").css("opacity", 1);
                    $("#sms_push_output").append(result['CONTACTS_MSG']+"<br>")
                    $("#sms_push_output").append(result['LISTS_MSG'])
                    $("#sms_push_output").append(result['CAMPAIGNS_MSG'])

                },
                complete: function(result) {
                    $("#loader").hide();
                    $("#mainbody").css("opacity", 1);
                }
            });        
        }
    });


    $("#vmdrop_push").click(function() {
        console.log("DROP.CO PUSH")
        $("#vmdrop_output").empty()

        var ds = $("#datasets").val();
        var drop_campaign = $("#vmdrop_campaign").val();

        if(drop_campaign == 'AFTERNOON' || drop_campaign == 'MORNING'){
            console.log(drop_campaign+" SELECTED DROP.CO CAMPAIGN")
            $.ajax({
                type: "POST",
                url: "vmdrop_push",
                data: JSON.stringify({'drop_campaign': drop_campaign, 'dataset': ds}),
                contentType: "application/json; charset=utf-8",
                dataType: 'json',
                beforeSend: function () { 
                    $("#mainbody").css("opacity", .35);
                    $("#loader").css("opacity", 1);
                    $("#loader").show()
                },
                success: function(result) {
                    $("#loader").hide();
                    $("#mainbody").css("opacity", 1);
                    console.log("AJAX SUCCESS")
                    console.log(result)
                    $("#vmdrop_output").append("<p>Status: <b>"+result['STATUS']+"</b><br>Success count: <b>"+result['SUCCESS_COUNT']+"</b></p>")
                },
                complete: function(result) {
                    $("#loader").hide();
                    $("#mainbody").css("opacity", 1);
                    $("#vmdrop_output").append()
                },
            });        
        }else{
            alert("NO DROP.CO CAMPAIGN SELECTED")
        }
    });


});