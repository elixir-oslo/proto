
<!DOCTYPE HTML>
<html>
    <!--js-app.mako-->
    <head>
        <title>${app.config.html_title}</title>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
        ## For mobile browsers, don't scale up
        <meta name="viewport" content="maximum-scale=1.0">
        ## Force IE to standards mode, and prefer Google Chrome Frame if the user has already installed it
        <meta http-equiv="X-UA-Compatible" content="IE=Edge,chrome=1">
        ## relative href for site root
        <link rel="index" href="${ h.url_for( '/' ) }"/>
        <link href="${h.url_for('/static/hyperbrowser/state/styles.css')}" rel="stylesheet" type="text/css" >
        ## HyperBrowser favicon setup
        <link rel="apple-touch-icon" sizes="180x180" href="${h.url_for('/static/apple-touch-icon.png')}">
        <link rel="icon" type="image/png" href="${h.url_for('/static/favicon-32x32.png')}" sizes="32x32">
        <link rel="icon" type="image/png" href="${h.url_for('/static/favicon-16x16.png')}" sizes="16x16">
        <link rel="manifest" href="${h.url_for('/static/manifest.json')}">
        <link rel="mask-icon" href="${h.url_for('/static/safari-pinned-tab.svg')}" color="#5bbad5">
        <link rel="shortcut icon" href="${h.url_for('/static/favicon.ico')}">
        <meta name="msapplication-config" content="${h.url_for('/static/browserconfig.xml')}">
        <meta name="theme-color" content="#ffffff">
        ## TODO: use loaders to move everything but the essentials below the fold
        ${ h.css(
            'jquery.rating',
            'jquery-ui/smoothness/jquery-ui',
            ## base needs to come after jquery-ui because of ui-button, ui- etc. name collision
            'base',
            'bootstrap-tour',
        )}
        ${ page_setup() }
    </head>

    <body scroll="no" class="full-content">
        <div id="everything" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;">
            ## TODO: needed?
            <div id="background"></div>

            %if masthead:
            <div id="masthead" class="navbar navbar-fixed-top navbar-inverse"></div>
            ## a div below the masthead to show server messages set in galaxy.ini
            <div id="messagebox" style="display: none;"></div>
            ## a message displayed when the user has been inactive and needs to reactivate their account
            <div id="inactivebox" class="panel-warning-message" style="display: none;"></div>
            %endif

        </div><!--end everything-->
        <div id='dd-helper' style="display: none;"></div>
        ${ js_disabled_warning() }

        ## js libraries and bundled js app
        ${ h.js(
            'bundled/libs.bundled',
            'bundled/' + js_app_name + '.bundled'
        )}
        <script type="text/javascript">
            ${js_app_entry_fn}(
                ${ h.dumps( options ) },
                ${ h.dumps( bootstrapped ) }
            );
        </script>
        <script src="${h.url_for('/static/hyperbrowser/state/index.js')}"></script>
    </body>
</html>

## ============================================================================
<%def name="page_setup()">
    ## Send js errors to Sentry server if configured
    %if app.config.sentry_dsn:
    ${h.js( "libs/tracekit", "libs/raven" )}
    <script>
        Raven.config('${app.config.sentry_dsn_public}').install();
        %if trans.user:
            Raven.setUser( { email: "${trans.user.email|h}" } );
        %endif
    </script>
    %endif

    <script type="text/javascript">
        // this is needed *before* the app code is loaded - many MVC access Galaxy.root for their url
        // TODO: change this by using a common Backbone.Model base class and url fn
        window.Galaxy = { root: '${ options[ "root" ] }' };

        window.force_left_panel = function(op) { window.Galaxy.page.left.force_panel(op); }
        function hbGetBaseUrl() { return '${h.url_for("/")}'; }
    </script>

    %if not form_input_auto_focus is UNDEFINED and form_input_auto_focus:
    <script type="text/javascript">
        $(document).ready( function() {
            // Auto Focus on first item on form
            if ( $("*:focus").html() == null ) {
                $(":input:not([type=hidden]):visible:enabled:first").focus();
            }
        });
    </script>
    %endif

    ## google analytics
    %if app.config.ga_code:
    <script type="text/javascript">
        (function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
        (i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
        m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
        })(window,document,'script','//www.google-analytics.com/analytics.js','ga');
        ga('create', '${app.config.ga_code}', 'auto');
        ga('send', 'pageview');
    </script>
    %endif

</%def>

## ============================================================================
<%def name="js_disabled_warning()">
    <noscript>
        <div class="overlay overlay-background noscript-overlay">
            <div>
                <h3 class="title">Javascript Required for Galaxy</h3>
                <div>
                    The Galaxy analysis interface requires a browser with Javascript enabled.<br>
                    Please enable Javascript and refresh this page.
                </div>
            </div>
        </div>
    </noscript>
</%def>
