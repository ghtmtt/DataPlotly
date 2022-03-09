# Changelog

## Unreleased

- Fix "Build a generic plot" processing algorithm. Kudos to @agiudiceandrea
- Fix #237 add data-driven color to Polar Plot marker color. Kudos to @jmonticolo

## 3.9.0 - 2022-04-11

- Customize font for plot title and plot axis. Kudos to @giliam
- Support for Python 3.10

## 3.8.1 - 2021-09-28

- bugfix

## 3.8.0 - 2021-09-28

- [feature] expose DataPlotly on QGIS Server for a GetPrint request kudos to @Gustry

## 3.7.1 - 2020-05-15

- bugfix

## 3.7.0

- [feature] histogram and pie chart bar and slices with same color of category! kudos to @jdugge
- [feature] plot background transparent in layouts!

## 3.6.0

- [feature] Multi Plot in layout composer! Ultra kudos to @SGroe
- [bugfix] Fix layout composer issue with many plots (ref #207). Thanks to the Italian Community for testing
- [bugfix] Fix categorical bar plot wrong behavior 
- [bugfix] code cleaning
 
## 3.5.0

- [bugfix] Fix loading old projects

## 3.4.0

- [feature] get labels within the plot itself 
- [bugfix] Native datetime support! thanks @jdugge
- [bugfix] Fix histogram selection

## 3.3.0
 
- [bugfix] better loading project part 2

## 3.2.0
 
- [bugfix] fix violin plot bug
- [bugfix] better loading project handling

## 3.1.0

- [feature] more data defined options available (in layout customization). Thanks @SGroe 
- [feature] X and Y axis bounds limits. Thanks @SGroe
- [feature] add box plot within violin plots
- [feature] renaming of plugin metadata to better search. Thanks @Gustry
- [bugfix] Box plot not working when no group is selected 
- [bugfix] Data-defined property overrides do not work in layout

## 3.0.0
 
- [feature] total refactoring of the code
- [feature] plots also in print composer
- [feature] atlas based plots
- [feature] chance to save/load configuration file of plot setting
- [feature] plot settings saved together with the project
- [feature] more datadefined properties
- [feature] show only selected/visible/filtered features
- [feature] unit tests and continuous integration

## 2.3.0

- [feature] tweaks polar plots, thanks @josephholler

## 2.2.0

- [feature] UI tweaks, thanks @nyalldawson

## 2.1.0

- [fix] typos in UI (thanks @leonmvd and @nyalldawson)
- [fix] better python packages imports (thanks @nyalldawson)

## 2.0.0

- [feature] DataPlotly is updated with plotly 3.3 version

## 1.6.0

- [feature] wheel zoom! Give it a try
- [feature] Edit plot title and X/Y labels in place

## 1.5.1

- [feature] Spanish translation. Special thanks to Luca Bellani
- [bugfix] always open English manual if locale not translated

## 1.5.0

- [feature] **new** Violin plots!
- [feature] **new** Polar plot layout!
- [feature] better default color choice

## 1.4.3

- [bugfix] correct interaction with pie plot
- update plotly.js to v 1.34.0

## 1.4.2

- [bugfix] correct saving html plot

## 1.4.1

- [bugfixing] adaptation for new API

## 1.4.0

- [feature] update plotly.js to v 1.33.1
- [feature] multiple selection with Shift + selection tool
- [feature] DataPlotly as Processing provider, thanks to Michaël Douchin of 3Liz
