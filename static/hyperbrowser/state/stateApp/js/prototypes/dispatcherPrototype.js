(function() {
'use strict';
	var _ = require('underscore');
	var Dispatcher = (function() {
		// Private variables
		var subscribers = {
		}, i, l,
		// Private methods 
		_dispatch = function(eventType, args) {
			var generalEvent  = eventType.split(":")[0],
					spesificEvent = eventType.split(":")[1];
			// dispatching general events ei change
			if(subscribers[generalEvent] !== undefined ) {
				for(i = 0; i < (l = subscribers[generalEvent].length); i+=1) {
						subscribers[generalEvent][i][0].call(subscribers[generalEvent][i][1], args);
				}
			}
			//dispatching spesific events ie change:mode
			if(subscribers[eventType] !== undefined && spesificEvent !== undefined) {
				for(i = 0; i < (l = subscribers[eventType].length); i+=1) {
						subscribers[eventType][i][0].call(subscribers[eventType][i][1], args);
				}
			}
			// dispatching any event if registered if event is an registered event
			if(subscribers['any'] && (subscribers[generalEvent] !== undefined 
				|| subscribers[eventType] !== undefined)) {
				for(i = 0; i < (l = subscribers['any'].length); i+=1) {
						subscribers['any'][i][0].call(subscribers['any'][i][1], args);
				}
			}
		};
		
		return {
			listenTo: function(eventType, callback, context) {
				if(typeof callback === 'function' && (typeof context === 'object')) {
					if(subscribers[eventType] === undefined) {
						subscribers[eventType] = [];
					} 
					var tmp = [callback, context];
					subscribers[eventType].push(tmp);
					tmp			= null;
				} 
			},
			stopListening: function(eventType, callback) {
				var eventCallbacks = subscribers[eventType]; 
				if(eventType === undefined) {
					for(var prop in subscribers) {
						delete subscribers[prop];
					}
					return;
				}
				if(eventType !== undefined && callback === undefined) {
							delete subscribers[eventType];
							return;
				}
				if(eventCallbacks !== undefined && typeof eventCallbacks.length === 'number') {
					for(i = 0; i < (l = eventCallbacks.length); i++) {
						if(eventCallbacks[i][0] === callback) {
							 eventCallbacks[i].splice(i, 1);
						} 
					}
				}
			},
			triggerEvent: function(eventType, args) {
				_dispatch(eventType, args);
			}
			// methods for testing purposes
			, getSubscribers: function() {
				return subscribers;
			}
		};
	}());
	module.exports = Dispatcher;
})();