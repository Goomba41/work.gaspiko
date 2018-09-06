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
            dataType: 'json',
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
//-------------------------------------------------------------------------------------------------
// 
//-------------------------------------------------------------------------------------------------
   
   
   
   
   
   
   
   
   
   
   
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
