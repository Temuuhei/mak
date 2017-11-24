/*
# -*- encoding: utf-8 -*-
##############################################################################
#
#    Samples module for Odoo 8 Backend Theme
#    Copyright (c) 2015 Antiun Ingeniería S.L. (http://www.antiun.com)
#       Endika Iglesias <endikaig@antiun.com>
#       Antonio Espinosa <antonioea@antiun.com>
#       Daniel Góme-Zurita <danielgz@antiun.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
*/


openerp.blue_backend_theme_v8 = function(instance, local) {
	var _t = instance.web._t;
	openerp_FieldMany2ManyTagsMultiSelection(instance);
	openerp_listview_html_widget(instance);
	web_listview_sticky(instance);
	
	// var wkhtmltopdf_state;

    // var trigger_download = function(session, response, c, action, options) {
        // session.get_file({
            // url: '/report/download',
            // data: {data: JSON.stringify(response)},
            // complete: openerp.web.unblockUI,
            // error: c.rpc_error.bind(c),
            // success: function(){
                // if (action && options && !action.dialog) {
                    // options.on_close();
                // }
            // },
        // });
    // };
// 	
	// instance.web.ActionManager.include({
		// ir_actions_report_xml: function(action, options) {
            // var self = this;
            // instance.web.blockUI();
            // action = _.clone(action);
            // _t =  instance.web._t;
// 
            // // QWeb reports
            // if ('report_type' in action && (action.report_type == 'qweb-html' || action.report_type == 'qweb-pdf' || action.report_type == 'controller')) {
                // var report_url = '';
                // switch (action.report_type) {
                    // case 'qweb-html':
                        // report_url = '/report/html/' + action.report_name;
                        // break;
                    // case 'qweb-pdf':
                        // report_url = '/report/pdf/' + action.report_name;
                        // break;
                    // case 'controller':
                        // report_url = action.report_file;
                        // break;
                    // default:
                        // report_url = '/report/html/' + action.report_name;
                        // break;
                // }
// 
                // // generic report: no query string
                // // particular: query string of action.data.form and context
                // if (!('data' in action) || !(action.data)) {
                    // if ('active_ids' in action.context) {
                        // report_url += "/" + action.context.active_ids.join(',');
                    // }
                // } else {
                    // report_url += "?options=" + encodeURIComponent(JSON.stringify(action.data));
                    // report_url += "&context=" + encodeURIComponent(JSON.stringify(action.context));
                // }
// 
                // var response = new Array();
                // response[0] = report_url;
                // response[1] = action.report_type;
                // var c = openerp.webclient.crashmanager;
// 
                // if (action.report_type == 'qweb-html') {
                    // window.open(report_url, '_blank', 'scrollbars=1,height=900,width=1280');
                    // instance.web.unblockUI();
                // } else if (action.report_type === 'qweb-pdf') {
                    // // Trigger the download of the pdf/controller report
                    // (wkhtmltopdf_state = wkhtmltopdf_state || openerp.session.rpc('/report/check_wkhtmltopdf')).then(function (presence) {
                        // // Fallback on html if wkhtmltopdf is not installed or if OpenERP is started with one worker
                        // if (presence === 'install') {
                            // self.do_notify(_t('Report'), _t('Unable to find Wkhtmltopdf on this \
// system. The report will be shown in html.<br><br><a href="http://wkhtmltopdf.org/" target="_blank">\
// wkhtmltopdf.org</a>'), true);
                            // report_url = report_url.substring(12)
                            // window.open('/report/html/' + report_url, '_blank', 'height=768,width=1024');
                            // instance.web.unblockUI();
                            // return;
                        // } else if (presence === 'workers') {
                            // self.do_notify(_t('Report'), _t('You need to start OpenERP with at least two \
// workers to print a pdf version of the reports.'), true);
                            // report_url = report_url.substring(12)
                            // window.open('/report/html/' + report_url, '_blank', 'height=768,width=1024');
                            // instance.web.unblockUI();
                            // return;
                        // } 
                        // return trigger_download(self.session, response, c, action, options);
                    // });
                // } else if (action.report_type === 'controller') {
                    // return trigger_download(self.session, response, c, action, options);
                // }                     
            // } else {
                // return self._super(action, options);
            // }
        // }
	// });
	
	var QWeb = instance.web.qweb;
	instance.web.Client.include({

		show_annoucement_bar : function() {
			return;
		},

		bind_events : function() {
			var self = this;
			this._super();

			var root = self.$el.parents();
			var elem_sm = $("<button id='leftbar_toggle' type='button' class='navbar-toggle left'><span class='icon-bar'></span><span class='icon-bar'></span></button>");
			elem_sm.prependTo(root.find('.navbar-header'));

			self.$el.on('click', '#leftbar_toggle', function() {
				var leftbar = root.find('.oe_leftbar');
				if (leftbar.css('display') == 'none') {
					leftbar.removeClass("hide");
					leftbar.addClass("show");
				} else {
					leftbar.removeClass("show");
					leftbar.addClass("hide");
				}
			});
		}
	});

	instance.web.Menu.include({
		reflow : function(behavior) {
			var self = this;
			var $more_container = this.$('#menu_more_container').hide();
			var $more = this.$('#menu_more');
			var $systray = this.$el.parents().find('.oe_systray');

			$more.children('li').insertBefore($more_container);
			// Pull all the items out of the more menu

			// 'all_outside' beahavior should display all the items, so hide the more menu and exit
			if (behavior === 'all_outside') {
				// Show list of menu items
				self.$el.show();
				this.$el.find('li').show();
				$more_container.hide();
				return;
			}

			// Hide all menu items
			var $toplevel_items = this.$el.find('li').not($more_container).not($systray.find('li')).hide();
			// Show list of menu items (which is empty for now since all menu items are hidden)
			self.$el.show();
			$toplevel_items.each(function() {
				var remaining_space = self.$el.parent().width() - $more_container.outerWidth() - 75;
				self.$el.parent().children(':visible').each(function() {
					remaining_space -= $(this).outerWidth();
				});

				if ($(this).width() >= remaining_space) {
					return false;
					// the current item will be appended in more_container
				}
				$(this).show();
				// show the current item in menu bar
			});
			$more.append($toplevel_items.filter(':hidden').show());
			$more_container.toggle(!!$more.children().length);
			// Hide toplevel item if there is only one
			var $toplevel = self.$el.children("li:visible");
			if ($toplevel.length === 1) {
				$toplevel.hide();
			}
		},

		open_menu : function(id) {
			var self = this;

			var root = self.$el.parents();
			var oe_main_menu_placeholder = root.find('#oe_main_menu_placeholder');

			if (oe_main_menu_placeholder.hasClass("in")) {
				oe_main_menu_placeholder.removeClass("in");
			}

			this._super(id);
		}
	});
};