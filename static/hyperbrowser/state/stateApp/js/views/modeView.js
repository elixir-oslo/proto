(function(){
	'use strict';
	var BaseView = require('../prototypes/viewPrototype'),
	_    = require('underscore'),
	storage    = require('simplestorage.js');

	var ModeView = Object.create(BaseView);

	_.extend(ModeView, (function() {
			// private variables
			// Self is needed because the parseEvent method is called from a click event and not from this object,
			// shadowing the this keyword.
			var self;
			return {
				template: _.template(
					'<li class="dropdown active">'
					+ '<a target="_self" id="mode" class="dropdown-toggle noLink" href="" ><%= this.toggleViewText(mode)%></a>'
           	 		+ '<ul class="dropdown-menu">'
               		+ '<li class="<%= (mode === "basic"? "disabledMode disabled": "") %>"><a href="" id="<%= (mode === "basic"? "": "basic") %>">Basic mode</a></li>'
               		+ '<li class="<%= (mode === "advanced"? "disabledMode disabled": "") %>"><a href="" id="<%= (mode === "advanced"? "": "advanced") %>">Advanced mode</a></li>'
             		+ '</ul>'
					+ '</li>'
					),
				initialize: function(options) {
					this.$el.attr('id', 'mode');
					this.eventSetup();
					self = this;
				},
				eventSetup: function() {
					this.$el.click(this.parseEvent);
					this.listenTo('change:mode', this.update, this);
					this.listenTo('change:history', this.update, this);
				},
				parseEvent: function(event) {
					event.preventDefault();
					event.stopPropagation();
					var attr = event.target.id;
					if(attr === 'basic' || attr === 'advanced') {
						self.model.toggleMode({mode: attr, triggerState: 'history'});
					} else {
						self.$el.find('.dropdown-menu').toggle();
					}
				},
				render: function(props) {
					var attributes = this.model.toJSON();
					this.$el.html(this.template(attributes));
					return this;
				},
				toggleViewText: function(text) {
					return (text === "basic" ? "Mode: Basic" : "Mode: Advanced");
				},
				update: function() {
					this.render();
				}
			}
		}())
	);

	module.exports = ModeView; 

}());
