var init_charts = function(charts_container, min_regions, max_regions) {
    var $chart_container = $('#topic_chart');
    var $selectors = $chart_container.next('form');

    var $elems = $(charts_container).find('.collapse');
    $elems.on('show', function() {
        $elems.filter('.in').collapse('hide');

        !$.isEmptyObject(APP.chart) && APP.chart.destroy();

        var $self = $(this).css('height', 'auto');

        $chart_container
            .data('topic', $self.data('topic'))
            .data('location', $self.data('location'))
            .attr('data-index', $self.attr('data-index'))
            .appendTo($self.children().first()).after($selectors);
    }).on('shown', function() {
        print_line_chart($chart_container, min_regions, max_regions);
    }).first().collapse('show');
}
