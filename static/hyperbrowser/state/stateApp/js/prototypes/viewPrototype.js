(function() {
'use strict';
	var _ = require('underscore'),
	Dispatcher = require('./dispatcherPrototype');

	/** the View object is the general prototype object for all views.
	* Override methods in a new prototype object to get specific behavior for view instances.
	* Create the new prototype object with var SpesificViewPrototype = Object.create(View); then
	* var viewInstance = Object.create(SpesificViewPrototype);
	*/
	var View = {

		template: null,

		$: function(selector) {
			return this.$el.find(selector);
		},
		/** The init method ties a model to a view instance
		* It also enforces which properties you can set on a view.
		* Other initializing properties or code must be set with the initialize method
		*/
		init: function(options, customInitializationOptions) {
			var viewOptionsWhiteList = ['model'];
			_.extend(this, _.pick(options, viewOptionsWhiteList));
			this.tagName = (options['el'] || options['tagName'] ||  'div');
			this.classNames = options['classNames' || ''];
			this.setElement(this.tagName);
			this.initialize(customInitializationOptions);
			
		},
		initialize: function(options) {
			return this;
		},
		render: function() {
			return this;
		},
		setElement : function(element) {
			if(element instanceof $) {
				this._setElement(element);
			} else {
				this._setElement(document.createElement(element));
			}
			return this;
		}, 
		// private methods:
		_setElement: function(el) {
			this.$el = (el instanceof $) ? el : $(el);
			this.el = this.$el[0];
			if(this.classNames) {
				this.$el.addClass(this.classNames);
			}
		}
	};
	_.extend(View, Dispatcher );
  module.exports = View;

}());