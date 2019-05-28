$(function() {

    refreshFileList()

    //show modal window
    $('table').on('click', '.del_confirm', function(){
        $("#del_pk").text($(this).data("pk"));
        $('#del_url').attr('href', "del/" + $(this).data("pk") + "/");
    });

    //focus del button when modal windows is displayed
    $('#deleteModal').on('shown.bs.modal', function () {
        $('#del_url').focus();
    });

    //text translation
    $('#translate_text_btn').on('click', function() {
        event.preventDefault();
        var csrf_token = getCookie("csrftoken");
        //set file translator language when language changed
        $('#text_translator_source_lang').val($('#id_source_lang').val());
        $('#text_translator_target_lang').val($('#id_target_lang').val());
        $.ajax({
            type:'POST',
            url:"/translate/translate_text/",
            data: new FormData($("#translate_text").get(0)),
            processData: false,
            contentType: false,
            beforeSend: function(xhr, settings) {
                if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", csrf_token);
                }
            },
        }).done(function(data){
            if (data.result == "error") {
                $.notify({
                    message: data.text,
                },{
                    type: "danger",
                    timer: 1000,
                    delay: 3000,
                    placement: {
                        from: 'top',
                        align: 'center'
                    }
                });
            }else{
                $('#target_text').val(data.text.replace("<br>", "\n"))
            }
        });
    });

    //upload file
    $('#upload').on('click', function() {
        event.preventDefault();
        var csrf_token = getCookie("csrftoken");
        //set file translator language when language changed
        $('#file_translator_source_lang').val($('#id_source_lang').val());
        $('#file_translator_target_lang').val($('#id_target_lang').val());
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
            $.notify({
                message: data.message.join("<br/>"),
            },{
                type: data.type,
                timer: 1000,
                delay: 3000,
                placement: {
                    from: 'top',
                    align: 'center'
                }
            });
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

    //file name input box to clickable
    $('#display_file_name').click(function() {
        $('#id_document').click();
    });

    //swap language when button click
    $('#swap_language').click(function() {
        source_lang = $('#id_source_lang').val();
        $('#id_source_lang').val($('#id_target_lang').val());
        $('#id_target_lang').val(source_lang);
    });

    //swap language when select same language
    $("#id_source_lang").on('focus', function () {
        previous = this.value;
    }).change(function() {
        source_lang = $('#id_source_lang').val();
        if (source_lang === $('#id_target_lang').val()){
            $('#id_target_lang').val(previous);
        }
        previous = this.value;
    });
    $("#id_target_lang").on('focus', function () {
        previous = this.value;
    }).change(function() {
        target_lang = $('#id_target_lang').val();
        if (target_lang === $('#id_source_lang').val()){
            $('#id_source_lang').val(previous);
        }
        previous = this.value;
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
