(function ($) {
    $(function () {

        var filter = [];

        // TODO find out why is it binding multiple times
        $('.btn-rule-action').unbind('click').bind('click', function(e) {
            e.preventDefault();

            var $this = $(this),
                $row = $this.parents('tr').first(),
                $table = $row.parent();
                id = $this.data('value'),
                url = $this.data('url');

            $.ajax({
                type: "POST",
                url: url,
                data: 'rule-id=' + id,
                beforeSend: function() {
                    $('#kss-spinner').show();
                },
                error: function() {
                    // TODO display err message through portal message
                },
                success: function() {
                    // Enable

                    if($this.hasClass('btn-rule-enable')) {
                        $row.removeClass('state-disabled').addClass('state-enabled');
                    }

                    // Disable

                    if($this.hasClass('btn-rule-disable')) {
                        $row.removeClass('state-enabled').addClass('state-disabled');
                    }

                    // DELETE

                    if($this.hasClass('btn-rule-delete')) {
                        $row.remove();
                        $table.find('tr:odd').removeClass('odd even').addClass('odd');
                        $table.find('tr:even').removeClass('odd even').addClass('even');
                    }

                },
                complete: function() {
                	$('#kss-spinner').hide();
                }
            });
        });


        $('.filter-option input').unbind('change').bind('change', function() {
            // Go through the checkboxes and map up what is the filtering criterea

            // The list of selected items is on higher scope so we can just
            // manipulate with the list, and not have to create it all the time

            // var $this = $(this);

            // // if the checkbox is selected, add it to the filter list
            // if ($this.attr('checked')) {
            //     list.push( $this.attr('id') );
            // } else {
            //     list.pop( $this.attr('id') );
            // }

            // filter the list



            // TODO update zebra stripes

        });

    });

}(jQuery));