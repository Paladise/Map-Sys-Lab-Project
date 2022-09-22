const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera( 75, window.innerWidth / window.innerHeight, 0.1, 1000 );

const renderer = new THREE.WebGLRenderer();
renderer.setSize( window.innerWidth, window.innerHeight );
document.body.appendChild( renderer.domElement );
const loader = new THREE.FileLoader();
// loader.load('list_of_points.txt')
THREE.Cache.enabled = true;
const list_of_points = [[2, 2, 0], [1, 2, 0], [0, 0, 0], [1, 0, 0], [2, 0, 0], [2, 2, 0], [2, 1, 0], [0, 1, 0], [0, 2, 0]];
// first parameter will be the size of map in pixels
// other parameters will be [x, y, z] although we might not need z later
var x, y, z;
x = list_of_points[0][0];
y = list_of_points[0][1];
z = list_of_points[0][2];
for (let i = 1; i < list_of_points.length; i++){
    const geometry = new THREE.BoxGeometry( 1, 1, 1 );
    geometry.translate(list_of_points[i][0]-(x/2), list_of_points[i][1]-(y/2), list_of_points[i][2]);
    const material = new THREE.MeshBasicMaterial( { color: 0xe3e19f } );
    const cube = new THREE.Mesh( geometry, material );
    cube.rotation.x = -.25;
    scene.add( cube );
}
// camera.position.z = x*y;
camera.position.z = 1000;

function animate() {
    requestAnimationFrame( animate );
    renderer.render( scene, camera );
};

animate();
var controls = new THREE.OrbitControls( camera, renderer.domElement );
controls.rotateSpeed = .5;
controls.enableDamping = true;
controls.dampingFactor = .05;

window.addEventListener( 'resize', function () {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize( window.innerWidth, window.innerHeight );
}, false )

animate();