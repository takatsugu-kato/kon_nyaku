// //select all checkbox
// $(document).on('change','[id*=id_glossary_id]',function() {
//     $('#text_glossary').val($('#id_glossary_id').val());
//     $('#file_glossary').val($('#id_glossary_id').val());
// })



$(function() {


    var path = location.pathname
    if (path == "/translate/translator/"){
        refreshFileList()
        // auto size the textarea
        // reference: https://www.webantena.net/javascriptjquery/plugin-jquery-autosize/
        autosize(document.querySelectorAll('textarea'));
        $("textarea").on("keyup",function(){
            setTargetTextBoxHeigth();
        });

        $('#source_text').keydown(function(e){
            if (e.ctrlKey && e.keyCode == 13){
                translateText()
            }
        })

        //clear text
        $('#text_clear').click(function(){
            $('textarea').val('');
            console.log("clear")
        });

        //show delete modal window
        $('table').on('click', '.del_confirm', function(){
            $("#del_pk").text($(this).data("pk"));
            $('#del_url').attr('href', "del/" + $(this).data("pk") + "/");
        });

        //show download modal window
        $('table').on('click', '.download_confirm', function(){
            $("#download_pk").text($(this).data("pk"));
            $("#download_OK").attr('data-pk', ($(this).data("pk")));
        });

        //download file
        $('#download_OK').on('click', function (){
            // window.open("../file_download/" + $(this).data("pk"), '_blank') //no warnings but window is flash...
            window.location.assign("../file_download/" + $(this).data("pk"));
        });


        //focus del button when modal windows is displayed
        $('#deleteModal').on('shown.bs.modal', function () {
            $('#del_url').focus();
        });

        //text translation
        $('#translate_text_btn').on('click', function() {
            translateText()
        });

        //upload file
        $('#upload').on('click', function() {
            event.preventDefault();
            var csrf_token = getCookie("csrftoken");
            //set file translator language when language changed
            $('#file_translator_source_lang').val($('#id_source_lang').val());
            $('#file_translator_target_lang').val($('#id_target_lang').val());
            $('#file_glossary').val($('input[name=glossary_id]:checked').val());
            $('#file_translator_jotai').val($('#jotai').prop('checked'));
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
                var radio = document.querySelector('input[type=radio][name=glossary_id]:checked');
                radio.checked = false;
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

        //download file
        $('#downloadModal').on('click', '#download_url', function(){
            event.preventDefault();
            $('#downloadModal').modal('hide');
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

        //swap language when button click
        $('#swap_language').click(function() {
            source_lang = $('#id_source_lang').val();
            $('#id_source_lang').val($('#id_target_lang').val());
            $('#id_target_lang').val(source_lang);
            source_text = $('#source_text').val();
            $('#source_text').val($('#target_text').val());
            $('#target_text').val(source_text);
            disableJotaiCheckbox()
            refreshGlossaryListForTranslatorView()
        });

        //swap language when select same language
        $("#id_source_lang").on('focus', function () {
            previous = this.value;
        }).change(function() {
            source_lang = $('#id_source_lang').val();
            if (source_lang === $('#id_target_lang').val()){
                $('#id_target_lang').val(previous);
                disableJotaiCheckbox()
                refreshGlossaryListForTranslatorView()
            }
            previous = this.value;
        });
        $("#id_target_lang").on('focus', function () {
            previous = this.value;
        }).change(function() {
            target_lang = $('#id_target_lang').val();
            if (target_lang === $('#id_source_lang').val()){
                $('#id_source_lang').val(previous);
                disableJotaiCheckbox()
                refreshGlossaryListForTranslatorView()
            }
            previous = this.value;
        });

        $("#id_source_lang").change(function() {
            refreshGlossaryListForTranslatorView()
        });

        $("#id_target_lang").change(function() {
            disableJotaiCheckbox()
            refreshGlossaryListForTranslatorView()
        });

        //only enable jotai checkbox if selected target is Japanese
        function disableJotaiCheckbox(){
            target_lang = $('#id_target_lang').val();
            if (target_lang === "ja"){
                $('#jotai').prop({'disabled':false})
            }else{
                $('#jotai').prop({'disabled':true})
                $('#jotai').prop('checked', false)
            }
        }

        function translateText(){
            event.preventDefault();
            var csrf_token = getCookie("csrftoken");
            //set file translator language when language changed
            $('#text_translator_source_lang').val($('#id_source_lang').val());
            $('#text_translator_target_lang').val($('#id_target_lang').val());
            console.log($('input[name=glossary_id]:checked').val())
            $('#text_glossary').val($('input[name=glossary_id]:checked').val());
            $('#text_translator_jotai').val($('#jotai').prop('checked'));
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
                    $('#target_text').val(data.text)
                    var radio = document.querySelector('input[type=radio][name=glossary_id]:checked');
                    radio.checked = false;
                }
            });
        }

        function refreshGlossaryListForTranslatorView(){
            var html;
            var csrf_token = getCookie("csrftoken");
            $.ajax({
                type:'POST',
                url:'/translate/get_glossary_list_data_for_translator_view/',
                data: {
                    sl: $('#id_source_lang').val(),
                    tl: $('#id_target_lang').val()
                },
                beforeSend: function(xhr, settings) {
                    if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                        xhr.setRequestHeader("X-CSRFToken", csrf_token);
                    }
                },
                dataType:'json',
            }).done(function(data){
                $(document.querySelector('#glossary_table')).html(data.html);
            });
        }
    }

    if (path == "/translate/glossary/"){
        refreshGlossaryListForGlossaryView()
        //upload glossary
        $('#upload_glossary').on('click', function() {
            event.preventDefault();
            var csrf_token = getCookie("csrftoken");
            $.ajax({
                type:'POST',
                url:"/translate/upload_glossary/",
                data: new FormData($("#glossary_upload").get(0)),
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
                refreshGlossaryListForGlossaryView()
            });
        });

        //show delete modal window
        $('table').on('click', '.del_confirm', function(){
            $("#del_pk").text($(this).data("pk"));
            $('#del_url').attr('href', "del/" + $(this).data("pk") + "/");
        });

        //delete glossary
        $('#deleteModal').on('click', '#del_url', function(){
            event.preventDefault();
            $('#deleteModal').modal('hide');
            var href = $(this).attr('href');
            $.ajax({
                url:href,
            }).done(function(){
                refreshGlossaryListForGlossaryView()
            });
        });
    }

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

    //reflesh file list
    function refreshFileList(){
        var html;
        $.ajax({
            url:'/translate/get_file_list_data/',
            dataType:'json',
        }).done(function(data){
            $(document.querySelector('#file_table')).html(data.html);
            if (data.done_flag === 0){
                setTimeout(function(){
                    refreshFileList();
                },5000);
            }
        });
    }

    //reflesh glossary list
    function refreshGlossaryListForGlossaryView(){
        var html;
        $.ajax({
            url:'/translate/get_glossary_list_data_for_glossary_view/',
            dataType:'json',
        }).done(function(data){
            $(document.querySelector('#glossary_table')).html(data.html);
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

    function setTargetTextBoxHeigth(){
        $('#target_text').height($('#source_text').height());
    }
});
