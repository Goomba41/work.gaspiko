//-------------------------------------------------------------------------------------------------
// ОБРАЩЕНИЯ К API
//-------------------------------------------------------------------------------------------------

$(document).ready(function(){
    (function ($) {
        $.fn.serializeFormJSON = function () {

            var o = {};
            var a = this.serializeArray();
            $.each(a, function () {
                if (o[this.name]) {
                    if (!o[this.name].push) {
                        o[this.name] = [o[this.name]];
                    }
                    o[this.name].push(this.value || '');
                }
                else {
                    o[this.name] = this.value || '';
                }
            });
            return o;
        };
    })(jQuery);

    $("form input[type=submit]").click(function() {
        $("input[type=submit]", $(this).parents("form")).removeAttr("clicked");
        $(this).attr("clicked", "true");
    });
});

//-------------------------------------------------------------------------------------------------
// НОВОСТИ
//-------------------------------------------------------------------------------------------------

// Удаление  новостей
function delete_news(id) {
   if (id == undefined) {
       if(confirm("Вы уверены, что хотите УДАЛИТЬ выбранные записи?")){
            var to_delete = [];
            $("input:checkbox[name=rowdelete]:checked").each(function(){
                to_delete.push($(this).val());
                $.ajax({
                    type : "DELETE",
                    url : "/API/v1.0/news/"+$(this).val(),
                    contentType: 'application/json;charset=UTF-8',
                    dataType: 'json',
                    success: function (e) {
                        message = {"type":"success", "text":"Удалено записей: "+to_delete.length};
                        localStorage.setItem("message", JSON.stringify(message));
                        location.reload(true);
                    },
                    error: function (e) {
                        message = e.responseJSON;
                        $('#message').addClass('show');
                        $('#message').addClass(message['type']);
                        $('#message').html(message['text']);
                        setTimeout("$('#message').removeClass('show');", 2500);
                    }
                });

            });
        }
   }
   else {
       if (confirm("Вы уверены, что хотите УДАЛИТЬ запись?")){
             $.ajax({
                type : "DELETE",
                url : "/API/v1.0/news/"+id,
                contentType: 'application/json;charset=UTF-8',
                dataType: 'json',
                success: function (e) {
                    message = {"type":"success", "text":"Удалена запись №"+e};
                    localStorage.setItem("message", JSON.stringify(message));
                    location.reload(true);
                },
                error: function (e) {
                    message = e.responseJSON;
                    $('#message').addClass('show');
                    $('#message').addClass(message['type']);
                    $('#message').html(message['text']);
                    setTimeout("$('#message').removeClass('show');", 2500);
                }
            });
        }
    }

}

//Добавление новости
$(document).ready(function(){
    $("form#add").submit(function(e) {
        e.preventDefault(); //Отменить стандартные действия при отправке формы (релоад)
        
        var button_type = $("input[type=submit][clicked=true]").attr("id");
        
        CKEDITOR.instances.myEditor.updateElement(); //Перед сериализацией формы обновить редактор текста, чтобы обновился его текст
        
        var data = $(this).serializeFormJSON(); //Сериализируем форму в JSON формат
        
        var formData = new FormData();
        formData.append('data', JSON.stringify(data)); //Добавляем данные в форму

        $.each($("input[type='file']"), function(i, file) { //Добавляем файлы из ввода файлов
            $.each($(this)[0].files, function(i, file) {
                formData.append('images',file);
            });
        });
        
        $.ajax({ //Отсылаем запрос
            type : "POST",
            url : $(this).attr("action"),
            cache: false,
            contentType: false,
            processData: false,
            data : formData,
            dataType: 'json',
            success: function (response) {
                    message = {"type":"success", "text":"Новость успешно добавлена!"};
                    localStorage.setItem("message", JSON.stringify(message));
                    
                    if (button_type=="with_reset") {
                        location.reload(true);
                    }
                    else if (button_type=="save") {
                        window.location = response['list'] ;
                    }
                    else if (button_type=="with_edit") {
                        window.location = response['edit'] ;
                    }
            },
            error: function(response) {
                message = response.responseJSON;
                $('#message').addClass('show');
                $('#message').addClass(message['type']);
                $('#message').html(message['text']);
                setTimeout("$('#message').removeClass('show');", 2500);
            }
        });//AJAX
        return false;
    });//form send
});

