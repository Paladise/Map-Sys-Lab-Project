const x_midpoint = 443;
const y_midpoint = 389;

var scene, renderer, camera, controls;
renderer = new THREE.WebGLRenderer();
//this is to get the correct pixel detail on portable devices
renderer.setPixelRatio(window.devicePixelRatio);

//and this sets the canvas' size.
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
const axesHelper = new THREE.AxesHelper(200);
scene.add(axesHelper);

function addText(text, x, y, multiplier) {
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
        mesh.position.set((x - x_midpoint) * multiplier, (y_midpoint - y) * multiplier, 30);
        mesh.name = "text";
        scene.add(mesh);
    })
}

const extrudeSettings = {
    steps: 2,
    depth: 30,
    bevelEnabled: false
};

controls = new THREE.TrackballControls(camera, renderer.domElement);
controls.rotateSpeed = 0
camera.position.set(0, -400, 800);


window.addEventListener('change', function() {
    renderer.render(scene, camera);
}, false)

function animate() {
    requestAnimationFrame(animate);
    controls.update()
    scene.traverse (function (object)
{
    if (object instanceof THREE.Mesh) {
        if (object.name === "text") {
            object.quaternion.copy( camera.quaternion );
        }
    }
});
    renderer.render(scene, camera);
};

function addLines(points, multiplier) {
    let x1, y1, x2, y2, w
    x1 = points[0];
    y1 = points[1];
    x2 = points[2];
    y2 = points[3];
    w = points[4] + 1;
    const shape = new THREE.Shape();
    shape.moveTo((x1 - x_midpoint) * multiplier, (y_midpoint - y1) * multiplier);
    shape.lineTo((x2 - x_midpoint) * multiplier, (y_midpoint - y2) * multiplier);
    shape.lineTo((x2 - x_midpoint + w) * multiplier, (y_midpoint - y2) * multiplier);
    shape.lineTo((x1 - x_midpoint + w) * multiplier, (y_midpoint - y1) * multiplier);
    shape.lineTo((x1 - x_midpoint) * multiplier, (y_midpoint - y1) * multiplier);

    const geometry = new THREE.ExtrudeGeometry(shape, extrudeSettings);
    const material = new THREE.MeshBasicMaterial({
        color: 0xffffff
    });
    const mesh = new THREE.Mesh(geometry, material);
    scene.add(mesh);
}

function render_model(model) {
    const list_of_text = model.rooms;
    const list_of_points = model.points;
    
    for (let i = 0; i < list_of_text.length; i++) {
        addText(list_of_text[i][0], list_of_text[i][1], list_of_text[i][2], 2)
    }
    
    for (let i = 0; i < list_of_points.length; i++) {
        addLines(list_of_points[i], 2)
    }
    
    $('#loadingScreen').remove();
    
    animate();   
}