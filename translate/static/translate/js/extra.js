$(function() {

    refreshFileList()

    //show modal window
    $('table').on('click', '.del_confirm', function(){
        $("#del_pk").text($(this).data("pk"));
        $('#del_url').attr('href', "del/" + $(this).data("pk") + "/");
    });

    //delete file
    $('#deleteModal').on('click', '#del_url', function(){
        event.preventDefault();
        $('#deleteModal').modal('hide');
        var href = $(this).attr('href');
        $.ajax({
            url:href,
        }).done(function(){
            refreshFileList()
        });
    });

    //translate
    $('table').on('click', '.tra', function(){
        event.preventDefault();
        var href = $(this).attr('href');
        $.ajax({
            url:href,
        }).done(function(){
            refreshFileList()
        });
    });

    //set the file name at hidden form when file is selected
    $('#id_document').on("change", function() {
        var file = this.files[0];
        if(file != null) {
            $('#id_name').val(file.name)
        }
    });

    //reflesh file list
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
