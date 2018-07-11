//-------------------------------------------------------------------------------------------------
// ОБРАЩЕНИЕ К API
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
                        console.log(e);
                    }
                });
            });
            window.location.href=document.location.origin+document.location.pathname;
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
                    console.log(e);
                }
            });
            window.location.href=document.location.origin+document.location.pathname;
        }
    }
}
   
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
