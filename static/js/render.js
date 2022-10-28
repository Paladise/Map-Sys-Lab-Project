var scene, renderer, camera, controls, groups, visibility, group;

function addText(text, x, y, multiplier, group, floor) {
    var loader = new THREE.FontLoader();
    loader.load('https://threejs.org/examples/fonts/optimer_regular.typeface.json', function(font) {

        var textGeo = new THREE.TextGeometry(text, {
            font: font,
            size: 20,
            height: 1,
        });
        var textMaterial = new THREE.MeshBasicMaterial({
            color: 0x000000,
            visible: true
        });
        var mesh = new THREE.Mesh(textGeo, textMaterial);
        mesh.position.set((x - 578) * multiplier, (567 - y) * multiplier, 30+floor*100);
        mesh.name = "text";
        group.add(mesh);
    })
};

const extrudeSettings = {
    steps: 2,
    depth: 30,
    bevelEnabled: false
};

function addLines(points, multiplier, group, floor) {
    let x1, y1, x2, y2, w
    x1 = points[0];
    y1 = points[1];
    x2 = points[2];
    y2 = points[3];
    w = points[4] + 1;
    const shape = new THREE.Shape();
    shape.moveTo((x1 - 578) * multiplier, (567 - y1) * multiplier);
    shape.lineTo((x2 - 578) * multiplier, (567 - y2) * multiplier);
    shape.lineTo((x2 - 578 + w) * multiplier, (567 - y2) * multiplier);
    shape.lineTo((x1 - 578 + w) * multiplier, (567 - y1) * multiplier);
    shape.lineTo((x1 - 578) * multiplier, (567 - y1) * multiplier);

    const geometry = new THREE.ExtrudeGeometry(shape, extrudeSettings);
    const material = new THREE.MeshBasicMaterial({
        color: 0xffffff
    });
    const mesh = new THREE.Mesh(geometry, material);
    mesh.position.set(0, 0, floor*100);
    group.add(mesh);
};

function changeFloor(){
    groups[visibility].visible = false
    visibility = btn.value
    groups[btn.value].visible = true
};

visibility = 0;
let btn = document.createElement("select");
groups = new Array();
btn.add = "Floor 1";
btn.add = "Floor 2";
btn.setAttribute("id", "currentFloor")
btn.setAttribute("name", "Floor")
document.body.appendChild(btn);
btn.addEventListener("change", changeFloor)

renderer = new THREE.WebGLRenderer();
//this is to get the correct pixel detail on portable devices
renderer.setPixelRatio(window.devicePixelRatio);

renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setClearColor(0xefebd9, 1);
document.body.appendChild(renderer.domElement);

scene = new THREE.Scene();

camera = new THREE.PerspectiveCamera(
    90, //FOV
    window.innerWidth / window.innerHeight, //aspect
    1, //near clipping plane
    2500 //far clipping plane
); 

for (var i=0; i<2; i++){
    group = new THREE.Group();
    var newOption = document.createElement("option");
    newOption.setAttribute("value", i)
    node = document.createTextNode("Floor " + String(i+1))
    newOption.appendChild(node)
    document.getElementById("currentFloor").appendChild(newOption);
    for (let j = 0; j < list_of_points[i].length; j++) {
        addLines(list_of_points[i][j], 2, group, i)
    }
    for (let j = 0; j < list_of_text[i].length; j++){
        addText(list_of_text[i][j][0], list_of_text[i][j][1], list_of_text[i][j][2], 2, group, i)
    }
    scene.add(group)
    if (i!=0){
        group.visible = false
    }
    groups.push(group)
}


controls = new THREE.TrackballControls( camera, renderer.domElement );
// controls.rotateSpeed = 0
camera.position.set(0, -400, 800);

function animate() {
    requestAnimationFrame(animate);
    controls.update()
    scene.traverse (function (object)
{
    if (object instanceof THREE.Mesh) {
        if (object.name == "text") {
            object.quaternion.copy( camera.quaternion );
        }
    }
});
    renderer.render(scene, camera);
};

animate();