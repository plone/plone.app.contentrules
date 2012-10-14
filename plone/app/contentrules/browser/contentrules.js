(function ($) {
    $(function () {

        var filter = [];

        // TODO find out why is it binding multiple times
        $('.btn-rule-action').unbind('click').bind('click', function(e) {
            e.preventDefault();

            var $this = $(this),
                $row = $this.parent().parent(),
                id = $this.data('value'),
                url = $this.data('url');

            $.ajax({
                type: "POST",
                url: url,
                data: 'rule-id=' + id,
                beforeSend: function() {
                    // TODO make fancy
                },
                error: function() {
                    console.log("ERROR");
                    // TODO display err message through portal message
                },
                success: function() {
                    // TODO feedback message

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
                        $this.parent().parent().remove();
                    }


                    // TODO update refresh zebra stripes on delete

                    console.log('success');
                },
                complete: function() {
                    // TODO make fancy
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