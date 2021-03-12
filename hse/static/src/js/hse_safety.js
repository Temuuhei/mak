openerp.hse.safety = function(instance) {
    var QWeb = instance.web.qweb;
    var _t = instance.web._t;
    // #################################### SAFETY REPORT ##########################################
    instance.hse.safety_report = instance.web.form.FormWidget.extend(instance.web.form.ReinitializeWidgetMixin, {
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
            this._super.apply(this, arguments);
            var self = this;
            this.set({
                start_date: false,
                end_date: false,
                projects: false,
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
            self.on("change:start_date", self, self.initialize_content);
            self.on("change:end_date", self, self.initialize_content);
            self.on("change:projects", self, self.initialize_content);
        },
        
        initialize_content: function() {
            var self = this;
            this.destroy_content();
            var main_obj;
            var rate_obj;
            var bird_pyramid_obj;
            var indicator_obj;
            var start_date = self.get('start_date');
            var end_date = self.get('end_date');
            var projects = self.get('projects')[0][2];
            var plan_actual_obj;
            return new instance.web.Model("hse.safety.report").call("get_man_hour", [start_date, end_date,projects,new instance.web.CompoundContext()])
            .then(function(details) {
                main_obj = details;
                return new instance.web.Model("hse.safety.report").call("get_rate", [start_date, end_date,projects,new instance.web.CompoundContext()])
                .then(function(details) {
                    rate_obj = details;
                    return new instance.web.Model("hse.safety.report").call("get_bird_pyramid", [end_date,projects,new instance.web.CompoundContext()])
                    .then(function(details) {
                        bird_pyramid_obj = details;
                        return new instance.web.Model("hse.safety.report").call("get_indicator", [start_date, end_date,projects,new instance.web.CompoundContext()])
                        .then(function(details) {
                            indicator_obj = details;
                            return new instance.web.Model("hse.safety.report").call("get_reclamation", [start_date, end_date,projects,new instance.web.CompoundContext()])
                            .then(function(details) {
                                plan_actual_obj = details;
                            });
                        }); 
                    });    
                });
            }).then(function(result) {
                self.main_obj = main_obj;
                self.rate_obj = rate_obj;
                self.plan_actual_obj = plan_actual_obj;
                self.bird_pyramid_obj = bird_pyramid_obj;
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
        get_safe_day: function(){
            self = this;
            series = [];
            for (var i=0; i<self.main_obj.man_hour.length; i++){
                series.push({dataField: self.main_obj.man_hour[i].project_name, displayText: self.main_obj.man_hour[i].project_name})
            }
            var sampleData = self.main_obj.survaljit;
            console.log(self.main_obj.survaljit);
            var toolTipCustomFormatFn = function (value, itemIndex, serie, group, categoryValue, categoryAxis) {
                return '<DIV style="text-align:left; height:100%;"><b>'+self.main_obj.survaljit[itemIndex][serie.dataField+'p']+'</b><br/><br/> </DIV>';
            };
            var safe_day = self.main_obj.all_day - self.main_obj.safe_day
            var settings = {
                title: _t("Total")+" << "+self.main_obj.all_day+" >> "+_t("days")+" << "+safe_day+" >> "+_t("days safe production"),
                description: "",
                enableAnimations: true,
                showLegend: true,
                showBorderLine: false,
                showToolTips: true,
                toolTipHideDelay: 15000,
                padding: { left: 5, top: 5, right: 5, bottom: 5 },
                titlePadding: { left: 0, top: 0, right: 0, bottom: 0 },
                source: sampleData,
                xAxis:
                    {
                        dataField: 'Үзүүлэлт',
                        unitInterval: 1,
                        axisSize: 'auto',
                        tickMarks: {
                            visible: true,
                            interval: 1,
                            color: '#BCBCBC'
                        },
                        gridLines: {
                            visible: false,
                            interval: 1,
                            color: '#BCBCBC'
                        }
                    },
                valueAxis:
                {
                    unitInterval: 1,
                    minValue: 0,
                    labels: { visible: true },
                    tickMarks: { color: '#BCBCBC' }
                },
                colorScheme: 'scheme02',
                seriesGroups:
                    [
                        {
                            type: 'stackedcolumn',
                            toolTipFormatFunction: toolTipCustomFormatFn,
                            
                            columnsGapPercent: 50,
                            seriesGapPercent: 0,
                            series: series
                        }
                    ]
            };
            return settings;
        },
        get_donut: function(title, obj){
            self = this;
            data = self.main_obj.man_hour
            series = [
                    {
                        dataField: obj,
                        displayText: 'project_name',
                        labelRadius: 80,
                        initialAngle: 0,
                        radius: 70,
                        innerRadius: 40,
                        centerOffset: 0,
                        formatFunction: function (value) {
                            if (isNaN(value))
                                return value;
                            return $.jqx.dataFormat.formatnumber(value, 'f');
                        },
                       
                    }
                ]
            var settings = {
                title: title,
                description: "",
                enableAnimations: true,
                
                showBorderLine: false,
                showToolTips: false,
                
                titlePadding: { left: 0, top: 0, right: 0, bottom: 0 },
                source: data,
                colorScheme: 'scheme02',
                seriesGroups:
                    [
                        {
                            type: 'donut',
                            showLabels: true,
                            series: series
                        }
                    ]
            };
            var valueText = 0;
            if (obj=='ytd'){
                    settings['showLegend']=false;
                    // settings['legendLayout']={ left: 330, top: 30, width: 90, height: 150, flow: 'vertical' };
                    settings['padding']={ left: 5, top: 5, right: 5, bottom: 5 };
                }
                else{
                    settings['showLegend']=true
                    settings['legendLayout']={ left: 330, top: 30, width: 90, height: 150, flow: 'vertical' };
                    settings['padding']={ left: 5, top: 5, right: 150, bottom: 5 };
                }
            for (var i=0; i<data.length; i++){
                if (obj=='ytd'){
                    valueText+=data[i].ytd
                }
                else{
                    valueText+=data[i].mtd
                }
            }
            rect_x = 140

            if (valueText.toString().length<6){
                rect_x +=0
            }
            settings.drawBefore = function (renderer, rect) {
                sz = renderer.measureText(valueText, 0, { 'class': 'chart-inner-text' });
                renderer.text(
                $.jqx.dataFormat.formatnumber(valueText, 'f'),
                rect.x +rect_x,
                rect.y + rect.height / 2,
                0,
                0,
                0,
                { 'class': 'chart-inner-text' }
                );
            }
            return settings;
        },
        get_rate: function(obj, title, displayText, maxValue){
            var sampleData = [];
            for (var i=0; i<obj.length; i++){
                sampleData.push({ Year: obj[i].year, frequency: obj[i].frequency, ir: obj[i].ir, plan: obj[i].plan, man_hour: obj[i].man_hour })
            }
            
            var latencyThreshold = 35;
            var settings = {
                title: title,
                description: title+" = ("+displayText+"*200,000) / "+_t("Man hour"),
                enableAnimations: true,
                showLegend: true,
                showBorderLine: false,
                showToolTips: false,
                padding: { left: 5, top: 5, right: 5, bottom: 5 },
                titlePadding: { left: 5, top: 0, right: 0, bottom: 5 },
                source: sampleData,
                xAxis: {
                    dataField: 'Year',
                    // unitInterval: 1,
                    gridLines: { visible: false },
                    valuesOnTicks: false,
                    padding: { bottom: 10 }
                },
                seriesGroups:
                    [
                        {
                            type: 'line',
                            valueAxis:
                            {
                                visible: true,
                                position: 'right',
                                unitInterval: 500000,
                                // minValue: 0,
                                title: { text: _t("Man hour") },
                                gridLines: { visible: false },
                                labels: { horizontalAlignment: 'left' }
                            },
                            series: [
                                    { dataField: 'man_hour', displayText: _t("Man hour") , opacity: 1.0, lineWidth: 2, dashStyle: '2,2'}
                                ],
                        },
                        {
                            type: 'line',
                            valueAxis:
                            {
                                visible: true,
                                minValue: 0,
                                maxValue: maxValue+1,
                                title: { text: displayText },
                                gridLines: { visible: false },
                            },
                            series: [
                                { dataField: 'plan', displayText: _t("Tolerable") , symbolType: 'circle',
                                    formatFunction: function (value,itemIndex) {if (value>0)return value;},
                                    
                                    labels:{
                                        visible: true,
                                        backgroundColor: 'yellow',
                                        backgroundOpacity: 0.2,
                                        borderColor: '#7FC4EF',
                                        borderOpacity: 0.7,
                                        padding: { left: 5, right: 5, top: 0, bottom: 0 }
                                    }
                                },
                                { dataField: 'frequency', displayText: displayText, symbolType: 'circle',
                                    formatFunction: function (value,itemIndex) {if (value>0)return value;},

                                    labels:{
                                        visible: true,
                                        backgroundColor: 'yellow',
                                        backgroundOpacity: 0.2,
                                        borderColor: '#7FC4EF',
                                        borderOpacity: 0.7,
                                        padding: { left: 5, right: 5, top: 0, bottom: 0 }
                                    }
                                },
                                { dataField: 'ir', displayText: title , symbolType: 'square',
                                    formatFunction: function (value,itemIndex) {if (value>0)return value;},
                                    labels:{
                                        visible: true,
                                        backgroundColor: 'yellow',
                                        backgroundOpacity: 0.2,
                                        borderColor: '#7FC4EF',
                                        borderOpacity: 0.7,
                                        padding: { left: 5, right: 5, top: 0, bottom: 0 }
                                    }
                                },
                            ],
                         },
                    ]
            };
            return settings;
        },
        get_bird_pyramid: function(){
            var self = this;
            var sampleData = [
                    { Index: '6', leading: 60, property_damage: 60, ma_fa: 60, lti: 60 },
                    { Index: '7', leading: 60, property_damage: 60, ma_fa: 60, lti: 60 }
                ];
            var settings = {
                title: "",
                description: "",
                enableAnimations: false,
                showLegend: false,
                showBorderLine: false,
                showToolTips: false,
                padding: { left: 15, top: 15, right: 15, bottom: 15 },
                titlePadding: { left: 10, top: 0, right: 0, bottom: 10 },
                source: sampleData,
                xAxis:
                {
                    dataField: 'Index',
                    visible:false
                },
                valueAxis:
                {
                    unitInterval: 240,
                    visible:false
                },
                colorScheme: 'scheme02',
                seriesGroups:
                    [
                        {
                            type: 'stackedcolumn',
                            columnsGapPercent: 200,
                            seriesGapPercent: 0,
                            columnsTopWidthPercent: 1,
                            columnsBottomWidthPercent: 200,
                            series: [
                                    { dataField: 'leading', labels: { visible: true}, formatFunction: function (value,itemIndex) {return _t('Leading indicators')+' '+self.bird_pyramid_obj[itemIndex].leading;}},
                                    { dataField: 'property_damage', labels: { visible: true}, formatFunction: function (value,itemIndex) {return _t('Property damage')+' '+self.bird_pyramid_obj[itemIndex].property_damage;}},
                                    { dataField: 'ma_fa', labels: { visible: true}, formatFunction: function (value,itemIndex) {return _t('MA, FA')+' '+self.bird_pyramid_obj[itemIndex].ma_fa;}},
                                    { dataField: 'lti', labels: { visible: true}, formatFunction: function (value,itemIndex) {return _t('LTI')+' '+self.bird_pyramid_obj[itemIndex].lti;}},
                                ]
                        }
                    ]
            };
            return settings;
        },
        get_indicator: function(){
            var self = this;
            var sampleData = self.indicator_obj;
            var toolTipCustomFormatFn = function (value, itemIndex, serie, group, categoryValue, categoryAxis) {
                return '<DIV style="text-align:left";><b>'+serie.displayText+':</b>'+ value + ' <br /> </DIV>';
            };
            var settings = {
                title: _t("Indicator"),
                description: "",
                enableAnimations: true,
                showLegend: true,
                showBorderLine: false,
                padding: { left: 5, top: 5, right: 5, bottom: 5 },
                titlePadding: { left: 90, top: 0, right: 0, bottom: 10 },
                source: sampleData,
                xAxis:
                {
                    dataField: 'Place',
                    unitInterval: 1,
                    tickMarks: {
                        visible: true,
                        unitInterval: 1,
                        color: '#888888'
                    },
                    gridLines: {
                        visible: false,
                        unitInterval: 1,
                        color: '#888888'
                    },
                    labels: { visible: true,
                        angle:20,
                        
                        },  
                },
                valueAxis:
                {
                    minValue: 0,
                    visible: true,
                    title: { text: _t('Indicator') },
                    tickMarks: { color: '#888888' },
                    gridLines: { color: '#888888' }
                },
                seriesGroups:
                    [
                        {
                            type: 'stackedcolumn',
                            columnsGapPercent: 100,
                            toolTipFormatFunction: toolTipCustomFormatFn,
                            seriesGapPercent: 20,
                            showLabels: true,
                            formatFunction: function (value, itemIndex, serie, group) {
                                if (value>0){
                                    return serie.displayText+' '+value;
                                }
                            },
                            series: [
                                    { dataField: 'hse_safety_meeting', displayText: _t('SM') },
                                    { dataField: 'hse_workplace_ispection', displayText: _t('WPI') },
                                    { dataField: 'hse_hazard_report', displayText: _t('HR') },
                                    { dataField: 'hse_risk_assessment', displayText: _t('RA') },
                                    { dataField: 'NEAR_MISS_INCIDENT', displayText: _t('NMI') },
                            ]
                        },
                          {
                                type: 'stackedcolumn',
                                columnsGapPercent: 100,
                                toolTipFormatFunction: toolTipCustomFormatFn,
                                seriesGapPercent: 20,
                                showLabels: true,
                                formatFunction: function (value, itemIndex, serie, group) {
                                    if (value>0){
                                        return serie.displayText+' '+value;
                                    }
                                },
                                series: [
                                    { dataField: 'FIRST_AID', displayText: _t('FA') },
                                    { dataField: 'MEDICAL_AID', displayText: _t('MA') },
                                    { dataField: 'PROPERTY_DAMAGE', displayText: _t('Pro dam') },
                                    { dataField: 'SPILL', displayText: _t('Spill') },
                                    { dataField: 'LTI', displayText: _t('LTI') },
                                ]
                          }
                    ]
            };
            return settings;
        },
        get_reclamation: function(obj){
            var sampleData = obj;
            // prepare jqxChart settings
            var toolTipCustomMeas = function (value, itemIndex, serie, group, categoryValue, categoryAxis) {
                return '<DIV style="text-align:left";><b>Маркшейдер <br/>'+value+' </b><br/><br/> </DIV>';
            };
            var toolTipCustomPlan = function (value, itemIndex, serie, group, categoryValue, categoryAxis) {
                return '<DIV style="text-align:left";><b>Төлөвлөгөө <br/>'+value+' </b><br/><br/> </DIV>';
            };
            var settings = {
                title: "Нөхөн сэргээлт м3",
                description: "Төлөвлөгөө гүйцэтгэл",
                enableAnimations: true,
                showLegend: true,
                showBorderLine: false,
                toolTipHideDelay: 5000,
                padding: { left: 5, top: 5, right: 5, bottom: 5 },
                titlePadding: { left: 0, top: 0, right: 0, bottom: 0 },
                source: sampleData,
                colorScheme: 'scheme02',
                xAxis:
                {
                    dataField: 'Date',
                    labels: { visible: true,
                        angle:90,
                        }, 
                    gridLines: { visible: false,}
                },
                valueAxis:
                {
                    minValue: 0,
                    visible: true,
                    gridLines: { visible: false, }
                },
                seriesGroups:
                    [
                        {
                              type: 'area',
                              alignEndPointsWithIntervals: true,
                              series: [
                                      { dataField: 'Plan', displayText: 'Төлөвлөгөө',symbolType: 'circle', 
                                      toolTipFormatFunction: toolTipCustomPlan,  opacity: 1},
                              ]
                          },
                        {
                            type: 'column',
                            
                            columnsGapPercent: 40,
                            seriesGapPercent: 10,
                            series: [
                                    { dataField: 'Meas', displayText: 'Маркшейдер' , toolTipFormatFunction: toolTipCustomMeas,},
                            ]
                        },
                    ]
            };
            return settings;
        },
        display_data: function() {
            var self = this;
            self.$el.html(QWeb.render("hse.safety_report", {widget: self}));
            try {
                $('#mtd_man_hour').jqxChart(self.get_donut(_t('Between the period'),'mtd'));
                $('#ytd_man_hour').jqxChart(self.get_donut(_t('Growth rates'),'ytd'));
                $('#safe_day').jqxChart(self.get_safe_day());

                $('#frequency_lti').jqxChart(self.get_rate(self.rate_obj.lti_frequency,_t('LTI frequency rate'),_t('LTI'),self.rate_obj.lti_max));
                // $('#frequency_lti').jqxChart('addColorScheme', 'customColorScheme', ['blue', 'red','gold']);
                $('#frequency_lti').jqxChart('addColorScheme', 'customColorScheme', ['blue', 'green','red','gold']);
                $('#frequency_lti').jqxChart({ colorScheme: 'customColorScheme' });
                $('#frequency_fa').jqxChart(self.get_rate(self.rate_obj.medical_aid_frequency,_t('Medical aid frequency rate'),_t('MA'),self.rate_obj.medical_aid_max));
                // $('#frequency_fa').jqxChart('addColorScheme', 'customColorScheme', ['blue', 'red','gold']);
                $('#frequency_fa').jqxChart('addColorScheme', 'customColorScheme', ['blue', 'green','red','gold']);
                $('#frequency_fa').jqxChart({ colorScheme: 'customColorScheme' });
                $('#frequency_ma').jqxChart(self.get_rate(self.rate_obj.first_aid_frequency,_t('First aid frequency rate'),_t('FA'),self.rate_obj.first_aid_max));
                // $('#frequency_ma').jqxChart('addColorScheme', 'customColorScheme', ['blue', 'red','gold']);
                $('#frequency_ma').jqxChart('addColorScheme', 'customColorScheme', ['blue', 'green','red','gold']);
                $('#frequency_ma').jqxChart({ colorScheme: 'customColorScheme' });

                $('#severity_lti').jqxChart(self.get_rate(self.rate_obj.lti_severity,_t('LTI severity rate'),_t('Lost days'),self.rate_obj.s_lti_max));
                // $('#severity_lti').jqxChart('addColorScheme', 'customColorScheme', ['blue', 'red','gold']);
                $('#severity_lti').jqxChart('addColorScheme', 'customColorScheme', ['blue', 'green','red','gold']);
                $('#severity_lti').jqxChart({ colorScheme: 'customColorScheme' });
                $('#severity_fa').jqxChart(self.get_rate(self.rate_obj.medical_aid_severity,_t('Medical aid severity rate'),_t('Lost days'),self.rate_obj.s_medical_aid_max));
                // $('#severity_fa').jqxChart('addColorScheme', 'customColorScheme', ['blue','red','gold']);
                $('#severity_fa').jqxChart('addColorScheme', 'customColorScheme', ['blue', 'green','red','gold']);
                $('#severity_fa').jqxChart({ colorScheme: 'customColorScheme' });
                $('#severity_ma').jqxChart(self.get_rate(self.rate_obj.first_aid_severity,_t('First aid severity rate'),_t('Lost days'),self.rate_obj.s_first_aid_max));
                // $('#severity_ma').jqxChart('addColorScheme', 'customColorScheme', ['blue', 'red','gold']);
                $('#severity_ma').jqxChart('addColorScheme', 'customColorScheme', ['blue', 'green','red','gold']);
                $('#severity_ma').jqxChart({ colorScheme: 'customColorScheme' });

                $('#indicator_chart').jqxChart(self.get_indicator());
                $('#indicator_chart').jqxChart('addColorScheme', 'customColorScheme', ['#2fff00','#29dd00','#24c100','#1fa900','#1d9a00','#ff2400','#e62020', '#dd1219','#b31b1b','#a91101']);
                $('#indicator_chart').jqxChart({ colorScheme: 'customColorScheme' });

                $('#bird_pyramid').jqxChart(self.get_bird_pyramid());
                $('#bird_pyramid').jqxChart('addColorScheme', 'customColorScheme', ['#37b860', '#e1e310','#e19505','#e5321e']);
                $('#bird_pyramid').jqxChart({ colorScheme: 'customColorScheme' });

                $('#reclamation_chart').jqxChart(self.get_reclamation(self.plan_actual_obj.plan_actual));
            }
            catch(err) {
                console.log(err.message);
            }
        },
    });
    instance.web.form.custom_widgets.add('hse_safety_report', 'instance.hse.safety_report');
    

}