$(function() {

    refreshFileList()

    //Set the file name at hidden form when file is selected
    $('#id_document').on("change", function() {
        var file = this.files[0];
        if(file != null) {
            $('#id_name').val(file.name)
        }
    });

    function refreshFileList(){
        var html;
        $.ajax({
            url:'/translate/get_file_list_data/',
            dataType:'json',
        }).done(function(data){
            $(document.querySelector('body > div > table > tbody')).html(data.html);
            if (data.done_flag === 0){
                setTimeout(function(){
                    refreshFileList();
                },5000);
            }
        });
    }
});
