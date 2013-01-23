(function ($) {
    $(function () {
    	function initforms(){
	    	$('#configure-conditions .rule-element input, #configure-actions .rule-element input').unbind('click').click(function(){
	    		$('#kss-spinner').show();
	    		var name = $(this).attr('name');
	    		var form = $(this).parents('form').first();
	    		var fieldset = form.parents('fieldset').first();
	    		var data = form.serialize() + "&" + name + "=1";
	    		var url = form.attr('action');
	    		$.post(url, data, function(html){
	    			var newfieldset = jq(html).find('#' + fieldset.attr('id'));
	    			fieldset.replaceWith(newfieldset);
	    			initforms();
	    			$('#kss-spinner').hide();
	    		})
	    		return false;
	    	})
    	}
    	initforms();
    });

}(jQuery));