    var ToolCTRL   = require('../../../../stateApp/js/controllers/toolCTRL.js'),
        Dispatcher = require('../../../../stateApp/js/prototypes/dispatcherPrototype.js'),
        ToolModel  = require('../../../../stateApp/js/models/toolModel.js'),
        History    = require('../../../../stateApp/js/prototypes/historyPrototype.js'),
        uriAnchor  = require('../../../../stateApp/js/polyfills/uriAnchor_mod');

    describe("A toolCTRL prototype object", function() {
        //window.top.frames['galaxy_main'].location = {};  
    it("is defined", function() {
        expect(ToolCTRL).not.toBeUndefined();
    });

    it("provides the methods of the BASE prototype controller", function() {
        var toolCTRL = Object.create(ToolCTRL);
            expect( _.isFunction(toolCTRL.init) ).toBe(true);
            toolCTRL = null;
    });
     
    describe("On a toolCTRL instance one can", function() {

        ////////////// Initializing /////////////
        var toolCTRL, spy, toolModel, history;

        beforeEach(function() {
            history = Object.create(History);
            toolCTRL  = Object.create(ToolCTRL);
            toolModel = Object.create(ToolModel);
            
        });
        afterEach(function() {
            toolCTRL.stopListening();
            toolCTRL = null;
        });
        ////////////// End initializing /////////////
        it("sets a dispatcher when creating an object", function() {
            expect( toolCTRL.listenTo).toBe(Dispatcher.listenTo);
        });
    });

    });


