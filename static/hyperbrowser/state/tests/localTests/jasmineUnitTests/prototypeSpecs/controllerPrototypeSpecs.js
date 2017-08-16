var Controller = require('../../../../stateApp/js/prototypes/controllerPrototype.js');

describe("A Controller PROTOTYPE", function() {
    
    it("is defined", function() {
        expect(Controller).not.toBeUndefined();
    });

    it("provides the init and modeCTRL methods", function() {
            var baseCTRL = Controller;
            expect( _.isFunction(baseCTRL.init) ).toBe(true);
            //expect( _.isFunction(baseCTRL.modeCTRL) ).toBe(true);
            //expect( _.isFunction(baseCTRL.toJSON) ).toBe(true);
            baseCTRL = null;
    });
});


