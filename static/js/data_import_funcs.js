$(document).ready(function() {
    
    console.log("data import funcs!");

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
            $.each( result, function(index, value) {
                console.log(result[index]['UPLOAD_FILENAME'])
                $("#filenames_table").append("<tr><td>"+result[index]['UPLOAD_FILENAME']+"</td><td>"+result[index]['UPLOAD_DATETIME']+"</td></tr>")
            });
        } 
    });


});

