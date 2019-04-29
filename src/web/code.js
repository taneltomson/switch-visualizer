var cy = cytoscape({
  container: document.getElementById('cy'),

  boxSelectionEnabled: false,
  autounselectify: true,

  style: cytoscape.stylesheet()
    .selector('node')
      .css({
        'content': 'data(id)',
        'text-valign': 'center',
        'color': 'white',
        'text-outline-width': 2,
        'text-outline-color': '#000',
        'background-color': '#ccc',
        'width': '120%',
      })
    .selector(':selected')
      .css({
        'background-color': 'black',
        'line-color': 'black',
        'target-arrow-color': 'black',
        'source-arrow-color': 'black',
        'text-outline-color': 'black'
      })
    .selector('edge')
      .css({
      'font-size': '10px',
      'target-label': 'data(targetPort)',
      'source-label': 'data(sourcePort)',
      'edge-text-rotation': 'autorotate',
      'target-text-offset': '90px',
      'source-text-offset': '90px',
      'width': 2,
      'line-color': '#ccc'
      }),

  elements: elements_data,

  layout: {
    name: 'breadthfirst',

    fit: true, // whether to fit the viewport to the graph
    directed: false, // whether the tree is directed downwards (or edges can point in any direction if false)
    padding: 30, // padding on fit
    circle: false, // put depths in concentric circles if true, put depths top down if false
    spacingFactor: 1.2, // positive spacing factor, larger => more space between nodes (N.B. n/a if causes overlap)
    boundingBox: undefined, // constrain layout bounds; { x1, y1, x2, y2 } or { x1, y1, w, h }
    avoidOverlap: true, // prevents node overlap, may overflow boundingBox if not enough space
    nodeDimensionsIncludeLabels: true, // Excludes the label when calculating node bounding boxes for the layout algorithm
    roots: undefined, // the roots of the trees
    maximalAdjustments: 0, // how many times to try to position the nodes in a maximal way (i.e. no backtracking)
    animate: false, // whether to transition the node positions
    ready: onCytoscapeReadyEvent, // callback on layoutready
    stop: undefined, // callback on layoutstop
    transform: function (node, position ){ return position; } // transform a given node position. Useful for changing flow direction in discrete layouts
  }
});

var saveLayoutWhenLeaving = true;

// Set listener for the button that resets the layout
document.getElementById("resetBtn").addEventListener("click", function() {
    localStorage.removeItem('graphLayout');
    console.log('Layout removed.');

    console.log('Reloading page.');
    saveLayoutWhenLeaving = false;
    location.reload();
});

function onCytoscapeReadyEvent(event) {
    // TODO: Check file hashes

    restoreSavedLayoutOnReadyEvent(event);
}

function restoreSavedLayoutOnReadyEvent(event) {
    var storedLayout = localStorage.getItem('graphLayout');

    if (storedLayout != null) {
        event.cy.json(JSON.parse(storedLayout));
        console.log('Layout restored!');
    }
}

function savePageLayout(){
    if (saveLayoutWhenLeaving) {
        localStorage.setItem('graphLayout', JSON.stringify(cy.json()));
    }
    return null;
}

// Set the listener that saves page layout when user refreshes or closes the page.
window.onbeforeunload = savePageLayout;

// Add tooltips to graph nodes
cy.nodes().forEach(function(node) {
    console.log("Adding tooltip to node", node.id());

    var tippyItem = tippy(node.popperRef(), {
        content: function() {
            var br = '<br />';

            for (var i in elements_data['nodes']) {
                if (elements_data['nodes'][i]['data']['id'] == node.id()) {
                    var nodeData = elements_data['nodes'][i]['data']

                    var text = '';
                    text += nodeData['id'] + br;
                    text += br;
                    text += 'Other devices:' + br;

                    for (var j in nodeData['otherDevices']) {
                        var otherDevice = nodeData['otherDevices'][j];
                        text += otherDevice['sysName'] + ' (' + otherDevice['address'] + ')' + br
                    }

                    break;
                }
            }

            return text;
        },
        placement: 'bottom', // prefer bottom - will use above when no space
        trigger: 'manual', // we'll programmatically show and hide the tooltip
        hideOnClick: false, // messes things up if on true
        sticky: true, // keep tooltips near nodes
        theme: 'translucent',
        interactive: true, // allow text selection on tooltips
    });

    // toggle tooltip visibility when tapping nodes
    node.on('tap', function(evt) {
        if (tippyItem.state.isVisible) {
            tippyItem.hide();
        } else {
            tippyItem.show();
        }
    });
});
