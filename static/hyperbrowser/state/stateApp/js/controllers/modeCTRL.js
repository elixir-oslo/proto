(function(){
	'use strict';
	var BaseController = require('../prototypes/controllerPrototype'),
			_    = require('underscore'),
			config = require('../stateAppConfig');

	var ModeController = Object.create(BaseController);
	_.extend(ModeController, {
		initialize: function() {
			this.listenTo('change:mode', this.parseEvent, this); 
			this.listenTo('change:history', this.parseEvent, this); 
			this.initMode = true;
		},
		parseEvent: function(modelObj) {
			this.toggleLeftPanel();
			if(modelObj === this.model) {
				this.updateMode(modelObj);
			}
		},
		toggleLeftPanel: function() {
			(this.model.get('mode') === "basic" ? window.force_left_panel('hide') : window.force_left_panel('show'));
		},
		updateMode: function(modelObj) {
			this.mainFrame = $(config.mainFrame);
			
			var tabValue, currentMode, 
					isBasic, analysisTab, basicTab, advancedTab, mode, mainTab, currentTab;
				this.mainContents = this.mainFrame.contents();
				this.mainDocument = this.mainContents.filter(function() {
						return this.nodeType === 9;
					});
			isBasic = this.mainDocument.find(config.isBasic);
			analysisTab = this.mainDocument.find(config.analysisTab);
			// Mode change triggered from within a gsuite tool (mainDocument/mainIFrame) 
			if(isBasic.length >= 1) {
				currentMode = modelObj.get('mode');
				var serializedForm, form;
				if(currentMode === 'basic' ) {
    				isBasic.prop('checked', 'checked');
    		    }
				if(currentMode === 'advanced' ) {
					isBasic.removeAttr('checked');
				}
				$(isBasic).trigger("change");
			} else if(analysisTab.length >= 1) {
					// mode change triggered from Gsuite tabs
					mainTab = this.mainDocument.find(config.mainTab);
					basicTab = this.mainDocument.find(config.basicTab);
					advancedTab = this.mainDocument.find(config.advancedTab);
					currentMode  = modelObj.get('mode');
					(currentMode === 'basic'? tabValue = config.tab2: tabValue = config.tab3);
							
					if(this.initMode) {
						this.initMode = false;
						tabValue = config.tab1;
						mainTab.addClass('active').siblings().removeClass('active');
					} else if(currentMode === 'basic') {
						basicTab.addClass('active').siblings().removeClass('active');
					} else if(currentMode === 'advanced') {
						advancedTab.addClass('active').siblings().removeClass('active');
					}
					currentTab = this.mainDocument.find(config.tabs + " " + tabValue);
					currentTab.show().siblings().hide();
				}
		}
	});

	module.exports = ModeController;
}());
