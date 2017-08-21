openerp.sync_smiley_chat = function (instance) {
    var QWeb = instance.web.qweb;
    var _t = instance.web._t;
    var mail = instance.mail;

    openerp.im_chat.Conversation.include({
        init: function(parent, c_manager, session, options) {
            var self = this;
            this._super(parent, c_manager, session, options);
            this.inputPlaceholder = 'Send a message...';
            $.extend(this.events, {
                "click .smiley_load": "smiley_load",
                "click .smiley-list .smiley": "put_smiley",
                "click .close-smiley": "close_smiley",
                "click .oe_im_chatview_content": "close_smiley",
            })
        },
        start: function() {
            var self = this;
            this._super.apply(this, arguments);
            $('.file_upload_btn').length > 0 ? $('input.oe_im_chatview_input').width(172): $('input.oe_im_chatview_input').width(190);
            $('input.oe_im_chatview_input').before("<span class='smiley_load'><img width='20' height='20' title='Add an emoticon' src='/sync_smiley_chat/static/src/img/smileylogo.png' class='grayscale'/></span>");
        },
        keydown: function(){
            var self = this;
            this._super.apply(this, arguments);
            this.$('.smiley-list').hide();
        },
        get_smiley_list: function(){
            var smileys = {
                ":D" : "<img src='/sync_smiley_chat/static/src/img/smile.png'/>",
                ":|" : "<img src='/sync_smiley_chat/static/src/img/neutral.png'/>",
                ":P" : "<img src='/sync_smiley_chat/static/src/img/yum.png'/>",
                ";)" : "<img src='/sync_smiley_chat/static/src/img/wink.png'/>",
                ":x" : "<img src='/sync_smiley_chat/static/src/img/stuck_out_tongue.png'/>",
                ":o" : "<img src='/sync_smiley_chat/static/src/img/open_mouth.png'/>",
                ":))" : "<img src='/sync_smiley_chat/static/src/img/laugh.png'/>",
                ":-/" : "<img src='/sync_smiley_chat/static/src/img/confused.png'/>",
                ":(" : "<img src='/sync_smiley_chat/static/src/img/sad.png'/>",
                ":-o" : "<img src='/sync_smiley_chat/static/src/img/scream.png'/>",
                ":3" : "<img src='/sync_smiley_chat/static/src/img/cat.png'/>",
                ":v" : "<img src='/sync_smiley_chat/static/src/img/ghost.png'/>",
                ":(|)" : "<img src='/sync_smiley_chat/static/src/img/boar.png'/>",
                ":cookie" : "<img src='/sync_smiley_chat/static/src/img/cookie.png'/>",
                ":(y)" : "<img src='/sync_smiley_chat/static/src/img/thumbsup.png'/>",
                ":(n)" : "<img src='/sync_smiley_chat/static/src/img/thumbsdown.png'/>",
                ":poop" : "<img src='/sync_smiley_chat/static/src/img/poop.png'/>",
                ":trollface" : "<img src='/sync_smiley_chat/static/src/img/trollface.png'/>",
                ":postalhorn" : "<img src='/sync_smiley_chat/static/src/img/postal_horn.png'/>",
                ":mwt" : "<img src='/sync_smiley_chat/static/src/img/man_with_turban.png'/>",
                ":man" : "<img src='/sync_smiley_chat/static/src/img/man.png'/>",
                ":postalhorn" : "<img src='/sync_smiley_chat/static/src/img/postal_horn.png'/>",
                ":postalhorn" : "<img src='/sync_smiley_chat/static/src/img/postal_horn.png'/>",
                ":beer" : "<img src='/sync_smiley_chat/static/src/img/beer.png'/>",
                ":pinky" : "<img src='/sync_smiley_chat/static/src/img/pinky.png'/>",
                ":musti" : "<img src='/sync_smiley_chat/static/src/img/musti.png'/>"
            };
            return smileys;
        },
        smiley: function(str){
            var self = this;
            var re_escape = function(str){
                return String(str).replace(/([.*+?=^!:${}()|[\]\/\\])/g, '\\$1');
             };
             var smileys = this.get_smiley_list();
            _.each(_.keys(smileys), function(key){
                var strarray=str.split(':');
                _.each(strarray, function(splitstr){
                    str = str.replace( new RegExp("(?:^|\\s)(" + re_escape(key) + ")(?:\\s|$)"), ' <span class="smiley">' + smileys[key] + '</span> ');
                });
            });
            return str;
        },
        put_smiley:function(el){
            this.$("input").val(this.$("input").val() + " " + el.currentTarget.id);
        },
        close_smiley: function(){
            this.$('.smiley-list').hide();
        },
        smiley_load: function(){
            var self = this;
            if (this.$('.smiley-list').is(":hidden")){
                this.$('.smiley-list').show();
            } else {
                this.$('.smiley-list').hide();
            }
            this.$('.smiley-list').find("span").remove();
            var smileys = this.get_smiley_list();
            _.each(smileys, function(smiley, key){
                self.$(".smiley-list").append("<span id=" + key + " class='smiley'>" + smiley + "</span>");
            });
        },
        insert_messages: function(messages){
            var self = this;
            // avoid duplicated messages
            messages = _.filter(messages, function(m){ return !_.contains(_.pluck(self.get("messages"), 'id'), m.id) ; });
            // escape the message content and set the timezone
            _.map(messages, function(m){
                if(!m.from_id){
                    m.from_id = [false, self.options["defaultUsername"]];
                }
                m.message = self.escape_keep_url(m.message);
                // TO Remove HTML from Smiley
                m.rem_html_smiley = m.message;
                // End
                m.message = self.smiley(m.message);
                m.create_date = Date.parse(m.create_date).setTimezone("UTC").toString("yyyy-MM-dd HH:mm:ss");
                return m;
            });
            this.set("messages", _.sortBy(this.get("messages").concat(messages), function(m){ return m.id; }));
        }
    });
}
