(function () {
    'use strict';
    var _ = require('underscore'),
        storage = require('simplestorage.js'),
        Dispatcher = require('./dispatcherPrototype'),
        uriAnchor = require('../polyfills/uriAnchor_mod');

    var History = (function () {
        // Private variables
        var triggerHashchange = true,
        // Private methods
            _hashChangeHandler = function (event) {
                var tmpUrlObject = uriAnchor.makeAnchorMap();
                if (triggerHashchange) {
                    event.data.self.triggerEvent('history:change', tmpUrlObject);
                }
            },
            _pushStateHandler = function (event) {
                console.log("History pushState eventType");
            };

        return {
            start: function (options) {
                uriAnchor.configModule({sub_delimit_char: "->"})
                options = options || {};

                if (options.pushState !== undefined) {
                    $(window).on('pushState', {self: this}, this.pushStateHandler);
                } else {
                    $(window).on('hashchange', {self: this}, this.hashChangeHandler);
                }
                this.listenTo('history:change', this.setModelState, this);
                this.listenTo('change:history', this.changeHistory, this);
                this.listenTo('set:history', this.changeHistory, this);

                if (location.hash !== '') {
                    //some browsers (firefox) does not trigger hashchange when coming 
                    //to a webpage for the first time
                    this.triggerEvent('history:change', uriAnchor.makeAnchorMap());
                } else if (storage.index().length > 0) {
                    this.triggerEvent('history:change', this.getStoredStateObject());
                } else {
                    this.triggerEvent('history:mode', options.initState);
                    triggerHashchange = false;
                    uriAnchor.setAnchor(options.initState, {}, true);
                }
            },
            stop: function (options) {
                options = options || {};
                this.stopListening();
                if (options) {
                    $(window).off('pushState');
                } else {
                    $(window).off('hashchange');
                }
            },
            //public methods only needed for testing
            hashChangeHandler: function (event) {
                event.stopPropagation();
                event.preventDefault();
                _hashChangeHandler(event);
            },
            pushStateHandler: function (event) {
                event.stopPropagation();
                _pushStateHandler(event);
            },
            setModelState: function (locationObj) {
                // Invariant: All states found in the location hash object is already in the storedStateObject
                var tmpModel, dependentObj;
                for (var prop in locationObj) {
                    tmpModel = {};
                    if (locationObj.hasOwnProperty(prop)) {
                        if ((prop.charAt(0) !== '_')) {
                            dependentObj = ('_' + prop);
                            if (locationObj[dependentObj]) {
                                tmpModel = locationObj[dependentObj];
                            }
                            tmpModel[prop] = locationObj[prop];
                            this.triggerEvent('history:' + prop, tmpModel);
                        }
                    }
                }
            },
            changeHistory: function (modelObj) {
                var modelName = modelObj.get('modelName'), modelState = modelObj.toJSON(),
                    locationObj = uriAnchor.makeAnchorMap();
                locationObj[modelName] = modelState[modelName];
                locationObj['_' + modelName] = {};
                for(var prop in modelState) {
                    if(modelState.hasOwnProperty(prop) && prop !== modelName) {
                        locationObj['_' + modelName][prop] = modelState[prop];
                    }
                    storage.set(prop, modelState[prop]);
                }
                triggerHashchange = false;
                uriAnchor.setAnchor(locationObj, {}, true);
            },
            getStoredStateObject: function () {
                var i, j, store = storage.index(), tmpStorageObj = {};
                for (i = 0; i < (j = store.length); i += 1) {
                    tmpStorageObj[store[i]] = storage.get(store[i]);
                }
                return tmpStorageObj;
            }
        };
    }());
    _.extend(History, Object.create(Dispatcher));
    module.exports = History;
})();