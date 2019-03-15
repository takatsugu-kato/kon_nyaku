$(function() {

    //Set the file name at hidden form when file is selected
    $('#id_document').on("change", function() {
        var file = this.files[0];
        if(file != null) {
            $('#id_name').val(file.name)
        }
    });
});
