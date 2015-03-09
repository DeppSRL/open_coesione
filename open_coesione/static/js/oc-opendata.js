$(document).ready(function() {
    $('a[href="#"]').on('click', function(e) {
        e.preventDefault();
    });

    $('.h3-switcher').on('switcher:toggle', function(e, state) {
        var switcher = $(this);
        switcher.toggleClass('selected', state).find('i').toggleClass('icon-chevron-up', state).toggleClass('icon-chevron-down', typeof state === 'boolean' ? !state : state);
        $('#' + switcher.data('target')).toggle(state);
    }).trigger('switcher:toggle', false).on('click', 'a', function() {
        var switcher = $(this).closest('.h3-switcher');
        $('.h3-switcher').each(function() {
            $(this).trigger('switcher:toggle', $(this).is(switcher) ? undefined : false);
        });

        location.href = '#' + switcher.attr('id');
    });

    $('.switcher').on('switcher:toggle', function(e, state) {
        var switcher = $(this);
        switcher.toggleClass('selected', state).find('i').toggleClass('icon-chevron-up', state).toggleClass('icon-chevron-down', typeof state === 'boolean' ? !state : state).closest('tr').toggleClass('selected', state);
        $('#' + switcher.data('target')).toggle(state);
    }).trigger('switcher:toggle', false).on('click', 'a', function() {
        var switcher = $(this).closest('.switcher');
        $('.switcher').each(function() {
            $(this).trigger('switcher:toggle', $(this).is(switcher) ? undefined : false);
        });
    });

    var hash = location.hash.replace('#', '');
    if (hash) {
        $('body').find('.h3-switcher#' + hash + ' a').trigger('click');
    }
});
