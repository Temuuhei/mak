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


openerp_FieldMany2ManyTagsMultiSelection = function(instance) {

	var _t = instance.web._t;

	instance.web.form.CompletionFieldMixin._search_create_popup = function(view, ids, context) {
		var self = this;
		var pop = new instance.web.form.SelectCreatePopup(this);
		var domain = self.build_domain();

		if (self.field.type == 'many2many') {
			var selected_ids = self.get_search_blacklist();
			if (selected_ids.length > 0) {
				domain = new instance.web.CompoundDomain(domain, ["!", ["id", "in", selected_ids]]);
			}
		}

		pop.select_element(self.field.relation, {
			title : (view === 'search' ? _t("Search: ") : _t("Create: ")) + this.string,
			initial_ids : ids ? _.map(ids, function(x) {
				return x[0];
			}) : undefined,
			initial_view : view,
			disable_multiple_selection : this.field.type != 'many2many',
		}, domain, new instance.web.CompoundContext(self.build_context(), context || {}));
		pop.on("elements_selected", self, function(element_ids) {
			for (var i = 0,
			    len = element_ids.length; i < len; i++) {
				self.add_id(element_ids[i]);
				if (self.field.type != 'many2many') {
					break;
				}
			}
			self.focus();
		});
	};
};
