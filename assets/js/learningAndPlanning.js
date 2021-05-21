import { initialiseFromStorage, saveToStorage } from "./utils.js";


const learnedNodesString = "learnedNodes";
const goalNodesString = "goalNodes";
var learnedNodes = initialiseFromStorage(learnedNodesString);
var goalNodes = initialiseFromStorage(goalNodesString);
var pathNodes = {};

function nodeLearned(node) {
    learnedNodes[node.data().id] = true;
    node.addClass("learned");
    node.style("opacity", 1);
}

function checkEdgeLearned(edge) {
    if (edge.source().classes().includes("learned") && edge.target().classes().includes("learned")) {
        edge.addClass("learned");
        edge.style("opacity", 1);
    } else {
        edge.removeClass("learned");
    }
}

function onLearnedSliderClick(node) {
    return function () {
        let nodeId = node.data().id;
        if (!(nodeId in learnedNodes)) {  // Not learned
            nodeLearned(node);
            // Deal with predecessors
            node.predecessors("node").forEach(function(node) {
                nodeLearned(node);
            });
            node.predecessors("edge").forEach(function(edge) {
                checkEdgeLearned(edge);
            });
        } else {  // Learned or set as unknown
            node.toggleClass("learned");
            // Deal with edges
            node.connectedEdges().forEach(function(edge) {
                checkEdgeLearned(edge);
            });
        }
        saveToStorage(learnedNodesString, learnedNodes);
    }
}

function setPath(node) {
    let path = node.predecessors().not(".goal").not(".path");
    path.addClass("path");
    path.nodes().forEach(function(node) {
        pathNodes[node.data().id] = true;
        node.style("opacity", 1);
    });
    path.edges().forEach(function(edge){
        edge.style("opacity", 1);
    });
}

function setGoal(node) {
    goalNodes[node.data().id] = true;
    node.addClass("goal");
    node.removeClass("path");
    node.style("opacity", 1);
    setPath(node);
}

function unsetGoal(node) {
    delete goalNodes[node.data().id];
    node.removeClass("goal");

    // Remove this goal's path
    let path = node.predecessors().not(".goal");
    path.removeClass("path");
    path.nodes().forEach(function(node) {
        delete pathNodes[node.data().id];
    });
    // Ensure all other goals have correct paths
    for (const goalId in goalNodes) {
        setPath(cy.nodes(`[id = "${goalId}"]`));
    }
}


function onSetGoalSliderClick(node) {
    return function () {
        let nodeId = node.data().id;

        // If not already set!
        if (!(nodeId in goalNodes)){
            // Set goal to class goal and unknown dependencies to class: path
            setGoal(node);
        } else {
            // If unsetting a goal, remove path from its predecessors and recalculate path to remaining goals
            unsetGoal(node);
        }
        saveToStorage(goalNodesString, goalNodes);
    }
}

function initialiseGraphState() {
    for (const nodeId in learnedNodes) {
        let node = cy.nodes("[id = '" + nodeId + "']");
        if (learnedNodes[nodeId]) {
            nodeLearned(node);
            node.connectedEdges().forEach(function(edge) {
                checkEdgeLearned(edge);
            });
        }
    }
    for (const nodeId in goalNodes) {
        let node = cy.nodes("[id = '" + nodeId + "']");
        setGoal(node);
    }
}

export {onLearnedSliderClick, learnedNodes, onSetGoalSliderClick, goalNodes, pathNodes, initialiseGraphState}
