$(document).ready(function() {        
        $('[href="'+document.location.href.match(/.*:\/\/[^\/]+(.*)/)[1]+'"]')
          .addClass("active")
          .parent("li").addClass("active");
});
