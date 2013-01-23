(function ($) {
    $(function () {
    	function initforms(){
	    	$('#configure-conditions .rule-element input, #configure-actions .rule-element input').unbind('click').click(function(){
	    		var name = $(this).attr('name');
	    		if(name=='form.button.EditCondition' || name=='form.button.EditAction'){
	    			return true
	    		}
	    		$('#kss-spinner').show();
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