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


web_listview_sticky = function (instance) {
    var _t = instance.web._t,
        _lt = instance.web._lt;
    var QWeb = instance.web.qweb;

    //Sticky Table Header
    instance.web.ListView.include({
        load_list: function () {
            var self = this;
            self._super.apply(this, arguments);
            var one2many_length = self.$el.parents('.oe_form_field.oe_form_field_one2many').length;
            var scrollArea = self.$el.parents('.oe_view_manager.oe_view_manager_current').find('.oe_view_manager_wrapper .oe_view_manager_body')[0];
            if(scrollArea &&  one2many_length == 0){
                self.$el.find('table.oe_list_content').each(function(){
                    $(this).stickyTableHeaders({scrollableArea: scrollArea});
                });
            }
        },
    });
};