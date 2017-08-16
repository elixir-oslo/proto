(function(){
	'use strict';
	var BaseModel = require('../prototypes/modelPrototype'),
			_         = require('underscore');

	var ToolModel = Object.create(BaseModel);

	_.extend(ToolModel, function() {
		var triggerState = 'history';
		return {
			initialize: function(modelState) {
				this.modelName = 'tool';
				this.eventSetup();
				this.modelState = {};
				this.init(modelState);
			},
			eventSetup: function() {
				this.listenTo('history:tool', this.setToolStateFromHistory, this);
				this.listenTo('home', this.eraseAllModels, this);
				this.listenTo('addEventType:set', this.addSetTool, this);
				this.listenTo('addEventType:change', this.addChangeTool, this);
			},
			setToolState: function(state) {
				triggerState = 'history';
				this.set(state);
			},
			setToolStateFromHistory: function(state) {
				// all model changes from history will use a fresh model, thus setting not changing state
				this.eraseAllModels();
				triggerState = 'tool';
				this.set(state);
			},
			addSetTool: function(args) {
				if(args.model === this) {
					this.triggerEvent( 'set:' + triggerState, this);
				}
			},
			addChangeTool: function(args) {
				if(args.model === this) {
					this.triggerEvent('change:' + triggerState, this);
				}	
			}
		}
 	}());

	module.exports = ToolModel;
}());
