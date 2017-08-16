var ToolModel = require('../../../../stateApp/js/models/toolModel.js'),
    ModeModel = require('../../../../stateApp/js/models/modeModel.js'),
    storage = require('simplestorage.js'),
    History = require('../../../../stateApp/js/prototypes/historyPrototype.js'),
    uriAnchor = require('../../../../stateApp/js/polyfills/uriAnchor_mod');

describe("A ToolModel class / constructor", function () {
    ////////////// Initializing /////////////
    var toolModel, view, spy, result, subs, history, modeModel, state;
    beforeEach(function () {
        storage.flush();
        location.hash = '';
        //storage.set('mode', 'basic');
        modeModel = Object.create(ModeModel);
        modeModel.initialize({mode: 'basic'});
        history = Object.create(History);
        toolModel = Object.create(ToolModel);


        //toolModel.stopListening();

        toolModel.initialize();
        history.start({initState: {mode: 'basic'}});
        state = {
            toolState: {
                pathName: '/state/hyper',
                toolSearch: '?GALAXY_URL=https%3A//hyperbrowser.uio.no/state/tool_runner&tool_id=hb_test_1'
            },
            tool: 'Analyze genomic tracks',
            toolHref: 'https://hyperbrowser.uio.no/state/hyper?GALAXY_URL=https%3A//hyperbrowser.uio.no/state/tool_runner&tool_id=hb_test_1',
            toolClass: 'tool-link',
            hostName: 'hyperbrowser.uio.no',
            target: 'galaxy_main'
        };
        toolModel.setToolState(state);

    });
    afterEach(function () {
        toolModel.stopListening();
        history.stop();
        toolModel = null;

    });
    ////////////// End initializing /////////////
    it("is defined", function () {
        expect(ToolModel).not.toBeUndefined();
    });
    it("provides the methods of the BASE prototype model", function () {

        expect(_.isFunction(toolModel.set)).toBe(true);
        expect(_.isFunction(toolModel.get)).toBe(true);
        expect(_.isFunction(toolModel.toJSON)).toBe(true);
    });
    it("sets a named attribute when creating an object, tested with get()", function () {
        expect(toolModel.get('tool')).toEqual('Analyze genomic tracks');
    });
    it("sets a object as attribute when creating an object, tested with get()", function () {
        expect(toolModel.get('toolState')).toEqual({
            pathName: '/state/hyper',
            toolSearch: '?GALAXY_URL=https%3A//hyperbrowser.uio.no/state/tool_runner&tool_id=hb_test_1'
        });

    });
    it("sets a object as attribute when creating an object, tested with toJSON()", function () {
        var testState = toolModel.toJSON();

        expect(testState).toEqual(state);

    });
    describe("On a tool instance one can", function () {

        it("provides the methods of the ToolModel prototype object", function () {
            expect(_.isFunction(ToolModel.initialize)).toBe(true);
            expect(_.isFunction(ToolModel.eventSetup)).toBe(true);
            modeViewInst = null;
        });
        it("initializing tool sets the state, tested with get", function () {
            result = toolModel.get('tool');
            expect(result).toEqual('Analyze genomic tracks');
        });

        it("initializing tool sets the state, tested with trigger change", function () {
            toolModel.stopListening();
            spy = spyOn(toolModel, 'triggerEvent').and.callThrough();
            toolModel.initialize();
            toolModel.setToolState({
                toolState: {
                    pathName: '/state/hyper',
                    toolSearch: '?GALAXY_URL=https%3A//hyperbrowser.uio.no/state/tool_runner&tool_id=hb_test_1'
                },
                tool: 'Analyze genomic tracks',
                toolHref: 'https://hyperbrowser.uio.no/state/hyper?GALAXY_URL=https%3A//hyperbrowser.uio.no/state/tool_runner&tool_id=hb_test_1',
                toolClass: 'tool-link',
                hostName: 'hyperbrowser.uio.no',
                target: 'galaxy_main'
            });

            expect(spy).toHaveBeenCalled();
            // two events pr model state
            expect(spy.calls.count()).toEqual(2);
        });

        it("Get modelName", function () {
            result = toolModel.get("modelName");
            //console.log("Get modelName:");
            //console.log(result);
            expect(result).toEqual("tool");
        });
        describe("Historify", function () {
            it("returns an object with the tool name and a modelState", function () {
                result = toolModel.toJSON();
                // console.log(result);
            });
        });

    });
});


