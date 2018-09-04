window.onload = function() {
    $( "#page-preloader" ).fadeOut(1000);
    if (localStorage.getItem('message')) {
      message = JSON.parse(localStorage.getItem('message'));
      $('#message').addClass('show');
      $('#message').addClass(message['type']);
      $('#message').html(message['text']);
      localStorage.removeItem('message')
      setTimeout("$('#message').removeClass('show');", 2500);
    }
  };



