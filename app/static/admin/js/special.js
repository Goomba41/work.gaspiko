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
            table: 'users'
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
    //~  Выделение всех чекбоксов
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
            table: 'roles'
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
            table: 'departments'
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
            table: 'posts'
        })
        location.reload();
    }
    function delete_news() {
       alert("Вы уверены, что хотите УДАЛИТЬ выбранные записи?");
       var yourArray = [];
       $("input:checkbox[name=rowdelete]:checked").each(function(){
            yourArray.push($(this).val());
        });
        $.post( "/admin/rows_delete", {
            param: yourArray,
            table: 'news'
        })
        location.reload();
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

    function get(id) {
         $.ajax({
            type : "POST",
            url : "/admin/appeals_status_change",
            contentType: 'application/json;charset=UTF-8',
            data : JSON.stringify({"get":id}),
            dataType: 'json',
        });
    }
    function reject(id) {
         $.ajax({
            type : "POST",
            url : "/admin/appeals_status_change",
            contentType: 'application/json;charset=UTF-8',
            data : JSON.stringify({"reject":id}),
            dataType: 'json',
        });
    }
    function done(id) {
         $.ajax({
            type : "POST",
            url : "/admin/appeals_status_change",
            contentType: 'application/json;charset=UTF-8',
            data : JSON.stringify({"done":id}),
            dataType: 'json',
        });
    }
    function checked(id) {
         $.ajax({
            type : "POST",
            url : "/admin/appeals_status_change",
            contentType: 'application/json;charset=UTF-8',
            data : JSON.stringify({"checked":id}),
            dataType: 'json',
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
