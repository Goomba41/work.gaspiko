function toggleInfo() {
    $( ".sidenav" ).toggle( "blind", 500 );
	if($('.sub-menu').css('display') == 'block')
		{
			 $( ".sub-menu" ).toggle( "blind", 500 );
		}
}

function toggleSubmenu() {
    $( ".sub-menu" ).toggle( "blind", 500 );
    if($('.sidenav').css('display') == 'block')
			{
				 $( ".sidenav" ).toggle( "blind", 500 );
			}
}
