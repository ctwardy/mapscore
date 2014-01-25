$(document).ready(function(){
	$("#testCaseTable").tablesorter();
	
	$(".testcase").mouseenter(function(evt){
		if ($(this).data('thumbexists')=="True") {
			$('.popup').html('<img src="/' + $(this).data('thumb') + '">');					
		} else {
			$('.popup').html('No thumbnail available');								
		}
		$('.popup').css({left: evt.pageX+30, top: evt.pageY-15, }).show();					
        $(this).on('mouseleave', function(){
            $('.popup').hide();
        });		
//		alert($(this).data('thumbexists'))
	});
});