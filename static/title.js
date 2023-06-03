document.addEventListener("DOMContentLoaded", function(event) {
       $(".menu").addClass("clean-menu");
 });


$(document).ready(function() {
  var spanTitles = $("span");
  var back = $("#back-title");

  back.addClass("activate-back");
  setTimeout(function() {
    spanTitles.addClass("active");
  }, 200);

  setTimeout(function(){
    $(".menu").removeClass("clean-menu");
    $("#title").addClass("title");
  }, 4000);
});

