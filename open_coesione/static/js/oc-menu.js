$(document).ready(function() {
    $('html').on('click.dropdown.data-api', function() {
        $('.submenu').children('ul').removeClass('submenu-show').addClass('submenu-hide');
    })

    $('.submenu').on('click', function(e) {
        $('.submenu').not($(this).parents('.submenu')).children('ul').removeClass('submenu-show').addClass('submenu-hide');
        $(this).children('ul').removeClass('submenu-hide').addClass('submenu-show');
        e.stopPropagation();
        e.preventDefault();
    }).children('a').append(' &raquo; ');

    $('#menu-search-type-selector').on('change', function() {
        $(this).closest('form').attr('action', '/' + $(this).val() + '/').find('input').attr('placeholder', 'Cerca tra i ' +  $(this).val());

        var is_territori = $(this).val() == 'territori';
        $('#menu-search').toggle(!is_territori);
        $('#menu-search-territori').toggle(is_territori);
    }).trigger('change');
});
