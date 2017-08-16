    var ModeModel  = require('../../../../stateApp/js/models/modeModel'),
    storage    = require('simplestorage.js'),
    ModeView   = require('../../../../stateApp/js/views/modeView'),
    Dispatcher = require('../../../../stateApp/js/prototypes/dispatcherPrototype'),
    History    = require('../../../../stateApp/js/prototypes/historyPrototype.js');

describe("A modeView Prototype ", function() {
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
        expect( _.isFunction(ModeView.parseEvent) ).toBe(true);
        expect( _.isFunction(ModeView.update) ).toBe(true);
        expect( _.isFunction(ModeView.toggleViewText) ).toBe(true);
        modeViewInst = null;
    });
    
    describe("On a mode view instance on can", function() {
        ////////////// Initializing /////////////
    var modeViewInst, result, dispatcher,
        modeModel, spy, eventSpy, history;

    beforeEach(function() {
        storage.flush();
        location.hash = '';
        history = Object.create(History);
        
        dispatcher   = Object.create(Dispatcher);
        modeModel    = Object.create(ModeModel);
        modeViewInst = Object.create(ModeView);

        modeModel.initialize({mode:'basic'});
        modeViewInst.init({model:modeModel, classNames: "clickTest"}); 
        window.force_left_panel = function(mode) {};
        setFixtures(modeViewInst.el); 
        history.start({initState: { mode: 'basic' }});

    });
    afterEach(function() {
        modeModel.stopListening();
        modeViewInst.stopListening();
        modeViewInst = null;
        modeModel    = null;
        dispatcher   = null;
        history.stop();
    });
    ////////////// End initializing /////////////
    
        it("set the root tagName when created", function() {
            modeViewInst = null;
            modeViewInst = Object.create(ModeView);
            modeViewInst.init({model:modeModel, tagName: 'aside'});

            modeViewInst.render();
            expect(modeViewInst.tagName).toEqual('aside');
        });

        it("set classes on the DOM element when initialized/created", function() {
            modeViewInst = null;
            modeViewInst = Object.create(ModeView);
            modeViewInst.init({model: modeModel, classNames: 'hidden toggle'});
            modeViewInst.render();
            result = modeViewInst.el;
            expect(result.outerHTML).toEqual('<div class="hidden toggle">'
                
                +'<a target="_self" id="mode" class="noLink" href="">Mode: Basic</a>' 
                     + '<div class="submenu">'
                        + '<ul>'
                            + '<li class="disabledMode"><a href="" id="basic">Basic mode</a></li>'
                            + '<li class=""><a href="" id="advanced">Advanced mode</a></li>'
                        + '</ul>'
                    + '</div>'
                + '</div>');
        });

        it("rewrite the render function", function() {
            spy = spyOn(modeViewInst, 'render');

            result = modeViewInst.render("new render property");
            expect( spy ).toHaveBeenCalledWith("new render property"); 
        });

        it("set the top element", function() {
            result = modeViewInst.setElement('p');
            expect(modeViewInst.el.nodeName.toLowerCase()).toEqual('p');
        });

        it("the top element is wrapped in a jQuery element", function() {
            result = modeViewInst.setElement('p');
            expect(modeViewInst.$el instanceof $).toBe(true);
        });

        it("initialize methods with proper attributes when the init method is called", function() {
            spyOn(ModeView, 'initialize');
            modeViewInst = Object.create(ModeView);
            modeViewInst.init( {model:modeModel},  {initialize: 'some initialize options'});
            expect(modeViewInst.initialize).toHaveBeenCalledWith( {initialize: 'some initialize options'});
        });

        it("render a template ready for attachment to the DOM", function() {
            modeViewInst.render();
            result = modeViewInst.el;
            expect(result.outerHTML).toEqual('<div class="clickTest">'
                +'<a target="_self" id="mode" class="noLink" href="">Mode: Basic</a>' 
                     + '<div class="submenu">'
                    + '<ul>'
                        + '<li class="disabledMode"><a href="" id="basic">Basic mode</a></li>'
                        + '<li class=""><a href="" id="advanced">Advanced mode</a></li>'
                    + '</ul>'
                    + '</div>'
                + '</div>');
        });

        it("containing dispatcher methods", function() {
            expect( _.isFunction(modeViewInst.listenTo) ).toBe(true);
            expect( _.isFunction(modeViewInst.stopListening) ).toBe(true);
            expect( _.isFunction(modeViewInst.triggerEvent) ).toBe(true);
        });
        
        describe("DOM testing: " , function() {
            beforeEach(function() {
                //mock a window method
               
            });
            afterEach(function() {

            });
            it("listens to the events specified in the initialize method of the view", function() { 
                spy = spyOn(modeViewInst.model, 'toggleMode');
                $('.clickTest').trigger( "click" );
                
                expect(spy).toHaveBeenCalled();
            });
            
            it("the jasmine-jquery helper can trigger DOM events", function() {
               eventSpy = spyOnEvent('.clickTest', 'click');
                $('.clickTest').trigger( "click" );
                
                expect('click').toHaveBeenTriggeredOn('.clickTest');
                expect(eventSpy).toHaveBeenTriggered();
            });

            describe("Following a click:", function() {
                it("does not trigger a new hashchange event", function() {
                    //var history = Object.create(History);
                    spy = spyOn(history, 'hashChangeHandler').and.callThrough();
                    history.start({initState: { mode: 'basic' }});
                    $('.clickTest').trigger( "click" );
                    expect(spy.calls.count()).toEqual(0);
                });
                it("does not setModelState on history", function() {
                    //var history = Object.create(History);
                    spy = spyOn(history, 'setModelState').and.callThrough();
                    history.start({initState: { mode: 'basic' }});
                    $('.clickTest').trigger( "click" );
                    expect(spy.calls.count()).toEqual(0);
                });
            });  
        });   

    });

});


