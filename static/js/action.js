$('#update_data').on('click', function(event) {
  event.preventDefault();
  $.ajax({
    method: 'POST',
    url: './sql/update.php',
    data:{action:'call_this'},
    success: function(data){
      $( "#response" ).html(data);

    }
});

return false;
});

$('#logout').on('click', function(event) {
  $.ajax({
    method: 'POST',
    url: './sql/logout.php',
    data:{action:'logout'},
    success: function(data){
      console.log('succesful logout')
      window.open('login.php', '_self');
    }
});

});

function checkjq(){
  window.onload = function() {
    if (window.jQuery) {
        // jQuery is loaded
        console.log("Yeah!");
        function postjq(){
          tet.preventDefault();
          $.ajax({
            method: 'POST',
            url: './register.php',
            data:{action:'jquery_loaded'},
            success: function(data){
            }
        });
    }
    }
};
};

function isEmpty( el ){
     return !$.trim(el.html())
 }
 function show_name(){if (isEmpty($('#con_pass_err'))) {
   $("#con_pass_err").hide();
 } else{
   $("#con_pass_err").hide();
 };
};

$(document).ready(function(){
    if( !$.trim( $('#con_pass_err').html() ).length ) {
      $("#con_pass_err").hide();
    }else{
      $("#con_pass_err").show();
    }
    if( !$.trim( $('#name_err').html() ).length ) {
      $("#name_err").hide();
    }else{
      $("#name_err").show();
    }
    if( !$.trim( $('#pass_err').html() ).length ) {
      $("#pass_err").hide();
    }else{
      $("#pass_err").show();
    }
  });
