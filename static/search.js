$(document).ready(function () {
    $(".col-md-6").each(function()
    {
        if($(this).children().length == 0)
        {
            $(this).hide();
        }
    });
});