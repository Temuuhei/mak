
	var QWeb = instance.web.qweb;
	var _t = instance.web._t;



odoo.define('mak_it_helpdesk.form_widgets', function (require) {
    "use strict";

    var core = require('web.core');
    var FieldSelection = core.form_widget_registry.get('selection');

    var ItHelpdeskJobSelection = FieldSelection.extend({
        events: _.defaults({
            'focus select': 'onFocus'
        }, FieldSelection.prototype.events),
        onFocus: function () {
            if (
                this.field_manager.fields.name_field_1.get_value() == 'email' &&
                this.field_manager.fields.name_field_2.get_value() == 'spark'
            ) {
                this.$el.find('option').hide();
            }
        }
    });
    core.form_widget_registry.add('it_helpdesk_job_selection', ItHelpdeskJobSelection);
});