//Редактирование новости
$(document).ready(function(){
    $("form#edit").submit(function(e) {
        e.preventDefault(); //Отменить стандартные действия при отправке формы (релоад)
        
        var button_type = $("input[type=submit][clicked=true]").attr("id");
        
        CKEDITOR.instances.myEditor.updateElement(); //Перед сериализацией формы обновить редактор текста, чтобы обновился его текст
        
        var data = $(this).serializeFormJSON(); //Сериализируем форму в JSON формат
        
        var formData = new FormData();
        formData.append('data', JSON.stringify(data)); //Добавляем данные в форму

        $.each($("input[type='file']"), function(i, file) { //Добавляем файлы из ввода файлов
            $.each($(this)[0].files, function(i, file) {
                formData.append('images',file);
            });
        });
                
        $.ajax({ //Отсылаем запрос
            type : "PUT",
            url : $(this).attr("action"),
            cache: false,
            contentType: false,
            processData: false,
            data : formData,
            success: function (response) {
                    message = {"type":"success", "text":"Новость успешно отредактирована!"};
                    localStorage.setItem("message", JSON.stringify(message));
                    
                    if (button_type=="with_reset") {
                        location.reload(true);
                    }
                    else if (button_type=="save") {
                        window.location = response['list'] ;
                    }
                    else if (button_type=="with_new") {
                        window.location = response['new'] ;
                    }
            },
            error: function(response) {
                message = response.responseJSON;
                $('#message').addClass('show');
                $('#message').addClass(message['type']);
                $('#message').html(message['text']);
                setTimeout("$('#message').removeClass('show');", 2500);
            }
        });//AJAX
        return false;
    });//form send
});

//Редактирование изображений новости
$(document).ready(function(){
    $("div.card").on("click", ".news-img-btn", function(e) {
        var action = $(this).data('action')
        var id = $(this).attr('id')
        var api_url = $("div[data-imgid='"+id+"']").data('url');
        
        var formData = new FormData();
        formData.append('action', action);
        formData.append('filename', id);
        console.log(id);
        if (action=='gallery_title') {
            formData.append(action,$("input[data-imgid='"+id+"']").val())
        };

        $.ajax({
            type : "PUT",
            url : api_url,
            cache: false,
            contentType: false,
            processData: false,
            data : formData,
            success: function (response) {
                
                    message = response;
                    $('#message').addClass('show');
                    $('#message').addClass(message['type']);
                    $('#message').html(message['text']);
                    setTimeout("$('#message').removeClass('show');", 2500);
                    
                    if (message['action']=="delete") {
                        $("div[data-imgid='"+id+"']").slideUp('slow', function(){ $("div[data-imgid='"+id+"']").remove();});
                    }
                    else if (message['action']=="as_cover") {
                        var prev_id = message['prev_id'];
                        
                        $("div[data-imgid='"+prev_id+"']").find($("div.delete")).append('<button id="'+prev_id+'" title="Открепить изображение" type="button" class="float-left btn btn-sm btn-danger m-1 news-img-btn" data-action="delete"><i class="fa fa-fw p-0 fa-trash" aria-hidden="true"></i></button>');
                        $("div[data-imgid='"+prev_id+"']").find($("button[data-action=as_cover")).removeClass('btn-success');
                        $("div[data-imgid='"+prev_id+"']").find($("button[data-action=as_cover")).addClass('btn-default');
                        $("div[data-imgid='"+prev_id+"']").find($("button[data-action=as_cover")).before('<button id="'+prev_id+'" title="Вставить в галерею в новости" type="button" class="btn btn-sm btn-default m-1 float-right news-img-btn" data-action="in_gallery"><i class="fa fa-fw p-0 fa-picture-o" aria-hidden="true"></i></button>');

                        
                        $("div[data-imgid='"+id+"']").find($("button[data-action=delete")).remove();
                        $("div[data-imgid='"+id+"']").find($("button[data-action=in_gallery")).remove();
                        $("div[data-imgid='"+id+"']").find($("div[data-action=gallery_title")).remove();
                        $("div[data-imgid='"+id+"']").find($("button[data-action=as_cover")).removeClass('btn-default');
                        $("div[data-imgid='"+id+"']").find($("button[data-action=as_cover")).addClass('btn-success');
                    }
                    else if (message['action']=="in_gallery") {
                        
                        var make = message['make'];
                        var title = message['gallery_title']
                        if (make == 'add') {
                            $("div[data-imgid='"+id+"']").find($("div.actions")).after("<div class='row mt-3' data-action='gallery_title'><div class='input-group m-1'><input type='text' class='form-control' id='image-title-"+id+"' data-imgid='"+id+"' placeholder='Заголовок'><div class='input-group-append'><button id='"+id+"' title='Сохранить' type='button' class='btn btn-success news-img-btn' data-action='gallery_title'><i class='fa fa-fw p-0 fa-floppy-o' aria-hidden='true'></i></button></div></div></div>");
                            $("div[data-imgid='"+id+"']").find($("button[data-action=in_gallery")).removeClass('btn-default');
                            $("div[data-imgid='"+id+"']").find($("button[data-action=in_gallery")).addClass('btn-success');
                            $("div[data-imgid='"+id+"']").find($("input[data-imgid='"+id+"']")).val(title);
                            //alert(title);
                        }
                        else if (make == 'remove') {
                            $("div[data-imgid='"+id+"']").find($("div[data-action='gallery_title']")).remove();
                            $("div[data-imgid='"+id+"']").find($("button[data-action=in_gallery")).removeClass('btn-success');
                            $("div[data-imgid='"+id+"']").find($("button[data-action=in_gallery")).addClass('btn-default');
                        }
                    }
            },
            error: function(response) {
                message = response.responseJSON;
                $('#message').addClass('show');
                $('#message').addClass(message['type']);
                $('#message').html(message['text']);
                setTimeout("$('#message').removeClass('show');", 2500);
            }
        });

    });
});

