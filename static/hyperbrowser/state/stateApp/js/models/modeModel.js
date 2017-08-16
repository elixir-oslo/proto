(function(){
	'use strict';
	var BaseModel = require('../prototypes/modelPrototype'),
			_         = require('underscore');

	var ModeModel = Object.create(BaseModel);

	_.extend(ModeModel, function() {
		var triggerState = 'history';
		return {
			initialize: function(modelState) {
        this.modelName = 'mode';
				this.eventSetup();
                this.init(modelState);

			},
			eventSetup: function() {
				this.listenTo('history:mode', this.toggleMode, this);
				this.listenTo('addEventType:set', this.addSetMode, this);
				this.listenTo('addEventType:change', this.addChangeMode, this);
			},
			toggleMode: function(state) {
				var tmpMode;
				if(state === undefined) {
					tmpMode = this.get('mode');
					triggerState = 'history';
			 		// Should I implement the strategy design pattern here, just to get some more meat?
			 		// It can be linked to state, but it isn't important to make the code easier to read 
			 		// or maintain, or is it? Or should it only listen for changes from the state:mode
			 		//console.log('triggered from the view');
					(tmpMode === 'basic' ? this.set({mode: 'advanced'}) : this.set({mode: 'basic'}));
				}
				else if(state && state.mode === "basic" || state.mode === "advanced" ) {
					if(state.triggerState !== undefined) {
						triggerState = state.triggerState;
					} else {
						triggerState = 'mode';
					}
					this.set({mode: state.mode});
				} else {
					// throw error
					console.log('Error: toggleMode');
				}
			},
			addSetMode: function(args) {
				if(args.model === this) {
					this.triggerEvent('set:' + triggerState, this);
				}
			},
			addChangeMode: function(args) {
				if(args.model === this) {
					this.triggerEvent('change:' + triggerState, this);
				}	
			}
		}
 	}());

	module.exports = ModeModel;
}());
