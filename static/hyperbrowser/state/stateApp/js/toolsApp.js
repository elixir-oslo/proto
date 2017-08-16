(function () {
    'use strict';
    var Controller = require('./controllers/toolCTRL'),
        ToolModel = require('./models/toolModel'),
        ToolView = require('./views/toolView'),
        uriAnchor = require('./polyfills/uriAnchor_mod'),
        config = require('./stateAppConfig');

    var toolApp = (function () {
        var toolCTRL, toolModel, toolView, parentFrame,
            toolsFrame, mainFrame, mainContent, mainDocument, toolState,
            currentMode, isBasic, analysisTab,

            _setUpMainFrame = function (modeModel) {
                mainFrame.on('load', function (e) {
                    mainContent = $($(config.mainFrame)[0]).contents();
                    mainDocument = mainContent.filter(function () {
                        return this.nodeType === 9;
                    });
                    // Set up 'click' event listener for gsuitbox
                    mainDocument.ready(function () {
                        $(config.gsuitebox, mainContent).on('click', function (e) {
                            toolState = {
                                tool: e.currentTarget.text
                            };
                            toolModel.eraseAllModels();
                            toolModel.setToolState(toolState);
                        });
                        _setUpGsuiteTabs(modeModel);
                        // Get state when ever a form is loaded
                        //var formSelects = mainContent.find('form select');
//                        var form = mainContent.find('form'),
//                         var form = mainContent.find('form.protoForm'),
//                             serializedForm = '';
//                             //serializedForm = form.serialize();
//                         if (form.length > 0) {
//                             toolModel.setToolState({
//                                 serializedForm: serializedForm,
//                                 currentSelection: e.currentTarget.name
//                             });
//                         } else if (uriAnchor.makeAnchorMap().mode === undefined) {
//                             // To account for situations where mode is not set in url
//                             modeModel.toggleMode({mode: modeModel.get('mode'), triggerState: 'history'});
//                         }
                        if (uriAnchor.makeAnchorMap().mode === undefined) {
                             // To account for situations where mode is not set in url
                             modeModel.toggleMode({mode: modeModel.get('mode'), triggerState: 'history'});
                        }
                    });
                });
            },
            _setUpToolFrame = function (modeModel) {
                // Setting up the toolFrame 
                toolsFrame.on('load', function (e) {
                    var toolsContent = $($(config.toolFrame)[0]).contents(),
                        toolsDocument = toolsContent.filter(function () {
                            return this.nodeType === 9;
                        });

                    $(config.toolLinks, toolsContent).on('click', function (e) {
                        toolState = {
                            tool: e.currentTarget.text
                        };
                        // Could also create new toolModel object
                        toolModel.eraseAllModels();
                        toolModel.setToolState(toolState);
                    });
                });
            },
            _setUpGsuiteTabs = function (modeModel) {
                var mode, anchorMap, tabValue, basicTab,
                    advancedTab;
                isBasic = mainDocument.find(config.isBasic);
                analysisTab = mainDocument.find(config.analysisTab);
                // Decides if the main g-suite tabs exist in main iFrame
                if (analysisTab.length >= 1) {
                    basicTab = mainDocument.find(config.basicTab);
                    advancedTab = mainDocument.find(config.advancedTab);
                    basicTab.on('click', function () {
                        modeModel.toggleMode({mode: 'basic', triggerState: 'history'});
                    });
                    advancedTab.on('click', function () {
                        modeModel.toggleMode({mode: 'advanced', triggerState: 'history'});
                    });
                }
                // // Decides if the tool provides both basic and advanced view, ie is a g-suite tool
                // if (isBasic.length >= 1) {
                //     isBasic.parent().hide();
                // }
            };

        return {
            start: function (modeModel) {
                // toolCTRL = Object.create(Controller);
                toolModel = Object.create(ToolModel);
                toolView = Object.create(ToolView);

                parentFrame = $(config.parentFrame);
                toolsFrame = $(config.toolFrame);
                mainFrame = $(config.mainFrame);

                // toolCTRL.init({model: toolModel});
                toolModel.initialize();
                toolView.init({
                    model: toolModel,
                    tagName: mainFrame
                });

                _setUpMainFrame(modeModel);
                _setUpToolFrame(modeModel);
            }
        }

    }());
    module.exports = toolApp;
}());
