openerp.hse = function(instance) {
    openerp.hse.safety(instance);
    openerp.hse.daily(instance);
    openerp.hse.my_safety(instance);
    var QWeb = instance.web.qweb;
    var _t = instance.web._t;

    instance.hse.Accident = instance.web.form.FormWidget.extend(instance.web.form.ReinitializeWidgetMixin, {
        events: {
            "click .oe_hse_check td": "go_to",
            "change .oe_hse_factor_tr textarea": "go_to_go",
        },
        init: function() {
            this._super.apply(this, arguments);
            var self = this;
            this.set({
                accident_line: [],
                sheets_factor: [],
            });
            this.updating = false;
            this.field_manager.on("field_changed:accident_line", this, this.query_sheets);
            this.field_manager.on("field_changed:factor_line", this, this.query_sheets);
            this.res_o2m_drop = new instance.web.DropMisordered();
            this.render_drop = new instance.web.DropMisordered();
            this.description_line = _t("/");
            // Original save function is overwritten in order to wait all running deferreds to be done before actually applying the save.
            this.view.original_save = _.bind(this.view.save, this.view);
            this.view.save = function(prepend_on_create){
                self.prepend_on_create = prepend_on_create;
                return $.when.apply($, self.defs).then(function(){
                    return self.view.original_save(self.prepend_on_create);
                });
            };
        },
        go_to_go: function(event) {
            var str = event.target.id;
            var factor_line_id = parseInt(str.split("r")[1]);
            var ddd = new instance.web.Model("hse.injury.factor.line").call("write", [[factor_line_id], {'notes': String($(event.target).val()) } ]).then(function () {
            });
        },
        go_to: function(event) {
            if ($(event.target).data("id")){
                var line_id = JSON.parse($(event.target).data("id"));
                check_value = this.$('[data-id="'+line_id+'"]').prop('checked')
                if (check_value){
                    this.$('[data-label="'+line_id+'"]').css({'color': 'red',});
                }else
                {
                    this.$('[data-label="'+line_id+'"]').css({ 'color': 'black'});
                }
                var self = this;
                document.getElementById("factor_immediate_cause").innerHTML="";
                document.getElementById("factor_base_cause").innerHTML="";
                var im_cause_str = '';
                var ba_cause_str = '';
                var ddd = new instance.web.Model("hse.injury.accident.line").call("write", [[line_id], {'check': check_value}]).then(function () {
                        var sss = new instance.web.Model("hse.injury.factor.line").call("search", [[["injury_id", "=", self.get('accident_line')[0].injury_id[0]], ]])
                            .then(function(ids) {
                                var rrr = new instance.web.Model("hse.injury.factor.line").call("read", [ids,[]]).then(function(details){
                                    var row_cnt = details.length;
                                    for (var j=0; j<row_cnt; j++){
                                        if (details[j].type == 'immediate_cause'){
                                            if(details[j].state == 'draft'){
                                                im_cause_str += '<tr><td style="font-size: 16px; font-weight: bold;">'+details[j].factor_id[1]+'</td><td class="oe_hse_factor_tr" ><textarea id=factor'+details[j].id+'>'+details[j].notes+' </textarea></td></tr>';
                                        
                                            }else{
                                                im_cause_str += '<tr><td style="font-size: 16px; font-weight: bold;">'+details[j].factor_id[1]+'</td><td class="oe_hse_factor_tr" ><textarea id=factor'+details[j].id+' readonly>'+details[j].notes+' </textarea></td></tr>';
                                            }
                                        }else{
                                            if(details[j].state == 'draft'){
                                                ba_cause_str += '<tr><td style="font-size: 16px; font-weight: bold;">'+details[j].factor_id[1]+'</td><td class="oe_hse_factor_tr" ><textarea id=factor'+details[j].id+'>'+details[j].notes+' </textarea></td></tr>';
                                        
                                            }else{
                                                ba_cause_str += '<tr><td style="font-size: 16px; font-weight: bold;">'+details[j].factor_id[1]+'</td><td class="oe_hse_factor_tr" ><textarea id=factor'+details[j].id+' readonly>'+details[j].notes+' </textarea></td></tr>';
                                            }
                                        }
                                    }
                                    document.getElementById("factor_immediate_cause").innerHTML=im_cause_str;
                                    document.getElementById("factor_base_cause").innerHTML=ba_cause_str;
                                });                                
                            });
                    });    
            }   
        },
        query_sheets: function() {
            var self = this;
            var commands = this.field_manager.get_field_value("accident_line");
            var commands2 = this.field_manager.get_field_value("factor_line");
            this.res_o2m_drop.add(new instance.web.Model(this.view.model).call("resolve_2many_commands", ["factor_line", commands2, [], 
                        new instance.web.CompoundContext()]))
                    .done(function(res) {
                    self.querying_factor = true;
                    self.set({sheets_factor: res});
                    self.querying_factor = false;
                });

            this.res_o2m_drop.add(new instance.web.Model(this.view.model).call("resolve_2many_commands", ["accident_line", commands, [], 
                    new instance.web.CompoundContext()]))
                .done(function(result) {
                self.querying = true;
                self.set({accident_line: result});
                self.querying = false;
            });
        },
        initialize_field: function() {
            instance.web.form.ReinitializeWidgetMixin.initialize_field.call(this);
            var self = this;
            self.on("change:accident_line", self, self.initialize_content);
            self.on("change:sheets_factor", self, self.initialize_content);
        },
        
        initialize_content: function() {
            var self = this;
            this.destroy_content();
            var lines;
            var factors;
            self.lines = self.get('accident_line');
            self.factors = self.get('sheets_factor');
            self.display_data();
        },
        destroy_content: function() {
            if (this.dfm) {
                this.dfm.destroy();
                this.dfm = undefined;
            }
        },
        display_data: function() {
            var self = this;
            self.$el.html(QWeb.render("hse.Accident", {widget: self}));
            if (self.get('accident_line')[0] !=undefined){
                document.getElementById("factor_immediate_cause").innerHTML="";
                var insert_str='';
                var sss = new instance.web.Model("hse.injury.factor.line").call("search", [[["injury_id", "=", self.get('accident_line')[0].injury_id[0]], ]])
                .then(function(ids) {
                    var rrr = new instance.web.Model("hse.injury.factor.line").call("read", [ids,[]]).then(function(details){
                        var row_cnt = details.length;
                        var im_cause_str = '';
                        var ba_cause_str = '';
                        for (var j=0; j<row_cnt; j++){
                            if (details[j].type == 'immediate_cause'){
                                if(details[j].state == 'draft'){
                                    im_cause_str += '<tr><td style="font-size: 16px; font-weight: bold;">'+details[j].factor_id[1]+'</td><td class="oe_hse_factor_tr" ><textarea id=factor'+details[j].id+'>'+details[j].notes+' </textarea></td></tr>';
                            
                                }else{
                                    im_cause_str += '<tr><td style="font-size: 16px; font-weight: bold;">'+details[j].factor_id[1]+'</td><td class="oe_hse_factor_tr" ><textarea id=factor'+details[j].id+' readonly>'+details[j].notes+' </textarea></td></tr>';
                                }
                            }else{
                                if(details[j].state == 'draft'){
                                    ba_cause_str += '<tr><td style="font-size: 16px; font-weight: bold;">'+details[j].factor_id[1]+'</td><td class="oe_hse_factor_tr" ><textarea id=factor'+details[j].id+'>'+details[j].notes+' </textarea></td></tr>';
                            
                                }else{
                                    ba_cause_str += '<tr><td style="font-size: 16px; font-weight: bold;">'+details[j].factor_id[1]+'</td><td class="oe_hse_factor_tr" ><textarea id=factor'+details[j].id+' readonly>'+details[j].notes+' </textarea></td></tr>';
                                }
                            }
                        }
                        document.getElementById("factor_immediate_cause").innerHTML=im_cause_str;
                        document.getElementById("factor_base_cause").innerHTML=ba_cause_str;
                    });                                
                });
            }
            
        },
    });
    
    instance.web.form.custom_widgets.add('hse_accident', 'instance.hse.Accident');


    
    // #################################### CORRECTIVE ACTIONS ##########################################
    
    instance.hse.corrective_actions = instance.web.form.FormWidget.extend(instance.web.form.ReinitializeWidgetMixin, {
        events: {
            "click .oe_mno_dash_see_hse": "go_to",
        },
        
        init: function() {
            $("head").append('<link rel="stylesheet" href="l10n_mn_dashboard/static/src/jqwidgets/jqwidgets/styles/jqx.base.css" type="text/css" />');
            $("head").append('<script type="text/javascript" src="l10n_mn_dashboard/static/src/jqwidgets/jqwidgets/jqxcore.js"></script>');
            $("head").append('<script type="text/javascript" src="l10n_mn_dashboard/static/src/jqwidgets/jqwidgets/jqxdata.js"></script>');
            // Grid
            $("head").append('<script type="text/javascript" src="l10n_mn_dashboard/static/src/jqwidgets/jqwidgets/jqxscrollbar.js"></script>');
            $("head").append('<script type="text/javascript" src="l10n_mn_dashboard/static/src/jqwidgets/jqwidgets/jqxbuttons.js"></script>');
            
            $("head").append('<script type="text/javascript" src="l10n_mn_dashboard/static/src/jqwidgets/jqwidgets/jqxdatatable.js"></script>');
            $("head").append('<script type="text/javascript" src="l10n_mn_dashboard/static/src/jqwidgets/scripts/demos.js"></script>');
            $("head").append('<script type="text/javascript" src="l10n_mn_dashboard/static/src/jqwidgets/jqwidgets/jqxdata.export.js"></script>');

            $("head").append('<script type="text/javascript" src="l10n_mn_dashboard/static/src/jqwidgets/jqwidgets/jqxchart.core.js"></script>');
            $("head").append('<script type="text/javascript" src="l10n_mn_dashboard/static/src/jqwidgets/jqwidgets/jqxdraw.js"></script>');
            
            $("head").append('<script type="text/javascript" src="l10n_mn_dashboard/static/src/jqwidgets/jqwidgets/jqxtooltip.js"></script>');
            $("head").append('<script type="text/javascript" src="l10n_mn_dashboard/static/src/jqwidgets/jqwidgets/jqxbulletchart.js"></script>');
            $("head").append('<script type="text/javascript" src="l10n_mn_dashboard/static/src/jqwidgets/jqwidgets/jqxgauge.js"></script>');
            

            this._super.apply(this, arguments);
            var self = this;
            this.set({
                projects: false,
                start_date: false,
                end_date: false,
            });
            this.updating = false;
            this.field_manager.on("field_changed:start_date", this, function() {
                this.set({"start_date": this.field_manager.get_field_value("start_date")});
            });
            this.field_manager.on("field_changed:end_date", this, function() {
                this.set({"end_date": this.field_manager.get_field_value("end_date")});
            });
            this.field_manager.on("field_changed:project_ids", this, function() {
                this.set({"projects": this.field_manager.get_field_value("project_ids")});
            });
            
            this.res_o2m_drop = new instance.web.DropMisordered();
            this.render_drop = new instance.web.DropMisordered();
            this.description_line = _t("/");
            // Original save function is overwritten in order to wait all running deferreds to be done before actually applying the save.
            this.view.original_save = _.bind(this.view.save, this.view);
            this.view.save = function(prepend_on_create){
                self.prepend_on_create = prepend_on_create;
                return $.when.apply($, self.defs).then(function(){
                    return self.view.original_save(self.prepend_on_create);
                });
            };
        },
        
        
        initialize_field: function() {
            instance.web.form.ReinitializeWidgetMixin.initialize_field.call(this);
            var self = this;
            self.on("change:projects", self, self.initialize_content);
            self.on("change:start_date", self, self.initialize_content);
            self.on("change:end_date", self, self.initialize_content);
        },
        
        initialize_content: function() {
            var self = this;
            this.destroy_content();
            var projects;
            var all_details;
            projects = self.get('projects')[0][2];
            var set_date_from = self.get('start_date');
            var set_date_to = self.get('end_date');
            return new instance.web.Model("hse.corrective.actions").call("get_all", [set_date_from,set_date_to,projects,new instance.web.CompoundContext()])
            .then(function(details) {
                all_details = details;

            }).then(function(result) {
                self.all_details = all_details;
                self.display_data();
            });
    
        },
        get_datatable: function(res){
            var data = res;
            var source =
            {
                localData: data,
                dataType: "array"
            };
            var linkrenderer = function (index, datafield, value, defaultvalue, column, rowdata) {
                
                if (data[index].uzuulelt==_t('Hazard report')){
                    return data[index].atag+"style='color: #ff5c25;'>"+value+"</a>";
                }
                if (data[index].uzuulelt==_t('Workplace ispection')){
                    return data[index].atag+"style='color: #0c4194;'>"+value+"</a>";
                }
                if (data[index].uzuulelt==_t('Accident/Incident')){
                    return data[index].atag+"style='color: #dc2e58;'>"+value+"</a>";
                }

                return data[index].atag+">"+value+"</a>";
            } 
            var dataAdapter = new $.jqx.dataAdapter(source);
            var settings_datatable= {
                width: 1050,
                // height: 120,
                source: dataAdapter,
                theme: 'ui-sunny',
                // aggregatesHeight: 70,
                sortable: true,
                // pageable: true,
                columnsResize: true,
                columns: [
                    {
                        text: _t('Indicators'), align: 'center', dataField: 'uzuulelt', width:140, cellsrenderer:linkrenderer
                    },
                    {
                        text: _t('Number'), align: 'center', dataField: 'number', width:110, cellsrenderer:linkrenderer
                    },
                    {
                        text: _t('Date'), align: 'center', dataField: 'date', width:80, cellsrenderer:linkrenderer
                    },
                    {
                        text: _t('Corrective action what'), align: 'center', dataField: 'corrective_action', width:230, cellsrenderer:linkrenderer
                    }, 
                    {
                        text: _t('Corrective action'), align: 'center', dataField: 'corrective_be_action', width:230, cellsrenderer:linkrenderer
                    }, 
                    {
                        text: _t('Date to take remedial action'), align: 'center', dataField: 'when', width:90, cellsrenderer:linkrenderer
                    },
                    {
                        text: _t('Responsible'), align: 'center', dataField: 'responsible', width:90, cellsrenderer:linkrenderer
                    }, 
                    {
                        text: _t('Project'), align: 'center', dataField: 'project', width:80, cellsrenderer:linkrenderer
                    },                
                ],
                
            };            
            return settings_datatable;
        },
        get_lineargauge: function(){
            settings = {
                orientation: 'vertical',
                height: 250,
                ticksMajor: { size: '10%', interval: 10 },
                ticksMinor: { size: '10%', interval: 5, style: { 'stroke-width': 1, stroke: '#aaaaaa'} },
                max: 100,
                min:0,
                pointer: { size: '6%' },
                colorScheme: 'scheme05',
                labels: { interval: 10, position: 'far' , formatValue: function (value, position) {
                    if (position === 'far') {
                        return value + '%';
                    }
                }},
                ranges: [
                { startValue: 0, endValue: 40, style: { fill: 'red', stroke: 'red'} , endWidth: 5, startWidth: 1},
                { startValue: 40, endValue: 80, style: { fill: 'orange', stroke: 'orange'} , endWidth: 10, startWidth: 5},
                { startValue: 80, endValue: 100, style: { fill: 'green', stroke: 'green'}, endWidth: 15, startWidth: 10}],
                animationDuration: 1500,
                // showTooltip: true
            }
            return settings;
        },
        get_donut: function(done, not_done){
            data =[
                {Repaire:  _t('Repaired'), Count: done },
                {Repaire:  _t('Non repair'), Count: not_done, },
            ];
            var settings = {
                title: '',
                description: "",
                enableAnimations: true,
                showLegend: true,
                showBorderLine: true,
                legendPosition: { left: 520, top: 140, width: 100, height: 100 },
                padding: { left: 5, top: 5, right: 5, bottom: 5 },
                titlePadding: { left: 0, top: 0, right: 0, bottom: 10 },
                source: data,
                colorScheme: 'scheme02',
                seriesGroups:
                    [
                        {
                            type: 'pie',
                            showLabels: true,
                            series:
                                [
                                    {
                                        dataField: 'Count',
                                        displayText: 'Repaire',
                                        labelRadius: 80,
                                        initialAngle: 150,
                                        radius: 100,
                                        // innerRadius: 40,
                                        centerOffset: 0,
                                        formatFunction: function (value) {
                                            return value;
                                        },
                                    }
                                ]
                        }
                    ]
            };
            return settings;
        },
        destroy_content: function() {
            if (this.dfm) {
                this.dfm.destroy();
                this.dfm = undefined;
            }

        },
        display_data: function() {
            var self = this;
            self.$el.html(QWeb.render("hse.corrective_actions", {widget: self}));
            var date_from = self.get('date_from');
            var date_to = self.get('date_to');
            
            try {
                $('#linearGauge').jqxLinearGauge(self.get_lineargauge());
                var val = 100*self.all_details.done/(self.all_details.done+self.all_details.not_done)
                $('#linearGauge').jqxLinearGauge('value', val);

                $('#hazard_report').jqxChart(self.get_donut(self.all_details.hazard_done,self.all_details.hazard_not_done));
                $('#hazard_report').jqxChart('addColorScheme', 'customColorScheme', ['#2d7b29', '#dc2e58']);
                $('#hazard_report').jqxChart({ colorScheme: 'customColorScheme' });

                $('#workplace_ispection').jqxChart(self.get_donut(self.all_details.workplace_done,self.all_details.workplace_not_done));
                $('#workplace_ispection').jqxChart('addColorScheme', 'customColorScheme', ['#2d7b29', '#dc2e58']);
                $('#workplace_ispection').jqxChart({ colorScheme: 'customColorScheme' });

                $('#injury_entry').jqxChart(self.get_donut(self.all_details.injury_done,self.all_details.injury_not_done));
                $('#injury_entry').jqxChart('addColorScheme', 'customColorScheme', ['#2d7b29', '#dc2e58']);
                $('#injury_entry').jqxChart({ colorScheme: 'customColorScheme' });
                $('#hazard').jqxDataTable(self.get_datatable(self.all_details.result));
            }
            catch(err) {
                console.log(err.message);
            }
        },
    });
    instance.web.form.custom_widgets.add('hse_corrective_actions', 'instance.hse.corrective_actions');



    // #################################### INJURY IMAGE ##########################################
    instance.hse.injury_image = instance.web.form.FormWidget.extend(instance.web.form.ReinitializeWidgetMixin, {
        events: {
        },
        init: function() {
            this._super.apply(this, arguments);
            var self = this;
            this.set({
                attach_image: false,
            });
            this.updating = false;
            this.field_manager.on("field_changed:attachment_ids", this, function() {
                this.set({"attach_image": this.field_manager.get_field_value("attachment_ids")});
            });
        },
        initialize_field: function() {
            instance.web.form.ReinitializeWidgetMixin.initialize_field.call(this);
            var self = this;
            self.on("change:attach_image", self, self.initialize_content);
        },
        
        initialize_content: function() {
            var self = this;
            this.destroy_content();
            var attach_ids = []
            if (self.get('attach_image')){
                attach_ids = self.get('attach_image')[0][2];
                return  new instance.web.Model('ir.attachment').call('search', [[['id', 'in', attach_ids],['index_content','=','image'] ]])
                .then(function(ids){
                        self.attach_ids = ids;
                        self.display_data();
                });
            }
        },
        destroy_content: function() {
            if (this.dfm) {
                this.dfm.destroy();
                this.dfm = undefined;
            }
        },
        display_data: function() {
            var self = this;
            self.$el.html(QWeb.render("hse.injury_image", {widget: self}));
            var html = '';
            for (var i=0; i<self.attach_ids.length; i++){
                url = instance.session.url('/web/binary/image', {model: 'ir.attachment', field: 'datas', filename_field:'datas_fname', id: self.attach_ids[i]});
                html += '<tr><td style="text-align: center; vertical-align: middle; border: 1px solid black; width: 400px"><img style="width: inherit" src="'+url+'"/></td>'
                i++;
                if (self.attach_ids[i]){
                    url = instance.session.url('/web/binary/image', {model: 'ir.attachment', field: 'datas', filename_field:'datas_fname', id: self.attach_ids[i]});
                    html += '<td style="text-align: center; vertical-align: middle; border: 1px solid black; width: 400px"><img style="width: inherit" src="'+url+'"/></td>'
                }

                html += '</tr>'
            }
            document.getElementById("image_table").innerHTML = html;
        },
    });
    
    instance.web.form.custom_widgets.add('hse_injury_image', 'instance.hse.injury_image');

    // #################################### COR ACT INJURY IMAGE ##########################################
    instance.hse.cor_act_injury_image = instance.web.form.FormWidget.extend(instance.web.form.ReinitializeWidgetMixin, {
        events: {
        },
        init: function() {
            this._super.apply(this, arguments);
            var self = this;
            this.set({
                attach_image: false,
            });
            this.updating = false;
            this.field_manager.on("field_changed:cor_act_attach_ids", this, function() {
                this.set({"attach_image": this.field_manager.get_field_value("cor_act_attach_ids")});
            });
        },
        initialize_field: function() {
            instance.web.form.ReinitializeWidgetMixin.initialize_field.call(this);
            var self = this;
            self.on("change:attach_image", self, self.initialize_content);
        },
        
        initialize_content: function() {
            var self = this;
            this.destroy_content();
            var attach_ids = []
            if (self.get('attach_image')){
                attach_ids = self.get('attach_image')[0][2];
                return  new instance.web.Model('ir.attachment').call('search', [[['id', 'in', attach_ids],['index_content','=','image'] ]])
                .then(function(ids){
                        self.attach_ids = ids;
                        self.display_data();
                });
            }
        },
        destroy_content: function() {
            if (this.dfm) {
                this.dfm.destroy();
                this.dfm = undefined;
            }
        },
        display_data: function() {
            var self = this;
            self.$el.html(QWeb.render("hse.cor_act_injury_image", {widget: self}));
            var html = '';
            for (var i=0; i<self.attach_ids.length; i++){
                url = instance.session.url('/web/binary/image', {model: 'ir.attachment', field: 'datas', filename_field:'datas_fname', id: self.attach_ids[i]});
                html += '<tr><td style="text-align: center; vertical-align: middle; border: 1px solid black; width: 400px"><img style="width: inherit" src="'+url+'"/></td>'
                i++;
                if (self.attach_ids[i]){
                    url = instance.session.url('/web/binary/image', {model: 'ir.attachment', field: 'datas', filename_field:'datas_fname', id: self.attach_ids[i]});
                    html += '<td style="text-align: center; vertical-align: middle; border: 1px solid black; width: 400px"><img style="width: inherit" src="'+url+'"/></td>'
                }

                html += '</tr>'
            }
            document.getElementById("cor_act_image_table").innerHTML = html;
        },
    });
    
    instance.web.form.custom_widgets.add('hse_cor_act_injury_image', 'instance.hse.cor_act_injury_image');

    // #################################### DESC INJURY IMAGE ##########################################
    instance.hse.desc_injury_image = instance.web.form.FormWidget.extend(instance.web.form.ReinitializeWidgetMixin, {
        events: {
        },
        init: function() {
            this._super.apply(this, arguments);
            var self = this;
            this.set({
                attach_image: false,
            });
            this.updating = false;
            this.field_manager.on("field_changed:desc_attach_ids", this, function() {
                this.set({"attach_image": this.field_manager.get_field_value("desc_attach_ids")});
            });
        },
        initialize_field: function() {
            instance.web.form.ReinitializeWidgetMixin.initialize_field.call(this);
            var self = this;
            self.on("change:attach_image", self, self.initialize_content);
        },
        
        initialize_content: function() {
            var self = this;
            this.destroy_content();
            var attach_ids = []
            if (self.get('attach_image')){
                attach_ids = self.get('attach_image')[0][2];
                return  new instance.web.Model('ir.attachment').call('search', [[['id', 'in', attach_ids],['index_content','=','image'] ]])
                .then(function(ids){
                        self.attach_ids = ids;
                        self.display_data();
                });
            }
        },
        destroy_content: function() {
            if (this.dfm) {
                this.dfm.destroy();
                this.dfm = undefined;
            }
        },
        display_data: function() {
            var self = this;
            self.$el.html(QWeb.render("hse.desc_injury_image", {widget: self}));
            var html = '';
            for (var i=0; i<self.attach_ids.length; i++){
                url = instance.session.url('/web/binary/image', {model: 'ir.attachment', field: 'datas', filename_field:'datas_fname', id: self.attach_ids[i]});
                html += '<tr><td style="text-align: center; vertical-align: middle; border: 1px solid black; width: 400px"><img style="width: inherit" src="'+url+'"/></td>'
                i++;
                if (self.attach_ids[i]){
                    url = instance.session.url('/web/binary/image', {model: 'ir.attachment', field: 'datas', filename_field:'datas_fname', id: self.attach_ids[i]});
                    html += '<td style="text-align: center; vertical-align: middle; border: 1px solid black; width: 400px"><img style="width: inherit" src="'+url+'"/></td>'
                }

                html += '</tr>'
            }
            document.getElementById("desc_image_table").innerHTML = html;
        },
    });
    
    instance.web.form.custom_widgets.add('hse_desc_injury_image', 'instance.hse.desc_injury_image');
};
