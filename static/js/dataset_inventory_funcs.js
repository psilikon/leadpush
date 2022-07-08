$(document).ready(function() {
    console.log("dataset inventory funcs!");

    //$("#data").hide();
 
 
    $("#mainbody").css("opacity", .35);
    $("#loader").show()
    $("#loader").css("opacity", 1);


    var selected_ds = "";
    var row_count = 0;
    

    $.ajax({
        type: "POST",
        url: "get_datasets",
        data: {},
        contentType: "application/json; charset=utf-8",
        dataType: 'json',
        success: function(result) {
            $.each( result, function( key, value ) {
                $("#datasets").append("<option value='"+value.DATASET_ID+"'>"+value.DATASET_ID+"</option>")
            });
            $("#mainbody").css("opacity", 1);
            $("#loader").hide()
        } 
    });


    $("#datasets").change(function() {
        var ds = $("#datasets").val();

        $.ajax({
            type: "POST",
            url: "get_dataset_details",
            data: JSON.stringify({'dataset':ds}),
            contentType: "application/json; charset=utf-8",
            dataType: 'json',
            beforeSend: function () { 
                console.log("beforeSend")
                
                $("#mainbody").css("opacity", .35);
                $("#loader").show()
                $("#loader").css("opacity", 1);

            },
            success: function(result) {
                console.log("success")

                $("#loader").hide()
                $("#mainbody").css("opacity", 1);

                selected_ds = result['DATASET_ID']
                var CREATION_DATE = result['CREATION_DATE']
                var DATASET_ID = result['DATASET_ID']
                var ROW_COUNT = result['ROW_COUNT']
                var SQL_QUERY = result['SQL_QUERY']
                

                $("#dataset_details").empty()
                
                $("#dataset_details").append("<table><tr><th>NAME</th><th>CREATE DATE</th><th>RECORD QTY.</th></tr><tr><td>"+DATASET_ID+"</td><td>"+CREATION_DATE+"</td><td>"+ROW_COUNT+"</td></tr></table>");
                $("#dataset_details").append("<br>SQL Query: <br>"+SQL_QUERY+"<br>");
            
            },
            complete: function() {
                console.log("complete")
                $('#dataset_table').DataTable({
                    destroy: true
                });
                
                $("#loader").hide()
                $("#mainbody").css("opacity", 1);


                $('#dataset_table').DataTable({
                    paging: false,
                    searching: false,
                    processing: true,
                    serverSide: true,
                    ajax: {
                        url: 'populate_dataTables',
                        data: {'dataset': ds},
                        type: 'POST',
                    },
                    columns: [
                        {data: 'APN'},
                        {data: 'SITUS_STATE'},
                        {data: 'SITUS_COUNTY'},
                        {data: 'LOT_ACREAGE'},
                        {data: 'PHONE'},
                        {data: 'LINE_TYPE'},
                        {data: 'EMAIL'},
                        {data: 'UPLOAD_FILENAME'}
                    ],
                });
            }
        });        

        
    });

});








