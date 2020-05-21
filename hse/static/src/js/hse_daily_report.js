openerp.hse.daily = function(instance) {
    var QWeb = instance.web.qweb;
    var _t = instance.web._t;
    // #################################### DAILY REPORT ##########################################
    instance.hse.daily_report = instance.web.form.FormWidget.extend(instance.web.form.ReinitializeWidgetMixin, {
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
            this._super.apply(this, arguments);
            var self = this;
            this.set({
                date: false,
                projects: false,
            });
            this.updating = false;
            this.field_manager.on("field_changed:date", this, function() {
                this.set({"date": this.field_manager.get_field_value("date")});
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
            self.on("change:date", self, self.initialize_content);
            self.on("change:projects", self, self.initialize_content);
        },
        
        initialize_content: function() {
            var self = this;
            this.destroy_content();
            var date = self.get('date');
            var projects = self.get('projects')[0][2];
            var man_hour;
            var man_day;
            var project_name;
            var injury_month;
            var injury_ytd;
            var lost_time_ytd;
            var lost_time_month;
            var all_injury;
            var accident_type;
            var incident_rate;
            var all_hse;
            var all_hse_survaljit;
            var bird_pyramid_obj;
            var rate_obj;
            return new instance.web.Model("hse.daily.report").call("get_injury", [date,projects,new instance.web.CompoundContext()])
            .then(function(details) {
                injury_month = details.month;
                injury_ytd = details.ytd;
                return new instance.web.Model("hse.daily.report").call("get_lost_time", [date,projects,new instance.web.CompoundContext()])
                .then(function(details) {
                    lost_time_month = details.month;
                    lost_time_ytd = details.ytd;
                    return new instance.web.Model("hse.daily.report").call("get_injury_detail", [date,projects,new instance.web.CompoundContext()])
                    .then(function(details) {
                        all_injury = details;
                        accident_type = details.all_accident;
                        return new instance.web.Model("hse.daily.report").call("get_nope_lti", [date,projects,new instance.web.CompoundContext()])
                        .then(function(details) {
                            man_hour = details.inc_man_hour;
                            man_day = details.inc_total_day;
                            incident_rate = details;
                            return new instance.web.Model("hse.daily.report").call("get_all_hse", [date,projects,new instance.web.CompoundContext()])
                            .then(function(details) {
                                all_hse = details;
                                return new instance.web.Model("hse.safety.report").call("get_bird_pyramid", [date,projects,new instance.web.CompoundContext()])
                                .then(function(details) {
                                    bird_pyramid_obj = details;
                                    return new instance.web.Model("hse.safety.report").call("get_rate", [date, date,projects,new instance.web.CompoundContext()])
                                    .then(function(details) {
                                        rate_obj = details;
                                    });
                                }); 
                            });
                        });
                    });
                });
            }).then(function(result) {
                self.bird_pyramid_obj = bird_pyramid_obj;
                self.rate_obj = rate_obj;
                self.date = date;
                self.projects = projects;
                self.man_hour = man_hour;
                self.all_hse = all_hse;
                self.man_day = man_day;
                self.injury_month = injury_month;
                self.injury_ytd = injury_ytd;
                self.lost_time_month = lost_time_month;
                self.lost_time_ytd = lost_time_ytd;
                self.all_injury = all_injury;
                self.accident_type = accident_type;
                self.incident_rate = incident_rate;
                self.display_data();
            });
        },
        get_all_hse: function(project_name, desc, obj, locations){
            var  sampleData = obj;
            var series = []
            var toolTipCustom = function (value, itemIndex, serie, group, categoryValue, categoryAxis) {
                return '<DIV style="text-align:left; width:100%;"><b> '+serie.dataField+':'+value+' </b><br/><br/> </DIV>';
            };
            for (var i = 0; i < locations.length; i += 1){
                series.push({dataField: locations[i], displayText: locations[i], toolTipFormatFunction: toolTipCustom});
            }

            var settings = {
                title: '',
                description: project_name+' '+desc,
                enableAnimations: true,
                showBorderLine: false,
                // showLegend: true,
                toolTipHideDelay: 15000,
                
                titlePadding: { left: 0, top: 0, right: 0, bottom: 0 },
                source: sampleData,
                xAxis:
                {
                    dataField: 'Үзүүлэлт',
                    showGridLines: false,
                    labels: { visible: true,
                    angle:55,
                    horizontalAlignment: 'right',
                    verticalAlignment: 'center',
                    },  
                },
                colorScheme: 'scheme05',
                seriesGroups:
                    [
                        {
                            type: 'stackedcolumn',
                            // orientation: 'horizontal',
                            columnsGapPercent: 60,
                            seriesGapPercent: 20,
                            showLabels: true,
                            valueAxis:
                            {
                                minValue: 0,
                                // unitInterval: 5,
                                // flip: true,
                                displayValueAxis: true,
                                description: '',
                                axisSize: 'auto',
                                tickMarksColor: '#888888',
                                gridLines: { visible: false },
                            },
                            series: series
                        }
                    ]
            };
            if (desc==_t('Leading indicators')){
                settings['showLegend']=true
                settings['legendLayout']= { left: 335, top: 0, width: 140, height: 310, flow: 'vertical' };
                settings['padding']= { left: 0, top: 0, right: 130, bottom: 0 };
            }else{
                settings['showLegend']=false
                // settings['legendLayout']= { left: 0, top: 0, width: 0, height: 0, flow: 'vertical' };
                settings['padding']= { left: 0, top: 0, right: 0, bottom: 0 };
            }
            return settings;
        },
        get_chart_bar: function(){
            self = this;
            var sampleData = self.all_injury.all_injury;
            max_injury = self.all_injury.max_injury;
            var serie = [];
            var toolTipCustom = function (value, itemIndex, serie, group, categoryValue, categoryAxis) {
                return '<DIV style="text-align:left; width:100%;" ><b> '+serie.displayText+':'+value+' </b><br/><br/> </DIV>';
            };
            for (var i = 0; i < self.accident_type.length; i += 1){
                serie.push({
                    dataField: self.accident_type[i].id, displayText: self.accident_type[i].name,
                    toolTipFormatFunction: toolTipCustom
                });
            }
            var settings = {
                title: _t("Detail of Accident/Incident"),
                description: "",
                enableAnimations: true,
                showLegend: true,
                showBorderLine: false,
                toolTipHideDelay: 15000,
                padding: { left: 0, top: 0, right: 130, bottom: 0 },
                legendLayout: { left: 275, top: 0, width: 140, height: 200, flow: 'vertical' },
                titlePadding: { left: 0, top: 0, right: 0, bottom: 0 },
                source: sampleData,
                xAxis:
                    {
                        dataField: 'Month',
                        unitInterval: 1,
                        // axisSize: 'auto',
                         labels: { visible: true,
                        angle:90,
                        horizontalAlignment: 'right',
                        verticalAlignment: 'center',
                        },  
                        gridLines: {
                            visible: false,
                            interval: 1,
                            color: '#BCBCBC'
                        },
                        valuesOnTicks: false
                    },
                valueAxis:
                {
                    unitInterval: 5,
                    minValue: 0,
                    labels: { horizontalAlignment: 'right' },
                    tickMarks: { visible: false },
                    gridLines: { visible: false },
                },
                colorScheme: 'scheme04',
                seriesGroups:
                    [
                        {
                            type: 'stackedcolumn',
                            columnsGapPercent: 20,
                            seriesGapPercent: 0,
                            series: serie,
                            showLabels: true,
                        }
                    ]
            };
            return settings;
        },
        get_chart_incident_rate: function(){
            self = this;
            var sampleData = self.incident_rate.month_lti
            var max_lti = self.incident_rate.max_lti
            var settings = {
                title: _t("LTI frequency rate=(LTI*200,000) / Man/hour"),
                description: "",
                showLegend: true,
                showBorderLine: false,
                enableAnimations: true,
                padding: { left: 0, top: 0, right: 0, bottom: 0 },
                titlePadding: { left: 0, top: 0, right: 0, bottom: 0 },
                source: sampleData,
                xAxis:
                    {
                        dataField: 'Month',
                        gridLines: { visible: false },
                        valuesOnTicks: false
                    },
                colorScheme: 'scheme01',
                columnSeriesOverlap: false,
                seriesGroups:
                    [
                        {
                            type: 'line',
                            valueAxis:
                            {
                                visible: true,
                                position: 'right',
                                unitInterval: 500000,
                                minValue: 0,
                                title: { text: _t("Man hour") },
                                gridLines: { visible: false },

                                labels: { horizontalAlignment: 'left' }
                            },
                            series: [
                                    { dataField: 'man_hour', displayText: _t("Man hour") , opacity: 1.0, lineWidth: 2, dashStyle: '2,2'}
                                ]
                        },
                        {
                            type: 'line',
                            valueAxis:
                            {
                                visible: true,
                                unitInterval: 0.5,
                                minValue: 0,
                                maxValue: max_lti+1,
                            },
                            series: [
                                    { dataField: 'lti', displayText: _t("LTI") , symbolType: 'square',
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
                                { dataField: 'ir', displayText: _t("LTI frequency rate") , symbolType: 'square',
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
                                ]
                        },
                        
                    ]
            };
            return settings;
        },
        get_donut: function(lti, desc, big_is) {
            var data = [];
            data.push({ text: 'Used', value:  100}); // current
            data.push({ text: 'Available', value: 0 }); // remaining
            var settings = {
                title: '',
                description: desc,
                enableAnimations: true,
                showLegend: false,
                showBorderLine: true,
                backgroundColor: '#FAFAFA',
                padding: { left: 0, top: 0, right: 0, bottom: 0 },
                titlePadding: { left: 0, top: 0, right: 0, bottom: 0 },
                source: data,
                showToolTips: false,
                seriesGroups:
                [
                    {
                        type: 'donut',
                        useGradientColors: false,
                        series:
                            [
                                {
                                    showLabels: false,
                                    enableSelection: false,
                                    displayText: 'text',
                                    dataField: 'value',
                                    labelRadius: 100,
                                    initialAngle: 90,
                                    radius: 35,
                                    innerRadius: 33,
                                    centerOffset: 0
                                }
                            ]
                    }
                ]
            };
            var valueText = lti;
            if (big_is){
                settings.drawBefore = function (renderer, rect) {
                    sz = renderer.measureText(valueText, 0, { 'class': 'chart-inner-text-big' });
                    renderer.text(
                    valueText,
                    rect.x + (rect.width - sz.width) / 2,
                    rect.y + rect.height / 2.4,
                    0,
                    0,
                    0,
                    { 'class': 'chart-inner-text-big' }
                    );
                }
            }else{
                settings.drawBefore = function (renderer, rect) {
                    sz = renderer.measureText(valueText, 0, { 'class': 'chart-inner-text' });
                    renderer.text(
                    valueText,
                    rect.x + (rect.width - sz.width) / 2,
                    rect.y + rect.height / 2,
                    0,
                    0,
                    0,
                    { 'class': 'chart-inner-text' }
                    );
                }
            }
            return settings;
        },
        get_bird_pyramid: function(){
            var self = this;
            var sampleData = [
                    { Index: '6', leading: 60, property_damage: 60, ma_fa: 60, lti: 60 },
                    { Index: '7', leading: 60, property_damage: 60, ma_fa: 60, lti: 60 }
                ];
            // prepare jqxChart settings
            var settings = {
                title: "",
                description: "",
                enableAnimations: false,
                showLegend: false,
                showBorderLine: false,
                showToolTips: false,
                padding: { left: 0, top: 0, right: 0, bottom: 0 },
                titlePadding: { left: 0, top: 0, right: 0, bottom: 0 },
                source: sampleData,
                xAxis:
                {
                    dataField: 'Index',
                    visible:false
                },
                valueAxis:
                {
                    unitInterval: 20,
                    visible:false
                },
                colorScheme: 'scheme02',
                seriesGroups:
                    [
                        {
                            type: 'stackedcolumn',
                            columnsGapPercent: 10,
                            seriesGapPercent: 0,
                            columnsTopWidthPercent: 1,
                            columnsBottomWidthPercent: 100,
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
        get_rate: function(obj, title, displayText, maxValue){
            var sampleData = [];
            for (var i=0; i<obj.length; i++){
                sampleData.push({ Year: obj[i].year, frequency: obj[i].frequency, ir: obj[i].ir, plan: obj[i].plan, man_hour: obj[i].man_hour })
            }
            
            var latencyThreshold = 35;
            var settings = {
                title: title+" = ("+displayText+"*200,000) / "+_t("Man hour"),
                description: "",
                enableAnimations: true,
                showLegend: true,
                showBorderLine: false,
                showToolTips: false,
                padding: { left: 0, top: 0, right: 170, bottom: 0 },
                legendLayout: { left: 675, top: 0, width: 150, height: 200, flow: 'vertical' },
                titlePadding: { left: 0, top: 0, right: 0, bottom: 0 },
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
                                title: { text: _t("Man hour")},
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
                                // { dataField: 'plan', displayText: _t("Tolerable") , symbolType: 'circle',
                                //     formatFunction: function (value,itemIndex) {if (value>0)return value;},
                                    
                                //     labels:{
                                //         visible: true,
                                //         backgroundColor: 'yellow',
                                //         backgroundOpacity: 0.2,
                                //         borderColor: '#7FC4EF',
                                //         borderOpacity: 0.7,
                                //         padding: { left: 5, right: 5, top: 0, bottom: 0 }
                                //     }
                                // },
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
        destroy_content: function() {
            if (this.dfm) {
                this.dfm.destroy();
                this.dfm = undefined;
            }
        },
        display_data: function() {
            var self = this;
            self.$el.html(QWeb.render("hse.daily_report", {widget: self}));
            try {
                $('#nope_lti_day').jqxChart(self.get_donut(self.man_day,_t("Day"),true));
                $('#nope_lti_day').jqxChart('addColorScheme', 'customColorScheme', ['#00BAFF', '#EDE6E7']);
                $('#nope_lti_day').jqxChart({ colorScheme: 'customColorScheme' });
                $('#nope_lti_hour').jqxChart(self.get_donut(self.man_hour,_t("Man/hour"),false));
                $('#nope_lti_hour').jqxChart('addColorScheme', 'customColorScheme', ['#00BAFF', '#EDE6E7']);
                $('#nope_lti_hour').jqxChart({ colorScheme: 'customColorScheme' });
                // INJURY
                $('#injury_this_month').jqxChart(self.get_donut(self.injury_month,_t("This month"),true));
                if (self.injury_month>0){
                    $('#injury_this_month').jqxChart('addColorScheme', 'customColorScheme', ['red', '#EDE6E7']);
                }
                else{
                    $('#injury_this_month').jqxChart('addColorScheme', 'customColorScheme', ['green', '#EDE6E7']);
                }
                $('#injury_this_month').jqxChart({ colorScheme: 'customColorScheme' });
                
                $('#injury_this_year').jqxChart(self.get_donut(self.injury_ytd,_t("This year"),true));
                if (self.injury_ytd>20){
                    $('#injury_this_year').jqxChart('addColorScheme', 'customColorScheme', ['red', '#EDE6E7']);
                }
                else{
                    if (self.injury_ytd == 0){
                        $('#injury_this_year').jqxChart('addColorScheme', 'customColorScheme', ['green', '#EDE6E7']);
                    }else{
                        $('#injury_this_year').jqxChart('addColorScheme', 'customColorScheme', ['gold', '#EDE6E7']);
                    }
                }
                $('#injury_this_year').jqxChart({ colorScheme: 'customColorScheme' });

                // LOST TIME
                $('#lost_time_month').jqxChart(self.get_donut(self.lost_time_month,_t("This month"),true));
                if (self.lost_time_month>0){
                    $('#lost_time_month').jqxChart('addColorScheme', 'customColorScheme', ['red', '#EDE6E7']);
                }
                else{
                    $('#lost_time_month').jqxChart('addColorScheme', 'customColorScheme', ['green', '#EDE6E7']);
                }
                $('#lost_time_month').jqxChart({ colorScheme: 'customColorScheme' });
                
                $('#lost_time_year').jqxChart(self.get_donut(self.lost_time_ytd,_t("This year"),true));
                if (self.lost_time_ytd>20){
                    $('#lost_time_year').jqxChart('addColorScheme', 'customColorScheme', ['darkred', '#EDE6E7']);
                }
                else{
                    if (self.lost_time_ytd == 0){
                        $('#lost_time_year').jqxChart('addColorScheme', 'customColorScheme', ['green', '#EDE6E7']);
                    }else{
                        $('#lost_time_year').jqxChart('addColorScheme', 'customColorScheme', ['gold', '#EDE6E7']);
                    }
                    
                }
                $('#lost_time_year').jqxChart({ colorScheme: 'customColorScheme' });
                if (self.accident_type){
                    // ALL INJURY
                    $('#injury_detail').jqxChart(self.get_chart_bar());
                    $('#injury_detail').jqxChart('addColorScheme', 'customColorScheme', ['DodgerBlue', 'cyan', 'CadetBlue', 'PaleGreen', 'DarkGoldenrod', 'LightCoral']);
                    $('#injury_detail').jqxChart({ colorScheme: 'customColorScheme' });
                    
                }
                // $('#incident_rate').jqxChart(self.get_chart_incident_rate());
                for (var i=0; i<self.all_hse.length; i++){
                    $('#hutlugch'+self.all_hse[i].project_id).jqxChart(self.get_all_hse(self.all_hse[i].project_name, _t("Leading indicators"), self.all_hse[i].hutlugch, self.all_hse[i].locations));
                    $('#hutlugch'+self.all_hse[i].project_id).jqxChart('addColorScheme', 'customColorScheme', 
                        ['#82dd7f', '#39abc3','#fbcb03','#d5ddff','#fd635a','#ee8c3f','#d7e753','#BBDAF6','#DEC990','#dfdce3']);
                    $('#hutlugch'+self.all_hse[i].project_id).jqxChart({ colorScheme: 'customColorScheme' });

                    $('#survaljit'+self.all_hse[i].project_id).jqxChart(self.get_all_hse(self.all_hse[i].project_name, _t("Lagging indicators"), self.all_hse[i].survaljit, self.all_hse[i].locations));
                    $('#survaljit'+self.all_hse[i].project_id).jqxChart('addColorScheme', 'customColorScheme', 
                        ['#82dd7f', '#39abc3','#fbcb03','#d5ddff','#fd635a','#ee8c3f','#d7e753','#BBDAF6','#DEC990','#dfdce3']);
                    $('#survaljit'+self.all_hse[i].project_id).jqxChart({ colorScheme: 'customColorScheme' });
                }

                $('#bird_pyramid').jqxChart(self.get_bird_pyramid());
                $('#bird_pyramid').jqxChart('addColorScheme', 'customColorScheme', ['#37b860', '#e1e310','#e19505','#e5321e']);
                $('#bird_pyramid').jqxChart({ colorScheme: 'customColorScheme' });

                $('#frequency_lti').jqxChart(self.get_rate(self.rate_obj.lti_frequency,_t("LTI frequency rate"),_t("LTI"),self.rate_obj.lti_max));
                $('#frequency_lti').jqxChart('addColorScheme', 'customColorScheme', ['blue', 'red','gold']);
                // $('#frequency_lti').jqxChart('addColorScheme', 'customColorScheme', ['blue', 'green','red','gold']);
                $('#frequency_lti').jqxChart({ colorScheme: 'customColorScheme' });
            }
            catch(err) {
                console.log(err.message);
            }
        },
    });

    instance.web.form.custom_widgets.add('hse_daily_report', 'instance.hse.daily_report');
}