//-------------------------------------------------------------------------------------------------
// API ИНВЕНТАРИЗАЦИИ
//-------------------------------------------------------------------------------------------------

//Получение информации об объекте
$(document).ready(function(){
$("div.info").on("click", ".btn", function(e) {
        var url = $(this).parent().data('url');
        var type = $(this).data('type');
        
        $.ajax({
            type : "GET",
            url : url,
            cache: false,
            contentType: false,
            processData: false,
            success: function (response) {

                    placing = response['placing'];
                    movements = response['movements'];
                    
                    if (type=="placing") {
                        $("div.modal-body").html("<p>Этаж: <b>"+placing['floor']+"</b>; Кабинет: <b>"+placing['room']+"</b>;</p><p>Описание: "+placing['description']+"</p>");
                        $("h4.modal-title").html("Информация об объекте: местоположение");
                    }
                    else if (type=="movements") {
                        $("h4.modal-title").html("Информация об объекте: перемещения");
                        if ( movements !== null ){
                            $("div.modal-body").html("Перемещения объекта:");
                            $(movements).each(function(index){
                                $("div.modal-body").append("<div class='row-fluid m-2'>"+this.from + " <i class='fa fa-fw fa-long-arrow-right p-0' aria-hidden='true'></i> " + this.to+" (<a href='#' title='"+this.date+"'>дата</a>)</div>" );
                            });
                        }
                        else {
                            $("div.modal-body").html("Объект не перемещался");
                        }
                    }
            },
            error: function(response) {
            }
        });

    });
});

