/**
 * Haversine formula to find distance between two points in km
 */
const calculateDistance = (lat1, lon1, lat2, lon2) => {
    const p = 0.017453292519943295;    // Math.PI / 180
    const c = Math.cos;
    const a = 0.5 - c((lat2 - lat1) * p) / 2 +
        c(lat1 * p) * c(lat2 * p) *
        (1 - c((lon2 - lon1) * p)) / 2;

    return 12742 * Math.asin(Math.sqrt(a)); // 2 * R; R = 6371 km
};

/**
 * Dijkstra's Shortest Path Algorithm
 * @param {Object} graph - Adjacency list representing coordinates or node IDs with distances { nodeA: { nodeB: 5, nodeC: 2 } }
 * @param {String} startNode
 * @param {String} endNode
 */
const dijkstraRoute = (graph, startNode, endNode) => {
    const distances = {};
    const previous = {};
    const unvisited = new Set(Object.keys(graph));

    for (let node in graph) {
        distances[node] = Infinity;
        previous[node] = null;
    }
    distances[startNode] = 0;

    while (unvisited.size > 0) {
        let currentNode = null;
        let shortestDist = Infinity;

        // Find unvisited node with smallest distance
        for (let node of unvisited) {
            if (distances[node] < shortestDist) {
                shortestDist = distances[node];
                currentNode = node;
            }
        }

        if (currentNode === null) break;
        if (currentNode === endNode) break;

        unvisited.delete(currentNode);

        for (let neighbor in graph[currentNode]) {
            if (unvisited.has(neighbor)) {
                const newDist = distances[currentNode] + graph[currentNode][neighbor];
                if (newDist < distances[neighbor]) {
                    distances[neighbor] = newDist;
                    previous[neighbor] = currentNode;
                }
            }
        }
    }

    // Build path
    const path = [];
    let current = endNode;
    while (current !== null) {
        path.unshift(current);
        current = previous[current];
    }

    if (path[0] === startNode) {
        return { distance: distances[endNode], path };
    } else {
        return { distance: Infinity, path: [] }; // No path
    }
};

module.exports = {
    calculateDistance,
    dijkstraRoute
};
