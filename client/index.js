var graphData = {{ data.chart_data | safe }}

var margin = {top: 30, right: 50, bottom: 30, left: 50};
var svgWidth = 600;
var svgHeight = 270;
var graphWidth = svgWidth - margin.left - margin.right;
var graphHeight = svgHeight - margin.top - margin.bottom;

var parseDate = d3.time.format("%Y-%m-%d").parse;