// Удаление объектов
function delete_items(id) {
   if (id == undefined) {
       if(confirm("Вы уверены, что хотите УДАЛИТЬ выбранные записи?")){
            var to_delete = [];
            $("input:checkbox[name=rowdelete]:checked").each(function(){
                to_delete.push($(this).val());
                $.ajax({
                    type : "DELETE",
                    url : "/API/v1.0/inventar/"+$(this).val(),
                    contentType: 'application/json;charset=UTF-8',
                    dataType: 'json',
                    success: function (e) {
                        message = {"type":"success", "text":"Удалено записей: "+to_delete.length};
                        localStorage.setItem("message", JSON.stringify(message));
                        location.reload(true);
                    },
                    error: function (e) {
                        message = e.responseJSON;
                        $('#message').addClass('show');
                        $('#message').addClass(message['type']);
                        $('#message').html(message['text']);
                        setTimeout("$('#message').removeClass('show');", 2500);
                    }
                });

            });
        }
   }
   else {
       if (confirm("Вы уверены, что хотите УДАЛИТЬ запись?")){
             $.ajax({
                type : "DELETE",
                url : "/API/v1.0/inventar/"+id,
                contentType: 'application/json;charset=UTF-8',
                dataType: 'json',
                success: function (e) {
                    message = {"type":"success", "text":"Удалена запись №"+e};
                    localStorage.setItem("message", JSON.stringify(message));
                    location.reload(true);
                },
                error: function (e) {
                    message = e.responseJSON;
                    $('#message').addClass('show');
                    $('#message').addClass(message['type']);
                    $('#message').html(message['text']);
                    setTimeout("$('#message').removeClass('show');", 2500);
                }
            });
        }
    }

}

//Добавление объектов
$(document).ready(function(){
    $("form#add_item").submit(function(e) {
        e.preventDefault(); //Отменить стандартные действия при отправке формы (релоад)
        
        var button_type = $("input[type=submit][clicked=true]").attr("id");      
        var data = $(this).serializeFormJSON(); //Сериализируем форму в JSON формат
        
        var formData = new FormData();
        formData.append('data', JSON.stringify(data)); //Добавляем данные в форму
        
        $.ajax({ //Отсылаем запрос
            type : "POST",
            url : $(this).attr("action"),
            cache: false,
            contentType: false,
            processData: false,
            data : formData,
            dataType: 'json',
            success: function (response) {
                    message = {"type":"success", "text":"Объект успешно добавлен!"};
                    localStorage.setItem("message", JSON.stringify(message));
                    
                    if (button_type=="with_reset") {
                        location.reload(true);
                    }
                    else if (button_type=="save") {
                        window.location = response['list'] ;
                    }
                    else if (button_type=="with_edit") {
                        window.location = response['edit'] ;
                    }
            },
            error: function(response) {
                message = response.responseJSON;
                $('#message').addClass('show');
                $('#message').addClass(message['type']);
                $('#message').html(message['text']);
                setTimeout("$('#message').removeClass('show');", 2500);
            }
        });//AJAX
        return false;
    });//form send
});

//Редактирование новости
$(document).ready(function(){
    $("form#edit_item").submit(function(e) {
        e.preventDefault(); //Отменить стандартные действия при отправке формы (релоад)
        
        var button_type = $("input[type=submit][clicked=true]").attr("id");
        var data = $(this).serializeFormJSON(); //Сериализируем форму в JSON формат
        
        var formData = new FormData();
        formData.append('data', JSON.stringify(data)); //Добавляем данные в форму
                
        $.ajax({ //Отсылаем запрос
            type : "PUT",
            url : $(this).attr("action"),
            cache: false,
            contentType: false,
            processData: false,
            data : formData,
            success: function (response) {
                    message = {"type":"success", "text":"Объект успешно отредактирован!"};
                    localStorage.setItem("message", JSON.stringify(message));
                    
                    if (button_type=="with_reset") {
                        location.reload(true);
                    }
                    else if (button_type=="save") {
                        window.location = response['list'] ;
                    }
                    else if (button_type=="with_new") {
                        window.location = response['new'] ;
                    }
            },
            error: function(response) {
                message = response.responseJSON;
                $('#message').addClass('show');
                $('#message').addClass(message['type']);
                $('#message').html(message['text']);
                setTimeout("$('#message').removeClass('show');", 2500);
            }
        });//AJAX
        return false;
    });//form send
});


