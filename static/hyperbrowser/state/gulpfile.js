(function() {
'use strict';
	var gulp       = require('gulp'),
	    gulputil   = require('gulp-util'),
	    source     = require('vinyl-source-stream'),
	   // streamify  = require('gulp-streamify'),
	    browserify = require('browserify'),
	    //uglify     = require('gulp-uglify'),
	    rename		 = require('gulp-rename'),
	    Server     = require('karma').Server,
	    watch      = require('gulp-watch');
	    //jshint    = require('gulp-jshint'),;

	gulp.task('default', ['util', 'browserify']);

	gulp.task('test', ['browserify', 'watch'], function (done) {
	  return new Server({
	    configFile: __dirname + '/tests/karma.conf.js',
	    singleRun: false
	  }, done).start();
	});
	gulp.task('serverTest', ['browserify'], function (done) {
	  return new Server({
	    configFile: __dirname + '/tests/karma.conf.js',
	    singleRun: true
	  }, done).start();
	});

	gulp.task('watch', function() {
		gulp.watch('stateApp/**/*.js', ['browserify']);
	});
	
	gulp.task('util', function() {
		return gulputil.log('Gulp is running');
	});

	gulp.task('browserify', function() {
		var bundleStream = browserify('./main.js').bundle();
		return bundleStream
			.pipe(source('main.js'))
			//.pipe(streamify(uglify()))
			.pipe(rename('index.js'))
			
			.pipe(gulp.dest('./'));
	});
	
}());
//	gulp.task('watch', function() {
	//	gulp.watch('stateApp/js/**/*.js', ['jshint']);
	//});
/*
	gulp.task('testing', function (done) {
	  return new Server({
	    configFile: __dirname + '/tests/karma.conf.js',
	    singleRun: true
	  }, done).start();
	});
*/



	//gulp.task('jshint', function() {
		//return gulp.src('stateApp/js/**/*.js')
		//	.pipe(jshint())
			//.pipe(jshint.reporter('jshint-stylish'));
	//});