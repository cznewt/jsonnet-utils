var g = new dagreD3.graphlib.Graph().setGraph({});

g.setGraph({
    nodesep: 20,
    ranksep: 50,
    rankdir: "LR",
    marginx: 50,
    marginy: 10
});

function colorNode(name) {
    var node = d3.selectAll(".node")[0].filter(function (d) {
        return d3.select(d).data()[0].name == name;
    });
    d3.selectAll(node).style("fill", "red");
}

function colorLink(src, tgt) {
    var link = d3.selectAll(".edgePath")[0].filter(function (d) {
        return (d3.select(d).data()[0][0].name == src && d3.select(d).data()[0][2].name == tgt);
    });
    d3.selectAll(link).style("stroke", "red");
}

d3.json("data.json", function (error, graph) {
    if (error) throw error;

    graph.nodes.forEach(function (node) {
        //console.log(node.id);
        if (node.type == 'prometheus-metric') {
            style = "fill: #ffeba7; opacity: 0.9";
        }
        else if (node.type == 'prometheus-alert') {
            style = "fill: #c0e3f7; opacity: 0.9";
        }
        else if (node.type == 'prometheus-record') {
            style = "fill: #c6e7ab; opacity: 0.9";
        }
        else if (node.type == 'grafana-dashboard') {
            style = "fill: #a2d876; opacity: 0.9";
        }
        else if ((node.type == 'input') || (node.type == 'output')) {
            style = "opacity: 0";
        }
        else {
            style = "fill: #fff";
        }

        g.setNode(node.id, { label: node.name, style: style });
    });

    graph.links.forEach(function (link) {
        if ((link.source == 'input') || (link.target == 'output')) {
            style = "opacity: 0";
        }
        else {
            style = "opacity: 0.9";
        }
        //console.log(link.source + '-' + link.target);
        g.setEdge(link.source, link.target, { label: "", style: style });
    });

    // Set some general styles
    g.nodes().forEach(function (v) {
        var node = g.node(v);
        //console.log(node);
        node.rx = node.ry = 5;
    });

    g.edges().forEach(function (e) {
        var edge = g.edge(e);
    });

    var svg = d3.select("svg"),
        inner = svg.select("g");

    svg.selectAll(".node rect").enter()
        .on("mouseover", function (d) {
            //first make all the nodes/links black (reset).
            console.log(d);
            d3.selectAll(".node").style("fill", "black");
            d3.selectAll(".edgePath").style("stroke", "steelblue");
            //color the node which is hovered.
            colorNode(d.name);
            //iterate over the imports which is the targets of the node(on which it is hovered) and color them.
            d.imports.forEach(function (name) {
                //colorNode(name);
                //color the link for a given source and target name.
                colorLink(d.name, name);
            });
        })

    // Set up zoom support
    var zoom = d3.zoom().on("zoom", function () {
        inner.attr("transform", d3.event.transform);
    });
    svg.call(zoom);

    // Create the renderer
    var render = new dagreD3.render();

    // Run the renderer. This is what draws the final graph.
    render(inner, g);

    // Center the graph
    var initialScale = 0.75;
    svg.call(zoom.transform, d3.zoomIdentity.translate((svg.attr("width") - g.graph().width * initialScale) / 2, 20).scale(initialScale));

    svg.attr('height', g.graph().height * initialScale + 40);

});
