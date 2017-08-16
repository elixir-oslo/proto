(function () {
    'use strict';
    var BaseController = require('../prototypes/controllerPrototype'),
        _ = require('underscore'),
        config = require('../stateAppConfig');

    var ToolController = Object.create(BaseController);

    _.extend(ToolController, {
        initialize: function () {
            this.listenTo('set:tool', this.parseEvent, this);
        },
        parseEvent: function (eventObj) {
            if (eventObj.get("serializedForm") !== undefined) {
                this.createAjaxCall(eventObj);
            }
        },
        //*
        /* Ajax call will only be executed when setting a tool for the first time.
         */
        createAjaxCall: function (eventObj) {
            var self = this, currentSelection;
            currentSelection = eventObj.get('currentSelection');
            $.ajax({
                type: 'post',
                url: config.urlHyperPostfix + "?" + currentSelection,
                data: eventObj.get('serializedForm'),
                beforeSend: function () {
                    self.triggerEvent('ajaxCall');
                },
                success: function (data) {
                    self.triggerEvent('change:tool', {model: this, data: data});
                },
                error: function (XMLHttpRequest, textStatus, errorThrown) {
                    console.log("AJAX Error");
                }
            });
        }
    });
    module.exports = ToolController;
}());