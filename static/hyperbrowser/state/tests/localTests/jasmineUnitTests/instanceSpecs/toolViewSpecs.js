var ToolModel  = require('../../../../stateApp/js/models/toolModel'),
    ModeView   = require('../../../../stateApp/js/views/modeView'),
    Dispatcher = require('../../../../stateApp/js/prototypes/dispatcherPrototype'),
    History    = require('../../../../stateApp/js/prototypes/historyPrototype.js');

describe("A toolView Prototype ", function() {
    it("is defined", function() {
        expect(ModeView).not.toBeUndefined();
    });
    
    it("provides the methods of the BASE VIEW prototype object", function() {
        expect( _.isFunction(ModeView.initialize) ).toBe(true);
        expect( _.isFunction(ModeView.render) ).toBe(true);
        expect( _.isFunction(ModeView.setElement) ).toBe(true);
        modeViewInst = null;
    });
    it("provides the methods of the ModeView prototype object", function() {
        expect( _.isFunction(ModeView.eventSetup) ).toBe(true);
        modeViewInst = null;
    });
    
    
    describe("On a mode view instance on can", function() {
        ////////////// Initializing /////////////
        var modeViewInst, result, dispatcher,
            toolModel, spy, eventSpy;

        beforeEach(function() {
            dispatcher   = Object.create(Dispatcher);
            toolModel    = Object.create(ToolModel);
            modeViewInst = Object.create(ModeView);
            //console.log(toolModel);
            toolModel.initialize({mode:'basic'});
            modeViewInst.init({model:toolModel, classNames: "clickTest"});  
        });
        afterEach(function() {
            modeViewInst = null;
            toolModel    = null;
            dispatcher   = null;
        });
        ////////////// End initializing /////////////
    
       
    });

});


