module.exports = function(config) {
    'use strict';
    config.set({
            frameworks: ['browserify','jasmine'],
                reporters: ['spec'],
                browsers: ['PhantomJS'],
                files: [

                        '../node_modules/jquery/dist/jquery.min.js',
                        '../node_modules/underscore/underscore-min.js',
                        '../node_modules/jasmine-jquery/lib/jasmine-jquery.js',

                        '../index.js',
                        '../tests/**/*.js'

                        ],
                preprocessors: {
                '../tests/**/*.js':['browserify']
            }
                });
};
