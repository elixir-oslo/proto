(function() {
	'use strict';
	var Controller = require('./controllers/modeCTRL'),
			ModeModel  = require('./models/modeModel'),
			ModeView   = require('./views/modeView'),
			storage    = require('simplestorage.js'),
			config 		 = require('./stateAppConfig');

	var modeApp = (function() {
		return {
			attachModeListeners: function(modeModel) {
				var mainFrame = $(config.mainFrame), mainContent, mainDocument;
				// Attach listener on home logo to clear
				$(config.hblogo).on('click', function(event) {
					var tmpMode = storage.get('mode');
					storage.flush();
					storage.set('mode', tmpMode);
				});
				// Attach toggle mode functionality on frame border arrow
				$(config.toolBorder).on('click', function(event) {
					event.stopImmediatePropagation();
					if (!window.Galaxy.page.left.hidden) {
						modeModel.toggleMode({'mode': 'basic', 'triggerState': 'history'});
					} else {
						modeModel.toggleMode({'mode': 'advanced', 'triggerState': 'history'});
					}
				});
				// Attach mode functionality to basic and advanced sections on gsuite main welcome page
				mainFrame.on('load', function(e) {
					mainContent  = $($(config.mainFrame)[0]).contents();
					mainDocument = mainContent.filter(function() {
								return this.nodeType === 9;
							});
					var tab1 = mainContent.find(config.tab1);
						if(tab1.length > 0) {
							tab1.find(config.basic).on('click', function() {
								modeModel.toggleMode({'mode': 'basic', 'triggerState': 'history'});
							});
							tab1.find(config.advanced).on('click', function() {
								modeModel.toggleMode({'mode': 'advanced', 'triggerState': 'history'});
							});
						}
				});  
			},
			start: function() {
				var modeCTRL = Object.create(Controller),
				masthead   = $(config.mainNav).first(),
				modeModel  = Object.create(ModeModel),
				modeView   = Object.create(ModeView);

				this.attachModeListeners(modeModel);
			
				// hide Analyse data tab
				masthead.find('ul#analysis').first().hide();
				masthead.find('ul#analysis li').first().removeClass('active');

				modeModel.initialize({mode: 'basic'});
				modeView.init({model: modeModel, tagName: 'ul', classNames: 'nav navbar-nav'});
				modeView.render();
				masthead.prepend(modeView.el);
				//masthead.find('ul li').first().addClass('active');
				modeCTRL.init({model: modeModel});
				
				return modeModel;
			}
		}
	}());
module.exports = modeApp;
}());

