(function(){
	'use strict';
	var BaseView = require('../prototypes/viewPrototype'),
			 _    	 = require('underscore'),
			 $    	 = require('jquery'),
			 Spinner = require('spin.js'),
			 config  = require('../stateAppConfig');

	var ToolView = Object.create(BaseView);

	_.extend(ToolView, (function() {
			// private variables
			var spinner, background;
			return {
				
				initialize: function(options) {
					this.listenTo('change:tool', this.update, this);
					this.listenTo('ajaxCall', this.disablePage, this);
				},
				disablePage: function() {
					background = $(config.background);
					background.css('z-index', 2);
					spinner = new Spinner({color:'#999', lines: 10, corners:0.9}).spin();
					background.append(spinner.el);
				},
				enablePage: function() {
					background.css('z-index', -1);
					background.remove();
				},
				setCorrectIframeUrl: function(data) {
					// Prefixing host url with "hyper". Because the host url is added automatically 
					// from the location of the running script, and this script is outside the script 
					// that performs the ajax call
					var tmp = data.split('?' + config.urlSourcePostfix).join(config.urlHyperPostfix +'?' + config.urlSourcePostfix);
					return tmp.split("form.action = '?'").join("form.action = '"+ config.urlHyperPostfix + "?'");
					 
				},
				render: function(model) {
					this.mainDocument = this.el.contentWindow.document;
					var dataCorrected = this.setCorrectIframeUrl(model.data);
					var newDoc = this.mainDocument.open("text/html", "replace");
					newDoc.write(dataCorrected);
					newDoc.close();
					this.enablePage();
					
					return this;
				},
				update: function(model) {
					this.render(model);
				}
			}
		}())
	);

	module.exports = ToolView; 

}());