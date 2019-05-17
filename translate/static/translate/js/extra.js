$(function() {

    refreshFileList()

    //show modal window
    $('table').on('click', '.del_confirm', function(){
        $("#del_pk").text($(this).data("pk"));
        $('#del_url').attr('href', "del/" + $(this).data("pk") + "/");
    });

    //upload file
    $('button').on('click', function() {
        event.preventDefault();
        var csrf_token = getCookie("csrftoken");
        $.ajax({
            type:'POST',
            url:"/translate/upload_file/",
            data: new FormData($("#file_upload").get(0)),
            processData: false,
            contentType: false,
            beforeSend: function(xhr, settings) {
                if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", csrf_token);
                    $('#id_document').val(null)
                    $('#id_name').val(null)
                    $('#display_file_name').val(null)
                }
            },
        }).done(function(data){
            $("#result").append(
                $('<div>', {
                    id: 'result_message',
                    class:'alert ' + data.type,
                    role:'alert',
                    html: data.message.join("<br/>")
                })
            )
            setTimeout("$('#result_message').fadeOut('slow').queue(function() {this.remove();})", 3000)
            refreshFileList()
        });
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
            $('#display_file_name').val(file.name)
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

    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }
});
