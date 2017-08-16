var Model = require('../../../../stateApp/js/prototypes/modelPrototype.js'),
    View  = require('../../../../stateApp/js/prototypes/viewPrototype.js'),
    Dispatcher = require('../../../../stateApp/js/prototypes/dispatcherPrototype.js');

describe("A View PROTOTYPE", function() {
    ////////////// Initializing /////////////
    var modeView,
        modeModel;

    beforeEach(function() {
        dispatcher   = Object.create(Dispatcher);
        modeModel    = Object.create(Model);
        modeModel.init({mode:'advanced'});
        modeView     = Object.create(View);
        modeView.init({model:modeModel, dispatcher: dispatcher});
    });
    afterEach(function() {
        
        
        modeView      = null;
        modeModel     = null;
    });
    ////////////// End initializing /////////////
    it("is defined", function() {
        expect(View).not.toBeUndefined();
    });

    it("provides the initialize and render methods", function() {
            modeView = null;
            modeView = Object.create(View);
            expect( _.isFunction(modeView.initialize) ).toBe(true);
            expect( _.isFunction(modeView.render) ).toBe(true);
            expect( _.isFunction(modeView.escape) ).toBe(false);
            modeView = null;
    });

    it("sets a named attribute when creating an object", function() {
            expect( modeView.model.modelProperties ).toBe(modeModel.modelProperties);
    });

    it("does not set attributes not named in the white list when creating an object", function() {
            var newView = Object.create(View);
            newView.init({model: modeModel, fakeModel: "basic"});

            expect( newView.model.get('mode')).toEqual('advanced');
            expect( newView.model.get('fakeModel') ).toBeUndefined();
    });
    describe("On a SUPER view instance", function() {
        ////////////// Initializing /////////////
        var viewInstance,
            modelInstance;

        beforeEach(function() {
            modeModel    = Object.create(Model);
            modeModel.init( {mode: "basic"} );
            viewInstance         = Object.create(View);
            viewInstance.init( {modelInstance:modeModel} );
        });
        afterEach(function() {
            viewInstance         = null;
            modelInstance        = null;
        });
        ////////////// End initializing /////////////
        it("one can set the top element", function() {
            var result = viewInstance.setElement('p');
            expect(viewInstance.el.nodeName.toLowerCase()).toEqual('p');
        });
        it("the top element is wrapped in a jQuery element", function() {
            var result = viewInstance.setElement('p');
            expect(viewInstance.$el instanceof $).toBe(true);
        });
        it("the initialize method is called with proper attributes when the init method is called", function() {
            spyOn(View, 'initialize');
            viewInstance         = Object.create(View);
            viewInstance.init( {modelInstance:modeModel},  {initialize: 'some initialize options'});
            expect(viewInstance.initialize).toHaveBeenCalledWith( {initialize: 'some initialize options'});
        });
        /*
        it("the $ function gets a local DOM representation", function() {

        });
        */
    });
});