//-------------------------------------------------------------------------------------------------
// 
//-------------------------------------------------------------------------------------------------
   
   
function make(action) {
    console.log(action);
}
   
   
   
   
   
   
   
   
   function password_reset(user_id) {
        var password = prompt("Пожалуйста, введите новый пароль:");
        numbers = password.match(/\d+/g);

        if (password != null && password.length>=8 && numbers!=null) {
            $.post( "/admin/password_reset", {
                new_password: password,
                user: user_id,
            })
        }else {alert( 'Не выполнены требования к паролю! Пароль должен состоять из цифр и букв, и быть длиной не менее 8 символов.' )};
        location.reload();
    }
    function delete_users() {
       alert("Вы уверены, что хотите УДАЛИТЬ выбранные записи?");
       var yourArray = [];
       $("input:checkbox[name=rowdelete]:checked").each(function(){
            yourArray.push($(this).val());
        });
        $.post( "/admin/rows_delete", {
            param: yourArray,
            table: 'users',
            success: function (e) {
                console.log(e);
                location.reload();
            }
        })
        location.reload();
    }
    function disable_rows() {
       alert("Вы уверены, что хотите выключить выбранные записи?");
       var yourArray = [];
       $("input:checkbox[name=rowdelete]:checked").each(function(){
            yourArray.push($(this).val());
        });
        $.post( "/admin/rows_disable", {
            param: yourArray
        })
        location.reload();
    }
    $(document).ready(function () {
    $('.action-rowtoggle').change(function () {
            $('input.action-checkbox').prop('checked', this.checked);
        });
    });
    function delete_roles() {
       alert("Вы уверены, что хотите УДАЛИТЬ выбранные записи?");
       var yourArray = [];
       $("input:checkbox[name=rowdelete]:checked").each(function(){
            yourArray.push($(this).val());
        });
        $.post( "/admin/rows_delete", {
            param: yourArray,
            table: 'roles',
            success: function (e) {
                console.log(e);
                location.reload();
            }
        })
        location.reload();
    }
    function delete_departments() {
       alert("Вы уверены, что хотите УДАЛИТЬ выбранные записи?");
       var yourArray = [];
       $("input:checkbox[name=rowdelete]:checked").each(function(){
            yourArray.push($(this).val());
        });
        $.post( "/admin/rows_delete", {
            param: yourArray,
            table: 'departments',
            success: function (e) {
                console.log(e);
                location.reload();
            }
        })
        location.reload();
    }
    function delete_posts() {
       alert("Вы уверены, что хотите УДАЛИТЬ выбранные записи?");
       var yourArray = [];
       $("input:checkbox[name=rowdelete]:checked").each(function(){
            yourArray.push($(this).val());
        });
        $.post( "/admin/rows_delete", {
            param: yourArray,
            table: 'posts',
            success: function (e) {
                console.log(e);
                location.reload();
            }
        })
        location.reload();
    }
    function delete_executors() {
       alert("Вы уверены, что хотите УДАЛИТЬ выбранные записи?");
       var yourArray = [];
       $("input:checkbox[name=rowdelete]:checked").each(function(){
            yourArray.push($(this).val());
        });
        $.post( "/admin/rows_delete", {
            param: yourArray,
            table: 'executors',
            success: function (e) {
                console.log(e);
                location.reload();
            }
        })
        location.reload();
    }
    function delete_kartoteka_requests() {
       alert("Вы уверены, что хотите УДАЛИТЬ выбранные записи?");
       var yourArray = [];
       $("input:checkbox[name=rowdelete]:checked").each(function(){
            yourArray.push($(this).val());
        });
        $.post( "/admin/rows_delete", {
            param: yourArray,
            table: 'requests',
            success: function (e) {
                console.log(e);
                window.location.replace("/kartoteka/request");
            }
        })

    }

    function disable(id) {
         $.ajax({
            type : "POST",
            url : "/admin/user_disable",
            contentType: 'application/json;charset=UTF-8',
            data : JSON.stringify(id),
            dataType: 'json',
            success: function (e) {
                console.log(e);
                location.reload();
            }
        });
    }

    $(document).ready(function () {
    $('.reminder_birthday').change(function () {
            if ($('.reminder_birthday').is(':checked')) {
                $.ajax({
                    type : "POST",
                    url : "/options",
                    contentType: 'application/json;charset=UTF-8',
                    data : JSON.stringify({"reminder_birthday":"on"}),
                    dataType: 'json',
                });
            } else {
                $.ajax({
                    type : "POST",
                    url : "/options",
                    contentType: 'application/json;charset=UTF-8',
                    data : JSON.stringify({"reminder_birthday":"off"}),
                    dataType: 'json',
                });
            }
        });
    });
