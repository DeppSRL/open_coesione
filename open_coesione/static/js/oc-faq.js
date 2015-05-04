$(document).ready(function() {
    $('.faq-risposta').hide();

    $('.faq-domanda').css('cursor', 'pointer').on('click', function() {
        var self = $(this);
        $('.faq-risposta').each(function() {
            $(this).prev().is(self) ? $(this).toggle() : $(this).hide();
        });
        if (self.next().is(':visible')) {
            location.href = '#' + self.closest('.faq').attr('id');
        }
    });

    $('#faq_list').find(location.hash + '.faq:first .faq-domanda').trigger('click');

    $('#faq_list').find('a[href^="#"]').not('.faq-domanda>a').on('click', function() {
        $('#faq_list').find($(this).attr('href') + '.faq .faq-domanda').trigger('click');
    });
});
