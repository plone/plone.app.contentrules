(function ($) {
    $(function () {

    	function updatezebra(table){
            table.find('tr:visible:odd').removeClass('odd even').addClass('odd');
            table.find('tr:visible:even').removeClass('odd even').addClass('even');
    	}

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
                        updatezebra($table);
                    }

                },
                complete: function() {
                	$('#kss-spinner').hide();
                }
            });
        });


        $('.filter-option input').unbind('change').bind('change', function() {
            // Go through the checkboxes and map up what is the filtering criterea
        	var $table = $('#rules_table_form table');
        	state_filters = $('.state-filters input:checked');
        	type_filters = $('.type-filters input:checked');

        	$table.find('tr').show();
        	if(state_filters.length > 0){
        		$('.state-filters input:not(:checked)').each(function(){
        			$table.find('.' + this.id).hide();
        		});
        	}
        	if(type_filters.length > 0){
        		$('.type-filters input:not(:checked)').each(function(){
        			$table.find('.' + this.id).hide();
        		});
        	}
            updatezebra($table);
        });

    });

}(jQuery));