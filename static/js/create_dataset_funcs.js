$(document).ready(function() {
    console.log("create dataset funcs!");
    
    $("#loader").css("opacity", 1);
    $("#loader").show();
    $("#mainbody").css("opacity", .35);

    var dataset_data = {}

    //populate state dropdown
    $.ajax({
        type: "POST",
        url: "get_state_list",
        data: {},
        contentType: "application/json; charset=utf-8",
        dataType: 'json',
        success: function(result) {
            $("#loader").hide()
            $("#mainbody").css("opacity", 1);
            $.each( result, function( key, value ) {
                console.log(value.SITUS_STATE)
                $("#state_filter").append("<option value='"+value.SITUS_STATE+"'>"+value.SITUS_STATE+"</option>")
            });
        } 
    });

    //populate filename dropdown
    $.ajax({
        type: "POST",
        url: "get_imported_filenames",
        data: {},
        contentType: "application/json; charset=utf-8",
        dataType: 'json',
        beforeSend: function () { 
            $("#loader").show()
            $("#mainbody").css("opacity", .35);
            $("#loader").css("opacity", 1);
                
        },
        success: function(result) {
            $("#loader").hide()
            $("#mainbody").css("opacity", 1);
            $.each( result, function(key, value) {
                console.log(value.UPLOAD_FILENAME)
                $("#filename_filter").append("<option value='"+value.UPLOAD_FILENAME+"'><b>"+value.UPLOAD_FILENAME+"</b>&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp["+value.UPLOAD_DATETIME+"]</option>")
            });
        } 
    });

    $("#state_filter").change(function() {
        $("#loader").css("opacity", 1);
        $("#loader").show()
        $("#mainbody").css("opacity", .35);

        $("#county_filter").empty();

        var state = $("#state_filter").val();
        $.ajax({
            type: "POST",
            url: "get_county_list",
            data: JSON.stringify({ "state_filter" : state}),
            contentType: "application/json; charset=utf-8",
            dataType: 'json',
            success: function(result) {

                $("#mainbody").css("opacity", 1);

                $.each( result, function( key, value ) {
                    $("#county_filter").append("<option value='"+value.SITUS_COUNTY+"'>"+value.SITUS_COUNTY+"</option>")
                });
                $("#loader").hide()
            } 
        });
    });

    $("#write_dataset").hide();
    $("#write_dataset_by_ids").hide();

    //Remove classes [fix this]
    $("#filename_filter").removeClass("query");
    $("#state_filter").removeClass("query");
    $("#county_filter").removeClass("query");
    $("#linetype_filter").removeClass("query");
    $("#phone_filter").removeClass("query");
    $("#lot_acreage_filter_min").removeClass("query");
    $("#lot_acreage_filter_max").removeClass("query");
    $("#dialer_api_count").removeClass("query");
    $("#email_api_count").removeClass("query");
    $("#sms_api_count").removeClass("query");
    $("#vm_api_count").removeClass("query");

    
    $("#filename_filter_active").prop("checked", false);
    $("#state_filter_active").prop( "checked", false );
    $("#county_filter_active").prop( "checked", false );
    $("#linetype_filter_active").prop( "checked", false );
    $("#phone_filter_active").prop( "checked", false );
    $("#lot_acreage_filter_min_active").prop( "checked", false );
    $("#lot_acreage_filter_max_active").prop( "checked", false );
    $("#dialer_api_count_active").prop("checked", false);
    $("#email_api_count_active").prop("checked", false);
    $("#sms_api_count_active").prop("checked", false);
    $("#vm_api_count_active").prop("checked", false);

    $("#dialer_api_count_active").change(function(){
        if($("#dialer_api_count_active").is(':checked')) {
            $("#dialer_api_count").addClass("query");
        } else {
            $("#dialer_api_count").removeClass("query");
        }
    });

    $("#email_api_count_active").change(function() {
        if($("#email_api_count_active").is(':checked')) {
            $("#email_api_count").addClass("query");
        }else{
            $("#remove_api_count").removeClass("query");
        }
    });
        
    $("#sms_api_count_active").change(function() {
        if($("#sms_api_count_active").is(':checked')) {
            $("#sms_api_count").addClass("query");
        } else {
            $("#sms_api_count").removeClass("query");
        }
    });

    $("#vm_api_count_active").change(function() {
        if($("#vm_api_count_active").is(':checked')) {
            $("#vm_api_count").addClass("query");
        } else {
            $("#vm_api_count").removeClass("query");
        }
    });

    $("#filename_filter_active").change(function() {
        if($("#filename_filter_active").is(':checked')) {
            $("#filename_filter").addClass("query");
        } else {
            $("#filename_filter").removeClass("query");
        }
    });

    $("#state_filter_active").change(function() {
        if($("#state_filter_active").is(':checked')) {
            $("#state_filter").addClass("query");
        } else {
            $("#state_filter").removeClass("query");
        }
    });

    $("#county_filter_active").change(function() {
        if($("#county_filter_active").is(':checked')) {
            $("#county_filter").addClass("query");
        } else {
            $("#county_filter").removeClass("query");
        }
    });

    $("#linetype_filter_active").change(function() {
        if($("#linetype_filter_active").is(':checked')) {
            $("#linetype_filter").addClass("query");
        } else {
            $("#linetype_filter").removeClass("query");
        }
    });

    $("#phone_filter_active").change(function() {
        if($("#phone_filter_active").is(':checked')) {
            $("#phone_filter").addClass("query");
        } else {
            $("#phone_filter").removeClass("query");
        }
    });

    $("#lot_acreage_filter_min_active").change(function() {
        if($("#lot_acreage_filter_min_active").is(':checked')) {
            $("#lot_acreage_filter_min").addClass("query");
        } else {
            $("#lot_acreage_filter_min").removeClass("query");
        }
    });

    $("#lot_acreage_filter_max_active").change(function() {
        if($("#lot_acreage_filter_max_active").is(':checked')) {
            $("#lot_acreage_filter_max").addClass("query");
        } else {
            $("#lot_acreage_filter_max").removeClass("query");
        }
    });

    
    $("#calculate").click(function() {
        $("#loader").show()
        $("#loader").css("opacity", 1);
        $("#mainbody").css("opacity", .35);

        $("#quantity_result").empty()

        obj = {}
        
        $(".query").each(function() {
            console.log($(this).attr("id"), $(this).val() );
            $("#quantity_result").append($(this).attr("id")+"  :  "+$(this).val()+"<br>"); 
            obj[$(this).attr("id")] = $(this).val();
        });

        $("#write_dataset").empty();
        $.ajax({
            type: "POST",
            url: "filter_query",
            data: JSON.stringify(obj),
            contentType: "application/json; charset=utf-8",
            dataType: 'json',
            success: function(response) {
                $("#loader").hide()
                $("#mainbody").css("opacity", 1);
                $("#write_dataset").show();

                dataset_data['MASTER_IDS'] = response['RESULTS']
                dataset_data['QUERY'] = response['QUERY']
                dataset_data['ROW_COUNT'] = response['ROW_COUNT']
                $("#quantity_result").append("<h3> Records matching parameters: "+response['ROW_COUNT']+"</h3>")
                if(response['ROW_COUNT'] > 0){
                    $("#write_dataset").empty();
                    $("#write_dataset").append('<input type="button" id="WRITE_DATASET" name="WRITE_DATASET" value="WRITE DATASET">');
                }else{
                    $("#write_dataset").empty();
                }
            } 
        });

    });

    $("#calculate_by_ids").click(function() {
        obj = {}
        $("#quantity_result").empty()
        obj['START'] = $("#first_id").val();
        obj['END'] = $("#last_id").val();
        
        $("#loader").show()
        $("#loader").css("opacity", 1);
        $("#mainbody").css("opacity", .35);

        $("#write_dataset_by_ids").empty();
        
        $.ajax({
            type: "POST",
            url: "filter_query_by_ids",
            data: JSON.stringify(obj),
            contentType: "application/json; charset=utf-8",
            dataType: 'json',
            success: function(response) {
                $("#loader").hide()
                $("#mainbody").css("opacity", 1);

                dataset_data['MASTER_IDS'] = response['RESULTS']
                dataset_data['QUERY'] = response['QUERY']
                dataset_data['ROW_COUNT'] = response['ROW_COUNT']
                $("#quantity_result").append("<h3> Records matching parameters: "+response['ROW_COUNT']+"</h3>")
                if(response['ROW_COUNT'] > 0){
                    $("#write_dataset_by_ids").empty();
                    $("#write_dataset_by_ids").show();
                    $("#write_dataset_by_ids").append('<input type="button" id="WRITE_DATASET_BY_IDS" name="WRITE_DATASET_BY_IDS" value="WRITE DATASET IDS">');
                }else{
                    $("#write_dataset_by_ids").empty();
                }
            } 
        });

    });

    $(document).on('click','#WRITE_DATASET',function(){
        //console.log(dataset_data);
        $.ajax({
            type: "POST",
            url: "write_dataset",
            data: JSON.stringify(dataset_data),
            contentType: "application/json; charset=utf-8",
            success: function(response) {
                $("#write_dataset").append("<p><br><b>Dataset created: </b>"+response['DATASET']+"</p>");
            } 
        });

    });

    $(document).on('click','#WRITE_DATASET_BY_IDS',function(){
        console.log(dataset_data);
        $.ajax({
            type: "POST",
            url: "write_dataset",
            data: JSON.stringify(dataset_data),
            contentType: "application/json; charset=utf-8",
            success: function(response) {
                $("#write_dataset_by_ids").append("<p><br><b>Dataset created: </b>"+response['DATASET']+"</p>");
            } 
        });

    });

    $("#lot_acreage_filter_min").change(function() {
        $("#lot_acreage_filter_min_value").empty();
        val = $("#lot_acreage_filter_min").val();
        $("#lot_acreage_filter_min_value").append(val);
    });

    $("#lot_acreage_filter_max").change(function() {
        $("#lot_acreage_filter_max_value").empty();
        val = $("#lot_acreage_filter_max").val();
        $("#lot_acreage_filter_max_value").append(val);
    });

    $("#record_quantity").change(function() {
        $("#record_quantity_value").empty();
        val = $("#record_quantity").val();
        $("#record_quantity_value").append(val);
    });


});
