openerp.sync_chat_multi_attach = function (instance) {
    var QWeb = instance.web.qweb;
    var _t = instance.web._t;
    var mail = instance.mail;

    openerp.im_chat.Conversation.include({
        init: function(parent, c_manager, session, options) {
            var self = this;
            this._super(parent, c_manager, session, options);
            this.inputPlaceholder = 'Send a message...';
            this.attachment_ids=[];
            $.extend(this.events, {
                "click button.file_upload_btn": "chat_file_upload",
                "change #inline_attach": "input_change"
            });
        },
        start: function() {
            var self = this;
            this._super.apply(this, arguments);
            $('.smiley_load').length > 0 ? $('input.oe_im_chatview_input').width(170): $('input.oe_im_chatview_input').width(180);
            $('input.oe_im_chatview_input').after("<button type='button' class='file_upload_btn'> <img width='14' height='16' title='Add an attachment' src='/sync_chat_multi_attach/static/src/img/paperpin.png'/></button><input type='file' id='inline_attach' multiple='multiple' style='display:none'/>");
            
            self.$el.find('.oe_im_chatview_content').on('dragover',function(e) {
                e.preventDefault();
                e.stopPropagation();
                $(this).css({'opacity': 0, 'overflow': 'hidden'});
                $(this).parent().find('div.hidden_drop').addClass('hidden_drop_highlight');
            })
            .on('dragleave', function(e){self.toggle_effect(e)})
            .on('drop',function(e) {
                if(e.originalEvent.dataTransfer && e.originalEvent.dataTransfer.files.length){
                    self.toggle_effect(e);
                    self.upload_files(e.originalEvent.dataTransfer.files);
                }
            });
        },
        toggle_effect: function(e){
            var self = this;
            e.preventDefault();
            e.stopPropagation();
            self.$el.find('div.hidden_drop').removeClass('hidden_drop_highlight');
            self.$el.find('.oe_im_chatview_content').css({'opacity': 1, 'overflow': 'auto'});
        },
        get_file_format: function(){
            var fileext_to_type = {
                '7z': 'archive',
                'aac': 'audio',
                'ace': 'archive',
                'ai': 'vector',
                'aiff': 'audio',
                'apk': 'archive',
                'app': 'binary',
                'as': 'script',
                'asf': 'video',
                'ass': 'text',
                'avi': 'video',
                'bat': 'script',
                'bin': 'binary',
                'bmp': 'image',
                'bzip2': 'archive',
                'c': 'script',
                'cab': 'archive',
                'cc': 'script',
                'ccd': 'disk',
                'cdi': 'disk',
                'cdr': 'vector',
                'cer': 'certificate',
                'cgm': 'vector',
                'cmd': 'script',
                'coffee': 'script',
                'com': 'binary',
                'cpp': 'script',
                'crl': 'certificate',
                'crt': 'certificate',
                'cs': 'script',
                'csr': 'certificate',
                'css': 'html',
                'csv': 'spreadsheet',
                'cue': 'disk',
                'd': 'script',
                'dds': 'image',
                'deb': 'archive',
                'der': 'certificate',
                'djvu': 'image',
                'dmg': 'archive',
                'dng': 'image',
                'doc': 'document',
                'docx': 'document',
                'dvi': 'print',
                'eot': 'font',
                'eps': 'vector',
                'exe': 'binary',
                'exr': 'image',
                'flac': 'audio',
                'flv': 'video',
                'gif': 'webimage',
                'gz': 'archive',
                'gzip': 'archive',
                'h': 'script',
                'htm': 'html',
                'html': 'html',
                'ico': 'image',
                'icon': 'image',
                'img': 'disk',
                'iso': 'disk',
                'jar': 'archive',
                'java': 'script',
                'jp2': 'image',
                'jpe': 'webimage',
                'jpeg': 'webimage',
                'jpg': 'webimage',
                'jpx': 'image',
                'js': 'script',
                'key': 'presentation',
                'keynote': 'presentation',
                'lisp': 'script',
                'lz': 'archive',
                'lzip': 'archive',
                'm': 'script',
                'm4a': 'audio',
                'm4v': 'video',
                'mds': 'disk',
                'mdx': 'disk',
                'mid': 'audio',
                'midi': 'audio',
                'mkv': 'video',
                'mng': 'image',
                'mp2': 'audio',
                'mp3': 'audio',
                'mp4': 'video',
                'mpe': 'video',
                'mpeg': 'video',
                'mpg': 'video',
                'nrg': 'disk',
                'numbers': 'spreadsheet',
                'odg': 'vector',
                'odm': 'document',
                'odp': 'presentation',
                'ods': 'spreadsheet',
                'odt': 'document',
                'ogg': 'audio',
                'ogm': 'video',
                'otf': 'font',
                'p12': 'certificate',
                'pak': 'archive',
                'pbm': 'image',
                'pdf': 'print',
                'pem': 'certificate',
                'pfx': 'certificate',
                'pgf': 'image',
                'pgm': 'image',
                'pk3': 'archive',
                'pk4': 'archive',
                'pl': 'script',
                'png': 'webimage',
                'pnm': 'image',
                'ppm': 'image',
                'pps': 'presentation',
                'ppt': 'presentation',
                'ps': 'print',
                'psd': 'image',
                'psp': 'image',
                'py': 'script',
                'r': 'script',
                'ra': 'audio',
                'rar': 'archive',
                'rb': 'script',
                'rpm': 'archive',
                'rtf': 'text',
                'sh': 'script',
                'sub': 'disk',
                'svg': 'vector',
                'sxc': 'spreadsheet',
                'sxd': 'vector',
                'tar': 'archive',
                'tga': 'image',
                'tif': 'image',
                'tiff': 'image',
                'ttf': 'font',
                'txt': 'text',
                'vbs': 'script',
                'vc': 'spreadsheet',
                'vml': 'vector',
                'wav': 'audio',
                'webp': 'image',
                'wma': 'audio',
                'wmv': 'video',
                'woff': 'font',
                'xar': 'vector',
                'xbm': 'image',
                'xcf': 'image',
                'xhtml': 'html',
                'xls': 'spreadsheet',
                'xlsx': 'spreadsheet',
                'xml': 'html',
                'zip': 'archive'
            }
            return fileext_to_type;
        },
        chat_file_upload: function(){
            var self = this;
            self.$el.find('#inline_attach').click();
        },
        input_change: function(e){
            var self = this;
            self.upload_files(e.target.files)
        },
        escape_keep_url: function(str){
            if (str.toLowerCase().indexOf("download_attachment") >= 0){
                return str;    
            }else{
                var url_regex = /(ftp|http|https):\/\/(\w+:{0,1}\w*@)?(\S+)(:[0-9]+)?(\/|\/([\w#!:.?+=&%@!\-\/]))?/gi;
                var last = 0;
                var txt = "";
                while (true) {
                    var result = url_regex.exec(str);
                    if (! result)
                        break;
                    txt += _.escape(str.slice(last, result.index));
                    last = url_regex.lastIndex;
                    var url = _.escape(result[0]);
                    txt += '<a href="' + url + '" target="_blank">' + url + '</a>';
                }
                txt += _.escape(str.slice(last, str.length));
                
                return txt;
            }
        },
        attachments_resize_image: function (id, resize) {
            return mail.ChatterUtils.get_image(this.session, 'ir.attachment', 'datas', id, resize);
        },
        send_attachments: function(){
            var self = this;
            var file_formats = self.get_file_format();
            for (var l in this.attachment_ids) {
                var attach = this.attachment_ids[l];
                if (!attach.formating) {
                    attach.url = attach.url;
                    attach.name = mail.ChatterUtils.breakword(attach.name || attach.filename);
                    attach.formating = true;
                    attach.file_type_icon =  file_formats[attach.filename.split('.').pop()];
                }
            }
            mes = $("<div class='oe_chat_msg_attachment_list'></div>").html( instance.web.qweb.render('sync_chat_multi_attach.chat.message.attachments', {'widget': this}) );  
            self.send_message(mes[0].innerHTML, "message");
        },
        upload_files: function(files){
            var self = this;
            var total_attachements = 0;
            self.attachment_ids = [];
            _.each(files, function(file){
                var querydata = new FormData();
                querydata.append('callback', 'oe_fileupload_temp2');
                querydata.append('ufile',file);
                querydata.append('model', 'im_chat.message');
                querydata.append('id', '0');
                querydata.append('multi', 'true');
                $.ajax({
                    url: '/web/binary/upload_attachment',
                    type: 'POST',
                    data: querydata,
                    cache: false,
                    processData: false,  
                    contentType: false,
                    success: function(id){
                        ++total_attachements;
                        self.attachment_ids.push({
                            'id': parseInt(id),
                            'name': file.name,
                            'filename': file.name,
                            'url': self.session.server + "/mail/download_attachment?model=im_chat.message&id=0" + "&method=download_attachment&attachment_id=" + id,
                            'upload': false
                        });
                        (total_attachements == files.length) ? self.send_attachments() : false;
                    }
                });
            });
        },
    });
}

