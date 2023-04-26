function createNewPath(newPath) {
    createSnackbar("Calculated path");
    
    path = newPath;
    
    for(let i = 0; i < pathPoints.length; i++) {
        groups[pathPointsFloors[i]].remove(pathPoints[i]);
    }
    
    pathPoints = [];
    pathPointsFloors = [];
    
    for(let i = 0; i < path.length; i++) {
        var dotGeometry = new THREE.BufferGeometry();
        dotGeometry.setAttribute('position', new THREE.BufferAttribute(new Float32Array([path[i][0], path[i][1], (path[i][2]-1)*floorHeight]), 3));
        var dotMaterial = new THREE.PointsMaterial({ size: 1, color: 0x09c6f9 });
        var dot = new THREE.Points(dotGeometry, dotMaterial);
        pathPoints.push(dot);
        pathPointsFloors.push(path[i][2]-1);
        groups[path[i][2]-1].add(dot);
    }
    for (let i=0; i<groups.length; i++) {
        scene.remove(groups[i]);
        scene.add(groups[i]);
    }
    changeFloor();
    
    n = 0;
    camera_first.position.set(path[0][0], path[0][1], path[0][2]*floorHeight+headPosition);
}