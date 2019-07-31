d3.json("data.json", function (error, graph) {
	console.log(graph);
	var rankSets = [
		{
			type: 'same',
			nodes: ['a', 'b'],
		}
	];

	// Set up SVG
	var svg = d3.select('svg');
	var width = +svg.attr('width');
	var height = +svg.attr('height');
	var margin = { top: 10, left: 50, bottom: 10, right: 50 };

	var i = -1;
	var layout = d3.sankey()
		.rankSets(rankSets)
		.extent([
			[margin.left, margin.top],
			[width - margin.left - margin.right, height - margin.top - margin.bottom]]);

	// Render
	var color = d3.scaleOrdinal(d3.schemeCategory10);
	var diagram = d3.sankeyDiagram()
		.linkColor(function (d) { return color(d.type); });

	layout(graph);
	svg
		.datum(graph)
		.call(diagram);

});
