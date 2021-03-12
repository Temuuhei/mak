openerp.sync_chat_notification = function (instance) {
    var QWeb = instance.web.qweb;
    var _t = instance.web._t;

    openerp.im_chat.ConversationManager.include({
        received_message: function(message) {
            var self = this;
            this._super.apply(this, arguments);
            if (! this.get("window_focus")) {
				if (this.session.uid != message.from_id[0]){
		            Notification.requestPermission(function(permission){
		                var image_url = openerp.session.url('/web/binary/image', {model:'res.users', field: 'image_small', id: message.from_id[0]});
		                var message_content = (typeof message.rem_html_smiley === "undefined") ? message.message : message.rem_html_smiley;
		                var notification = new Notification(message.from_id[1],{body:message_content,icon:image_url,dir:'auto'});
		                setTimeout(function(){
		                    notification.close();
		                },4000);
		            });
				}
            }
        }
    });
}
