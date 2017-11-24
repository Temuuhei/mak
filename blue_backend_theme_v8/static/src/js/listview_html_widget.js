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


openerp_listview_html_widget= function(instance) {
	var _t = instance.web._t;
	instance.web.list.columns.map['field.html'] = 'instance.web.list.HtmlColumn';

    instance.web.list.HtmlColumn = instance.web.list.Column.extend({
        _format: function (row_data, options) {
            return instance.web.format_value(
                row_data[this.id].value, this, options.value_if_empty);
        }
    });
};
