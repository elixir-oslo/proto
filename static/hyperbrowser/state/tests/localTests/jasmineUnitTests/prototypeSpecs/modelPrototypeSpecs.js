var Model   = require('../../../../stateApp/js/prototypes/modelPrototype.js'),
    History = require('../../../../stateApp/js/prototypes/historyPrototype.js'),
    storage    = require('simplestorage.js');

describe("A Model PROTOTYPE", function() {
    ////////////// Initializing /////////////
        var model, spy, result, history;

        beforeEach(function() {
            storage.flush();
            history = Object.create(History);
            model    = Object.create(Model);
            history.start({initState: {mode:'basic'}});
            model.init();
        });
        afterEach(function() {
            
            //console.log('before stopListening');
            //console.log(model.getSubscribers());
            model.stopListening();
            //console.log('after stopListening');
            //console.log(model.getSubscribers());
            model   = null;
            result = null;
            history.stop();

        });
        ////////////// End initializing /////////////
    it("is defined", function() {
        expect(Model).not.toBeUndefined();
    });

    it("is a dispatcher", function() {
            var model = Model;
            expect( _.isFunction(model.listenTo) ).toBe(true);
            expect( _.isFunction(model.stopListening) ).toBe(true);
            expect( _.isFunction(model.triggerEvent) ).toBe(true);
            model = null;
    });
    
    it("initializes models with properties when creating an object", function() {
            model = Object.create(Model);
            model.init({con:'construct text'});

            expect( model.get('con') ).toEqual('construct text');
        });
    describe("An instance of the model prototype provides", function() {
    
        
        describe("The set method can:", function() {
            it("call the set method", function() {
                spyOn(model, 'set').and.callThrough();
                result = model.set({model:'advanced'});
                expect( model.set ).toHaveBeenCalled();
                expect( model.set ).toHaveBeenCalledWith({model:'advanced'});
            });
            it("set several attributes", function() {
                model.set({
                    a:'alf',
                    b:'bear'
                });

                result = model.get('a');
                expect(result).toEqual('alf');
                result = model.get('b');
                expect(result).toEqual('bear');

            });
            it("set objects with objects ", function() {
                var state = {
                    a:'alf',
                    obj:{ b:'bear',
                          c: { d: 'dear'}
                        }
                    }
                model.set(state);
                result = model.toJSON();
                expect(result).toEqual(state);

            });
            it("trigger 'set' events on the model when setting a property", function() {
                spy    = spyOn(model, 'triggerEvent').and.callThrough();
                result = model.set({model:'advanced'});
                expect( spy ).toHaveBeenCalled();
                expect( spy ).toHaveBeenCalledWith('addEventType:set', {model:model});
            });

            it("call the set method with no attribute and it will fail silently", function() {
                spyOn(model, 'set');
                model.set();

                expect( model.set ).toHaveBeenCalled();
            });
            
            it("trigger 'change' events on the model when setting a property that has already been set", function() {
                
                spy    = spyOn(model, 'triggerEvent');
                model.set({model:'basic'});
                expect( spy ).toHaveBeenCalledWith('addEventType:set', {model:model});
                model.set({model:'advanced'});
                expect( spy ).toHaveBeenCalledWith('addEventType:change', {model:model});
            });

        });
        describe("the get method can:" , function() {
            it("call the get method", function() {
                spy = spyOn(model, 'get');
                model.get('model');

                expect( spy ).toHaveBeenCalled();
            });
            it("get a named attribute", function() { 
                model.set({model:'advanced'});
                result = model.get('model');
                
                expect(result).toEqual('advanced');
            });
        });
        describe("the toJSON method", function() {
            it("clones the model:", function() {
                // test setting objects on objects
                model.set({
                    a:'alfa',
                    b:'beta'
                });
                result = model.toJSON();
                expect(result).toEqual({
                    a:'alfa',
                    b:'beta'
                });
            });
        });
        
    });
});


