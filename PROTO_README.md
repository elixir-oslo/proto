# Galaxy ProTo
## Table of Contents

  * [Introduction](#introduction)
  * [Background](#background)
  * [Features](#features)
  * [Installation](#installation)
  * [Tool development](#tool-development)
    * [Documentation of the API](#documentation-of-the-api)
    * [Miscellaneous features, tips and best practices](#miscellaneous-features-tips-and-best-practices)
      * [Reading datasets from history](#reading-datasets-from-history)
      * [Hide options box](#hide-options-box)
      * [HTML output](#html-output)
      * [Extra output files linked from the main HTML output](#extra-output-files-linked-from-the-main-html-output)
      * [Running R code](#running-r-code)
      * [More than one output history element](#more-than-one-output-history-element)
      * [Storing state information](#storing-state-information)
      * [Variable number of option boxes](#variable-number-of-option-boxes)
      * [Use class constants to store selection box text](#use-class-constants-to-store-selection-box-text)
      * [Changing type of ProTo option box](#changing-type-of-proto-option-box)
      * [CamelCase or snake_case?](#camelcase-or-snake_case)
  * [Known limitations](#known-limitations)
  * [Version log](#version-log)

## Introduction
The Galaxy Prototyping Tool API (Galaxy ProTo) is an extension of the Galaxy web-based platform for data intensive biomedical research, which is available from [galaxyproject.org](https://galaxyproject.org). Galaxy ProTo is a new tool building methodology introduced by the [Genomic HyperBrowser project] (https://hyperbrowser.uio.no) as an unofficial alternative for defining Galaxy tools. Galaxy ProTo provides:

- Rapid and simple development of Galaxy tools using Python code only (no XML knowledge needed)
- Fully on-the-fly development, no need to restart the server or reload the tool to witness changes
- Fully dynamic user interface, able to change the interface based upon e.g. earlier selection, input files or database queries

## Background

In addition to being a feature-rich framework for biomedical research, Galaxy can also be thought of as a simple way to provide web access to locally developed functionality. Galaxy can for instance be used by master students to showcase their developed functionality to the supervisors and examiners, or it can be used by researchers to easily provide access to their *ad hoc* developed scripts. For such use, however, Galaxy poses some limitations. For one, the developer needs to learn the XML format used by Galaxy, with all the twists and turns inherent in the format. Also, the format itself has limited support for dynamics in the parameter option boxes, e.g. for providing the user with direct feedback based upon dynamic calculations within the interface itself.

## Features

Instead of XML files, Galaxy ProTo supports defining the user interface of a tool as a Python class. There are no limitations to what kind of code that can be executed to generate the interface. For instance one could read the beginning of an input file and provide dynamic options based on the file contents. When developing a ProTo tool, results of changes in the code can be witnessed on-the-fly in a web browser; there is no need to reload the tool or restart the Galaxy server. When development is finished, a ProTo tool can be easily be installed into the Galaxy tool menu alongside the standard Galaxy tools. Galaxy ProTo thus empowers developers without Galaxy experience to easily develop Galaxy tools, both for prototyping purposes, but also for developing fully functional, interactive tools.

## Installation

It is highly recommended that users of Galaxy ProTo create a GitHub fork of the project to host their developed ProTo tools, so this guide will follow that approach. If, for some reason, you do not want to create a GitHub fork, please just skip item 1 and 2, use the URL "https://github.com/elixir-no-nels/proto" in item 3.i., and skip item 3.iii.

1. Create a github user (if you do not already have one), at https://github.com, and sign in.
2. Fork Galaxy Proto:
  1. Access "https://github.com/elixir-no-nels/proto"
  2. Click the fork button and follow the guide
  3. Note the URL to your forked repo, e.g. "https://github.com/user/proto"
3. Clone your GitHub fork to your computer/server:
  1. `git clone https://github.com/user/proto galaxy_proto` using the URL to your forked repo
  2. `cd galaxy_proto`
  3. `git remote add upstream https://github.com/elixir-no-nels/proto`
  4. `git checkout proto_master`
4. Create your own GIT branch for your tools, in this guide named "myproject_dev":
  1. `git branch myproject_dev`
  2. `git checkout myproject_dev`
5. Set up the main Galaxy config files:
  1. `cd config`
  2. `cp galaxy.ini.sample galaxy.ini`
  3. `cp tool_conf.xml.sample tool_conf.xml`
6. Set up an empty PostgreSQL database (follow a PostgreSQL tutorial to do this). See [Known Limitations] (#known-limitations).
7. Edit galaxy.ini:
  1. Uncomment "port" and set it to an unused port number (or keep the default 8080 if you want).
  2. Uncomment "host" and set it to `0.0.0.0` (given that you want to access the Galaxy ProTo web server from other computers).
  3. Uncomment "database_connection" and set it to point to your PostgreSQL database, as explained in the [Galaxy Wiki] (https://wiki.galaxyproject.org/Admin/Config/Performance/ProductionServer#Switching_to_a_database_server).
  4. Uncomment "admin_users" and add the email address(es) for the admins. An admin account is needed to publish finished ProTo tools to the tool menu. You will need to register with the same address in Galaxy to get the admin account.
  5. Uncomment "id_secret" and set it to the result of the one-liner generation code in the comments.
  6. Uncomment "restricted_users" and add any users that need access to private development tools (e.g. developers or test users). Admin users are by default also restricted users and no not need to be listed twice.
  7. Uncomment "proto_id_secret" and set it to the result of the one-liner generation code in the comments, but with a different code than "id_secret". NOTE: This step is important if you want to maintain the redo functionality, see "Known Limitations" above.
8. Start up Galaxy ProTo:
  1. `cd ..` (to exit the "config" directory).
  2. `./run.sh`. The Galaxy should now be accessible from e.g. http://yourserver.edu:8080, where the hostname and port will change according to your setup.
  - For making Galaxy run in the background, use `./run.sh --daemon` to start it and `./run.sh --stop-daemon` to stop it.
9. In order to commit code changes and push to your github fork, run:
    - `git add $FILE` for all new and changed files
    - `git commit -m "Some nice commit message"`
    - `git push origin myproject_dev` to push all local commits to GitHub

## Tool development

Tool development in ProTo consists of three major steps, each handled by dedicated tool under the tool header "ProTo development tools":

1. **ProTo tool generator**: This tool is used to dynamically generate a Python module (i.e. a *.py file) that defines a new ProTo tool. The module is a duplicate of a selected tool template, containing a very simple usage example.
2. **ProTo tool explorer**: After a Python module has been generated, one needs to edit the *.py file in some editor (preferably an IDE, like PyCharm). One can then witness the creation of the tool on-the-fly using the ProTo tool explorer. Just save the file, and the user interface of the tool will be updated. The ProTo tool explorer contains all the tools that has not been installed (i.e. is under development).
3. **ProTo tool installer**: After the tool has been finalized, it can be published as a separate tool in the tool menu. A restricted user can carry out this with the ProTo tool installer, but an administrator needs to refresh the tool menu for the new tool to appear.

See the help text inside each tool for more usage details.

### Documentation of the API

The complete API is documented as pydoc strings within the [ToolTemplate.py] (lib/proto/tools/ToolTemplate.py) file, and a HTML compilation of the documentation (with some manual modifications) is available in the [ToolTemplate.html] (https://rawgit.com/elixir-no-nels/proto/proto_dev/static/proto/html/ToolTemplate.html) file.

A basic tutorial has yet to be written, but here are some points to get you started:

1. A ProTo tool is a subclass of the `GeneralGuiTool` class. The user interface and functionality of the tool is defined based upon whether certain methods are available in the subclass (uncommented from the [ToolTemplate.py] (lib/proto/tools/ToolTemplate.py) or [ToolTemplateMinimal.py] (lib/proto/tools/ToolTemplateMinimal.py) file), and if available, the exact content which is returned from the method.
2. The minimal set of methods to be defined is `getToolName()` and `execute()`. Only defining these two methods will produce a tool existing of a single execute button.
3. Adding other input (and output) boxes is a matter of first defining them in the return statement of `getInputBoxNames()` with a certain key, e.g. "histSelect". Secondly, one needs to implement a method `getOptionsBoxKey`, exchanging the actual key string in the method, e.g. `getOptionsBoxHistSelect`. The return value of this method defines the type of input field, e.g. returning a string creates a text box, while a list of strings creates a selection list. See the [ToolTemplate.html] (https://rawgit.com/elixir-no-nels/proto/proto_dev/static/proto/html/ToolTemplate.html) documentation for the complete list of input fields.
4. The parameter `prevChoices` provided to the `getOptionsBox...()` methods is a namedtuple object of all previous options boxes (including the previous content of the current options box). One can access previous user selections and unput by using standard member access, e.g. `prevChoices.histSelect`. Similarly the parameter `choices` provided to the `execute()` method and others contain the full list of option box selections, in the same format.
5. The parameter `galaxyFn` contains the disk path to the output dataset of the tool. Please write tool output to this file path. See [ToolTemplate.html] (https://rawgit.com/elixir-no-nels/proto/proto_dev/static/proto/html/ToolTemplate.html) for more details.
6. Validation of input parameters can be done in the method `validateAndReturnErrors()`. It takes in the `choices` parameter (as explained in point 4), so that the selections and other input from the user can be validated. If there is something wrong with the input, e.g. the user typed some alphabetic characters in a numbers-only input field, just return a string with the error message, and this will be shown to the user (and the "Execute" button will be hidden).

### Miscellaneous features, tips and best practices

#### Reading datasets from history
To read a dataset from history, first define one of the input boxes to be a `"__history__"` input box, optionally filtering for certain file types. For reading the file, make use of the utility method `extractFnFromDatasetInfo`, e.g.:

```
@classmethod
def getOptionBoxHistory(cls, prevChoices):
    return '__history__, 'txt'
    
@classmethod
def execute(cls, choices, galaxyFn=None, username=''):
    from proto.CommonFunctions import extractFnFromDatasetInfo, extractFileSuffixFromDatasetInfo, extractNameFromDatasetInfo
    datasetInfo = choices.history
    fileName = extractFnFromDatasetInfo(datasetInfo)
    suffix = extractFileSuffixFromDatasetInfo(datasetInfo) # if needed
    datasetName = extractNameFromDatasetInfo(datasetInfo) # if needed
    with open(fileName) as infile:
        (...)
```

#### Hide options box
To make an options box visible only if the user has selected something in a previous options box (e.g. selected a history element):

```
@classmethod
def getOptionBoxHideable(cls, prevChoices):
    if prevChoices.history:
        return ['Choice1', 'Choice2']</code>
```

The reason this works is that returning None from an getOptionsBox method hides the box. If no return is specified in a Python method, it by default returns None.

#### HTML output
The module [HtmlCore] (lib/proto/HtmlCore.py) contains an API for simple generation of HTML pages. For example, a simple HTML page can be created like this (in the `execute()` method):
```
from proto.HtmlCore import HtmlCore

with open(galaxyFn, 'w') as outFile:
    core = HtmlCore()
    core.header('This is a header')
    core.paragraph('This is a paragraph.')
    core.link('This is a link', 'http://www.google.com')

    print>>outFile, core
```

Note that when using `begin()` and `end()` methods, which adds the HTML start and end tags, the output file format (as defined by the `getOutputFormat()` method of the tool) must be set to 'customhtml'.

An overview of the methods are available from [HtmlCore.html]  (https://rawgit.com/elixir-no-nels/proto/proto_dev/static/proto/html/HtmlCore.html). However, the methods have not been documented yet.

#### Extra output files linked from the main HTML output
The module [StaticFile] (lib/proto/StaticFile.py) contains a very useful class, especially for HTML output, named `GalaxyRunSpecificFile`. The aim of this class is to serve as a reference to an additional output file connected to the output dataset. Such extra files are stored under the 'dataset_XYZ_files' directory (for those familiar with the Galaxy file hierarchy). The class is aimed for use in the `execute()` method of a tool. The following example (also making use of [HtmlCore] (#html-output)) shows the usage:

```
from proto.HtmlCore import HtmlCore
from proto.StaticFile import GalaxyRunSpecificFile

with open(galaxyFn, 'w') as outFile:
    core = HtmlCore()
    core.header('This is a header')

    myFile = GalaxyRunSpecificFile(['extra', 'detailed_results.html'], galaxyFn)
    path = myFile.getDiskPath(ensurePath=True) # ensurePath=True makes sure all directories are created
    url = myFile.getURL()
    link = myFile.getLink('Link to detailed results')

    print>> open(path, 'w'), 'This is the contents of the file'

    core.descriptionLine('Disk path of file:', path)
    core.descriptionLine('URL to file:', url)
    core.paragraph(link)

    print>>outFile, core
```

An overview of the methods are available from [StaticFile.html]  (https://rawgit.com/elixir-no-nels/proto/proto_dev/static/proto/html/StaticFile.html), but not yet with detailed documentation.

#### Running R code
Galaxy ProTo includes support for running `R` code via the `rpy2` Python package. If `R` is available when starting up Galaxy ProTo, `rpy2` is automatically installed. However, `R` is not a mandatory dependency for Galaxy ProTo; the rest of the functionality still works without `R` installed.

In addition to the standard `rpy2` setup, Galaxy ProTo includes advanced autoconversion setup that automatically converts standard Python object (lists, vectors, dicts) and `NumPy` objects (arrays, matrices, scalars) into the corresponding `R` objects, and vice-versa. In almost all cases, no extra thought needs to be put on conversion, just include the parameters that feels natural, in stark contrast to the default `rpy2` setup.

To run `R` code, just import `from proto.RSetup import r` (or `robjects`), and follow the documentation of the [rpy2] (http://rpy2.readthedocs.io/) library. In order to install R libraries into the virtualenv that Galaxy runs within, just add the name of the library into the [r-packages.txt file] (lib/galaxy/dependencies/r-packages.txt), and restart Galaxy ProTo.

Here follows an example (in the `execute()` method) that creates a `R` histogram plot as an extra file, linked to from the main HTML output file. (The example also makes use of the [HtmlCore] (#html-output) and [GalaxyRunSpecificFile] (#extra-output-files-linked-from-the-main-html-output) classes.):

```
from proto.HtmlCore import HtmlCore
from proto.RSetup import r
from proto.StaticFile import GalaxyRunSpecificFile

with open(galaxyFn, 'w') as outFile:
    core = HtmlCore()
    core.header('This is a header')

    myFile = GalaxyRunSpecificFile(['extra', 'histogram.png'], galaxyFn)
    path = myFile.getDiskPath(ensurePath=True)
    link = myFile.getLink('Link to histogram')

    r.png(path)
    numbers = [1,2,1,3,3,4,1,4,4,4,4,3,4,5,7,5,7,3,5,4,6,6,7,5,7,7,5,6]
    r.hist(numbers, breaks=xrange(0,8), main='Histogram', xlab='Some numbers')
    r('dev.off()')

    core.line(link)
    print>>outFile, core
```

#### More than one output history element
Galaxy ProTo supports the creation of more than one history element, as in this code snippet (**Note: As of version 0.9, this functionality is not operational. We are working on a fix.**):

```
class MyTool(GeneralGuiTool):
    EXTRA_OUTPUT_TITLE = 'Title of extra output'
    EXTRA_OUTPUT_FORMAT = 'bed'

    (...)

    @classmethod
    def getExtraHistElements(cls, choices):
        from proto.tools.GeneralGuiTool import HistElement
        return [HistElement(cls.EXTRA_OUTPUT_TITLE, cls.EXTRA_OUTPUT_FORMAT)]

    (...)

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):
        (...)
        extraOutFn = cls.extraGalaxyFn[cls.EXTRA_OUTPUT_TITLE]
        cls._writeSomethingToExtraOutput(extraOutFn)
        (...)
```

#### Storing state information
One should never store state information in class member variables for the GenericGuiTool subclasses. Class constants are allowed (with CAPITALIZED_NAMES), but these should not contain information that will change according to user input (i.e. not being used as a constant). Doing so defeats one of the core design strategies for the ProTo system, that all state information is stored in the prevChoices variables, and can have unforeseen consequences.

If you need to store state information for some reason (this will be very rare), you can use a hidden option box, e.g.:
```
return '__hidden__', myStateInfoAsStr`
```

You can retrieve the previous value of the hidden options box from the prevChoices namedtuple, e.g.
```
def getOptionsBoxHidden(prevChoices):
    if prevChoices.hidden is None:
    ...
```

#### Variable number of option boxes
In order to specify variable amounts of input boxes of the same type, a hack is possible:

```
class MyTool(GeneralGuiTool):
    MAX_NUM_OF_EXTRA_BOXES = 20
    (...)
    @classmethod
    def getInputBoxNames(cls):
    # Existing option boxes
      + [('Extra box number %s' % (i+1), 'extra%s' % i) for i \
         in range(cls.MAX_NUM_OF_EXTRA_BOXES)]
    (...)
    def _getOptionBoxExtra(cls, prevChoices, index):
        if index < numBoxes(prevChoices): #numBoxes is placeholder for some logic that returns the exact number of boxes
            #code for option box
            return #something

    @classmethod
    def setupExtraBoxMethods(cls):
        from functools import partial
        for i in xrange(cls.MAX_NUM_OF_EXTRA_BOXES):
            setattr(cls, 'getOptionsBoxExtra%s' % i, partial(cls._getOptionBoxExtra, index=i))
    (...)
    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):
        (...)
        extraChoices = [getattr(choices, 'extra%s' % i) \
                        for i in range(numBoxes(choices))]

(...)
MyTool.setupExtraMethods()
```

When the module (Python file) is first read, the `setupExtraMethods()` method is called, which sets
up `MAX_NUM_OF_EXTRA_BOXES` new option boxes. The code for each box is essentially similar to:

```
    @classmethod
    def getOptionsBoxExtra0(cls, prevChoices):
        return cls._methodForOptionsBox(prevChoices, index=0)
```

#### Use class constants to store selection box text
While one could hardcoded strings (e.g. of a selection box) directly in the return statements of a `getOptionsBox...()` method, one would later (typically in the execute method) have to check whether the user has selected something by checking against the same hardcoded sting. This might cause problems later on if one wants to change the text. Instead one should use use class constants.

Instead of hardcoding the strings, like this:
```
class MyTool(GeneralGuiTool):

    (...)

    @staticmethod
    def getOptionsBoxSelect(prevChoices):
        return ['The first choice', 'The second choice']

    (...)

    @staticmethod
    def execute(choices, galaxyFn=None, username=''):
        if choices.select == 'The first choice':
            # Do something
```

One should use class constants, like this:
```
class MyTool(GeneralGuiTool):
    SELECT_FIRST_CHOICE = 'The first choice'
    SELECT_SECOND_CHOICE = 'The second choice'

    (...)

    @classmethod
    def getOptionsBoxSelect(cls, prevChoices):
        return [cls.SELECT_FIRST_CHOICE, cls.SELECT_SECOND_CHOICE]

    (...)

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):
        if choices.select == cls.SELECT_FIRST_CHOICE:
            # Do something
```
If one want to change the text later, the change is thus done only one place.

#### Changing type of ProTo option box
**One should never dynamically change the type of a single option box (e.g. from text field to selection box)!** If such changes are needed, just specify two option boxes and hide the one that is not in use. See [Hide option box] (#hide-options-box).

#### CamelCase or snake_case?

For historical reasons, Galaxy ProTo is implemented using "camelCase" (or "mixedCase") styling for functions, member variables and methods, contrary to the recommended Python standard [PEP8] (https://www.python.org/dev/peps/pep-0008/), even though it is allowed ("allowed only in contexts where that's already the prevailing style (e.g. threading.py), to retain backwards compatibility."). As the superclass of new ProTo tools use "camelCase", the subclasses themselves also need to follow the "camelCase" standard. If there is enough interest in it, it might be possible create support for the snake_case style, but it has not been a priority until now.

## Known limitations

- Galaxy ProTo tools will not run as part of a Galaxy workflow. Support for this might be developed if the need is high, but it is not a priority right now, as Galaxy ProTo is envisioned first and foremost as a way to provide easy and dynamic interaction directly with the user.
- Galaxy ProTo works best connected to a PostgreSQL database (as recommended for [production Galaxy instances] (https://wiki.galaxyproject.org/Admin/Config/Performance/ProductionServer)). It will work out-of-the-box with the default SQLite database, but due to a basically unfixable deadlock issue, the user will experience significant waiting time when using the tools. Using SQLite, the opening of tools will once in a while fail and time out after 15 seconds, after which the tool reloads for another try. Because of this is it highly recommended to use PostgreSQL instead of SQLite.
- Galaxy ProTo has only been tested on Linux-based operating systems. It will probably also work on Mac OS X, and probably not on Windows.
- The "Run this job again" functionality of Galaxy will break for old history elements if the "proto_id_secret" configuration options is changed in the "galaxy.ini" file.
- ProTo tools are not supported in Galaxy Tool Shed, mainly because the API is an unofficial alternative to the Galaxy XML.
- Tested mainly with Chrome and Firefox web browsers.

## Version log

* v0.9.1: Small bugfixes and updates to the README.md.
* v0.9: Full functionality, but still with rests of HyperBrowser code to ble cleaned out.
