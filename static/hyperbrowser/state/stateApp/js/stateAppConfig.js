(function() {
'use strict';
	// HTML element id's and classes used in the state application
	// Ex: If the name of the element #galaxy_main is to be changed,
	// the corresponding property of the below object must also be changed.
	var stateAppConfig = (function() {
		return {
			parentFrame 			: 'iframe',
			mainFrame   			: '#galaxy_main',
			toolFrame   			: '#galaxy_tools',
			hblogo   	  			: '#masthead .title',
			mainNav     			: '#masthead .navbar-tabs',
			toolBorder  			: '#left .panel-collapse',
			gsuitebox   			: '.gsuitebox a',
			toolLinks   			: 'a.tool-link',
			isBasic     			: '#isBasic input',
			analysisTab 			: '#tab-links',
			basicTab    			: '#tab-links li:nth-child(2)',
			advancedTab 			: '#tab-links li:nth-child(3)',
			tabs							: '.tabs',
			tab1							: '#tab1',
			tab2							: '#tab2',
			tab3							: '#tab3',
      basic 						: '#basic',
			advanced  				: '#advanced',
			background  			: '#background',
			urlHyperPostfix   : 'hyper',
			urlSourcePostfix  : 'mako'
		}
	}());
	module.exports = stateAppConfig;
}());
