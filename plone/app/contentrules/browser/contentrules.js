(function ($) {
    $(function () {


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

    });

}(jQuery));