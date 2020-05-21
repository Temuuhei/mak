openerp.hse.my_safety = function(instance) {
    var QWeb = instance.web.qweb;
    var _t = instance.web._t;
    instance.hse.my_safety = instance.web.form.FormWidget.extend(instance.web.form.ReinitializeWidgetMixin, {
        init: function() {
            $("head").append('<link rel="stylesheet" href="l10n_mn_dashboard/static/src/jqwidgets/jqwidgets/styles/jqx.base.css" type="text/css" />');
            $("head").append('<script type="text/javascript" src="l10n_mn_dashboard/static/src/jqwidgets/jqwidgets/jqxcore.js"></script>');
            $("head").append('<script type="text/javascript" src="l10n_mn_dashboard/static/src/jqwidgets/jqwidgets/jqxdata.js"></script>');
            $("head").append('<script type="text/javascript" src="l10n_mn_dashboard/static/src/jqwidgets/jqwidgets/jqxscrollbar.js"></script>');
            $("head").append('<script type="text/javascript" src="l10n_mn_dashboard/static/src/jqwidgets/jqwidgets/jqxbuttons.js"></script>');
            $("head").append('<script type="text/javascript" src="l10n_mn_dashboard/static/src/jqwidgets/jqwidgets/jqxdatatable.js"></script>');
            $("head").append('<script type="text/javascript" src="l10n_mn_dashboard/static/src/jqwidgets/scripts/demos.js"></script>');
            $("head").append('<script type="text/javascript" src="l10n_mn_dashboard/static/src/jqwidgets/jqwidgets/jqxdata.export.js"></script>');
            $("head").append('<script type="text/javascript" src="l10n_mn_dashboard/static/src/jqwidgets/jqwidgets/jqxchart.core.js"></script>');
            $("head").append('<script type="text/javascript" src="l10n_mn_dashboard/static/src/jqwidgets/jqwidgets/jqxdraw.js"></script>');
            $("head").append('<script type="text/javascript" src="l10n_mn_dashboard/static/src/jqwidgets/jqwidgets/jqxmenu.js"></script>');
            $("head").append('<script type="text/javascript" src="l10n_mn_dashboard/static/src/jqwidgets/jqwidgets/jqxlistbox.js"></script>');
            $("head").append('<script type="text/javascript" src="l10n_mn_dashboard/static/src/jqwidgets/jqwidgets/jqxdropdownlist.js"></script>');
            $("head").append('<script type="text/javascript" src="l10n_mn_dashboard/static/src/jqwidgets/jqwidgets/jqxgrid.js"></script>');
            $("head").append('<script type="text/javascript" src="l10n_mn_dashboard/static/src/jqwidgets/jqwidgets/jqxgrid.selection.js"></script>');
            $("head").append('<script type="text/javascript" src="l10n_mn_dashboard/static/src/jqwidgets/jqwidgets/jqxgrid.pager.js"></script>');
            $("head").append('<script type="text/javascript" src="l10n_mn_dashboard/static/src/jqwidgets/jqwidgets/jqxgrid.filter.js"></script>');
            $("head").append('<script type="text/javascript" src="l10n_mn_dashboard/static/src/jqwidgets/jqwidgets/jqxcheckbox.js"></script>');
            $("head").append('<script type="text/javascript" src="l10n_mn_dashboard/static/src/jqwidgets/jqwidgets/jqxgrid.columnsresize.js"></script>');
            $("head").append('<script type="text/javascript" src="l10n_mn_dashboard/static/src/jqwidgets/jqwidgets/jqxgrid.sort.js"></script>');
            
            this._super.apply(this, arguments);
            var self = this;
            this.set({
                start_date: false,
                end_date: false,
                employees: false,
            });
            this.updating = false;
            this.field_manager.on("field_changed:start_date", this, function() {
                this.set({"start_date": this.field_manager.get_field_value("start_date")});
            });
            this.field_manager.on("field_changed:end_date", this, function() {
                this.set({"end_date": this.field_manager.get_field_value("end_date")});
            });
            this.field_manager.on("field_changed:employee_ids", this, function() {
                this.set({"employees": this.field_manager.get_field_value("employee_ids")});
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
            self.on("change:start_date", self, self.initialize_content);
            self.on("change:end_date", self, self.initialize_content);
            self.on("change:employees", self, self.initialize_content);
        },
        
        initialize_content: function() {
            var self = this;
            this.destroy_content();
            var training_obj;
            var indicator_obj;
            var start_date = self.get('start_date');
            var end_date = self.get('end_date');
            var employees = self.get('employees')[0][2];
            return new instance.web.Model("hse.my.safety").call("get_training", [start_date, end_date,employees,new instance.web.CompoundContext()])
            .then(function(details) {
            	training_obj = details;
                return new instance.web.Model("hse.my.safety").call("get_indicator", [start_date, end_date,employees,new instance.web.CompoundContext()])
                .then(function(details) {
                    indicator_obj = details;
                });
                
            }).then(function(result) {
                self.training_obj = training_obj;
                self.indicator_obj = indicator_obj;
                self.display_data();
                
            });
        },
        destroy_content: function() {
            if (this.dfm) {
                this.dfm.destroy();
                this.dfm = undefined;
            }
        },
        get_table: function(obj, color){
            var data = obj;
            var source =
            {
                localData: data,
                dataType: "array"
            };
            var linkrenderer = function (index, datafield, value, defaultvalue, column, rowdata) {
                return "<div style='background-color:"+color+"; height:100%;'><a style='color: white;'>"+value+"</a></div>";
            } 
            var dataAdapter = new $.jqx.dataAdapter(source);
            var settings_datatable= {
                width: 420,
                // height: 150,
                source: dataAdapter,
                theme: 'ui-sunny',
                autorowheight: true,
                altrows: true,
                // aggregatesHeight: 70,
                // sortable: true,
                // pageable: true,
                autoheight: true,
                columnsResize: true,
                columns: [
                    {
                        text: _t('Training'), align: 'center', dataField: 'training_name', width:320, cellsrenderer:linkrenderer
                    },
                    {
                        text: _t('Date'), align: 'center', dataField: 'date', width:85, cellsrenderer:linkrenderer
                    },
                ],
                
            };            
            return settings_datatable;
        },
        get_bar: function(obj, title, displayText){
        	var sampleData = obj;
            console.log(obj);
            var toolTipCustomFormatFn = function (value, itemIndex, serie, group, categoryValue, categoryAxis) {
                return '<DIV style="text-align:left";><b>'+obj[itemIndex].name+'</b><br/><br/><br/> </DIV>';
            };
            var settings = {
                title: title,
                description: "",
                enableAnimations: true,
                showLegend: false,
                showBorderLine: false,
                enableCrosshairs: true,
                toolTipHideDelay: 15000,
                padding: { left: 5, top: 5, right: 5, bottom: 5 },
                titlePadding: { left: 10, top: 0, right: 0, bottom: 10 },
                source: sampleData,
                xAxis:
                    {
                        dataField: 'date',
                        gridLines: { visible: false },
                        valuesOnTicks: false,
                        labels: { visible: true,
                        angle:0,
                        
                        }, 
                    },
                valueAxis:
                {
                    unitInterval: 1,
                    labels: { horizontalAlignment: 'right' },
                    gridLines: { visible: false },
                    tickMarks: { color: '#BCBCBC' }
                },
                seriesGroups:
                    [
                        {
                            type: 'stackedarea',
                            toolTipFormatFunction: toolTipCustomFormatFn,
                            series: [
                                    { dataField: 'count', displayText: displayText , symbolType: 'circle',
                                        labels:{
                                        visible: true,
                                        backgroundColor: 'yellow',
                                        backgroundOpacity: 0.2,
                                        borderColor: '#7FC4EF',
                                        borderOpacity: 0.7,
                                        padding: { left: 5, right: 5, top: 0, bottom: 0 }
                                    }
                                    },
                                    
                                ]
                        }
                    ]
            };
            return settings;
        },
        display_data: function() {
            var self = this;
            self.$el.html(QWeb.render("hse.my_safety", {widget: self}));
            try {
                $('#hazard_report').jqxChart(self.get_bar(self.indicator_obj.hazard_report,_t('Hazard report'),_t('Hazard report')));
                $('#workplace_ispection').jqxChart(self.get_bar(self.indicator_obj.workplace_ispection,_t('Workplace ispection'),_t('workplace_ispection')));
                $('#safety_meeting').jqxChart(self.get_bar(self.indicator_obj.safety_meeting,_t('Safety meeting'),_t('Safety meeting')));
                $('#accident_entry').jqxChart(self.get_bar(self.indicator_obj.accident,_t('Accident/Incident'),_t('Accident/Incident')));
                $('#accident_entry').jqxChart('addColorScheme', 'customColorScheme', ['#E1372D']);
                $('#accident_entry').jqxChart({ colorScheme: 'customColorScheme' });
                $('#sitting_training').jqxGrid(self.get_table(self.training_obj.sitting_training,'green'));
                $('#stay_training').jqxGrid(self.get_table(self.training_obj.stay_training,'red'));
            }
            catch(err) {
                console.log(err.message);
            }
        },
    });
    instance.web.form.custom_widgets.add('hse_my_safety', 'instance.hse.my_safety');
}