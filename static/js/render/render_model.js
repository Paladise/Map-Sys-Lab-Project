var path, model_json, scene, scene2, renderer, camera, controls, groups, visibility, group, insetwidth, insetheight, size, travel, pathPoints, pathPointsFloors, window_width;
var mainContainer, modelContainer, togglePanelBtn, navPanel, floorBtn, room1, room2, findPathButton, pauseText;
var roomsContainer, floorBtnContainer, findPathContainer, pauseContainer, floorHeading, numFloors, mid_x, mid_y;

const extrudeSettings = {
    steps: 2,
    depth: 30,
    bevelEnabled: false
};

const multiplier = 2; // Multiply size of rendered model

var n = 0; // Index of current camera position on path
var cam_count = 0

var lookahead = 15; // How far the camera looks ahead
var headPosition = 20; // How high the camera position is

var floorHeight = 50; // Distance between each floor
var textHeight = 40; // Distance from text to respective floor

// Wall texture
const texture = new THREE.TextureLoader().load( "/static/textures/plaster.jpg" ); // Hardcoded static path, should do it separately
texture.wrapS = THREE.RepeatWrapping;
texture.wrapT = THREE.RepeatWrapping;

function addText(text, x, y, group, floor, mid_x, mid_y) {
    /* Function to add text labels at certain locations */
    
    var loader = new THREE.FontLoader();
    loader.load('https://threejs.org/examples/fonts/optimer_regular.typeface.json', function(font) {

        var textGeo = new THREE.TextGeometry(text, {
            font: font,
            size: 20,
            height: 1,
        });
        var textMaterial = new THREE.MeshPhongMaterial({
            color: 0x000000,
            visible: true
        });
        
        // Create two meshes for text, one for bird-eye view camera and one for first-person view
        
        var mesh = new THREE.Mesh(textGeo, textMaterial);
        mesh.position.set((x - mid_x) * multiplier, (mid_y - y) * multiplier, floorHeight*floor+textHeight);
        mesh.name = "text1";
        mesh.layers.set(1);
        group.add(mesh);
        
        mesh = new THREE.Mesh(textGeo, textMaterial);
        mesh.position.set((x - mid_x) * multiplier, (mid_y - y) * multiplier, floorHeight+floor*textHeight);
        mesh.name = "text2";
        mesh.layers.set(2);
        group.add(mesh);
    });
};

function addLines(points, group, floor) {
    /* Function add walls at certain locations */
    
    let x1, y1, x2, y2, w;
    x1 = points[0];
    y1 = points[1];
    x2 = points[2];
    y2 = points[3];
    w = points[4] + 1;
    const shape = new THREE.Shape();
    shape.moveTo((x1 - mid_x) * multiplier, (mid_y - y1) * multiplier);
    shape.lineTo((x2 - mid_x) * multiplier, (mid_y - y2) * multiplier);
    shape.lineTo((x2 - mid_x + w) * multiplier, (mid_y - y2) * multiplier);
    shape.lineTo((x1 - mid_x + w) * multiplier, (mid_y - y1) * multiplier);
    shape.lineTo((x1 - mid_x) * multiplier, (mid_y - y1) * multiplier);
    
    const geometry = new THREE.ExtrudeGeometry(shape, extrudeSettings);
    const material = new THREE.MeshBasicMaterial({
        // color: 0xffffff
        map: texture
    });
    const mesh = new THREE.Mesh(geometry, material);
    mesh.castShadow = true;
    mesh.receiveShadow = true;
    mesh.position.set(0, 0, floor*floorHeight);
    group.add(mesh);
}

function changeFloor() {
    for (let i = 0; i < groups.length; i++) {
        groups[i].visible = false; // Hide every floor group
    }
    
    visibility = floorBtn.value;
    groups[floorBtn.value].visible = true; // Make that specific floor visible
}

function resize() {
    camera.aspect = window.innerWidth/window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight)

    insetwidth = window.innerWidth / 3;
    insetheight = window.innerHeight / 3;
    camera_first.aspect = insetwidth / insetheight;
    camera_first.updateProjectionMatrix();
}

function mouse_input() {
    var x = window.event.clientX;
    var y = window.event.clientY;
    if ((x>window_width - insetwidth - 16) && (y<window.innerHeight - insetheight - 16)){
        cam_count += 1;
    }
    else {
        if (travel) {
            travel = false;
            pauseText.style.visibility = "visible";
        } else if (path && n != path.length) {
            travel = true;
            pauseText.style.visibility = "hidden";
        }
    }
}

function toggle_panel() {
    navPanel.classList.toggle("collapsed");
    document.getElementsByClassName("menu")[0].classList.toggle("collapsed");
}

function createSnackbar(message) {
    var snackbar = document.createElement("div");
    snackbar.classList.add("snackbar");
    snackbar.innerHTML = message;
    document.body.appendChild(snackbar);
    
    setTimeout(function() {
        snackbar.remove();
    }, 3000);
}

var slowDown = 0;

function animate() {
    requestAnimationFrame(animate);
    controls.update();
    scene.traverse (function (object) {
        if (object instanceof THREE.Mesh) {
            if (object.name == "text1") {
                object.quaternion.copy( camera.quaternion );
            }
            if (object.name == "text2") {
                object.quaternion.copy( camera_first.quaternion );
            }
        }
    });
    renderer.setViewport(0, 0, window_width, window.innerHeight)
    renderer.render(scene, cameras[cam_count%2]);
    renderer.clearDepth();
    renderer.setScissorTest(true);
    renderer.setScissor(
        window_width - insetwidth - 16,
        window.innerHeight - insetheight - 16,
        insetwidth,
        insetheight,
    );
    renderer.setViewport(
        window_width - insetwidth - 16,
        window.innerHeight - insetheight - 16,
        insetwidth,
        insetheight,
    );
    renderer.render(scene, cameras[(cam_count+1)%2]);
    renderer.setScissorTest(false);
    
    // Move first person view camera
    
    if (travel && path) {
        if (n < path.length) {
            if (path[n][2] - 1 != floorBtn.value) { // If changing floors
                if(n != 0) {
                    var msgVal = "down";
                    if(path[n][2] - 1 > floorBtn.value) {
                        msgVal = "up";
                    }
                    createSnackbar("Walk " + msgVal + " the stairs");   
                }
                
                visibility = path[n][2]-1
                floorBtn.value = path[n][2]-1;
                changeFloor();
                travel = false;
            }
            pathPoints[n].material.color.setHex(0x045de9);
        }else {
            travel = false;
            createSnackbar("Arrived");
        }
        
        if (n < path.length-lookahead) {
            camera_first.position.set(path[n][0], path[n][1], headPosition+Math.sin(n/6)+(visibility)*floorHeight);
            camera_first.lookAt(path[n + lookahead][0], path[n + lookahead][1], headPosition+Math.sin(n/6)+(visibility)*floorHeight);
        }

        if(n > 1) {
            if(camera_first.rotation.x > 1) {
                camera_first.rotation.x = Math.PI / 2;
                camera_first.rotation.z = 0;
            }else {
                camera_first.rotation.x = -Math.PI / 2;
                camera_first.rotation.z = Math.PI;
            }
        }
        
        if(slowDown == 2) {
            n++;
            slowDown = 0;
        }else{
            slowDown++;
        }
        
    }
};

function render_model(model) {
    $('#loadingText').html("Rendering model...");
    
    //Get JSON model attributes
    numFloors = model["num_floors"];
    
    // Setting initial values
    
    visibility = 0;
    size = 20;
    travel = false;
    groups = new Array();
    model_json = model;
    window_width = window.innerWidth;
    
    // Create Three.js renderer
    
    renderer = new THREE.WebGLRenderer();
    renderer.setPixelRatio(window.devicePixelRatio); //get the correct pixel detail on portable devices
    renderer.setSize(window_width, window.innerHeight);
    renderer.setClearColor(0xefebd9, 1); // Default background color
    
    // Create Three.js scene
    
    scene = new THREE.Scene();
    
    // const axesHelper = new THREE.AxesHelper(400);
    // scene.add(axesHelper);
    
    // Bird eye view camera
    camera = new THREE.PerspectiveCamera(
        90, //FOV
        window.innerWidth / window.innerHeight, //aspect
        1, //near clipping plane
        5000 //far clipping plane
    );
    camera.layers.enable(1);
    camera.position.set(0, 0, 750); 
    camera.lookAt(0, 0, 0);
    
    // First person view camera
    
    camera_first = new THREE.PerspectiveCamera(
        90, //FOV
        window.innerWidth / window.innerHeight, //aspect
        1, //near clipping plane
        2500 //far clipping plane
    );
    camera_first.layers.enable(2);
    camera_first.position.set(0, 0, 10);
    camera_first.rotation.x = Math.PI / 2;
    camera_first.rotation.z = 0;
    
    const camera_first_helper = new THREE.CameraHelper(camera_first); // Show where first person view camera is
    scene.add(camera_first_helper);
    cameras = [camera, camera_first]
    // Connect to user interface
    
    mainContainer = document.getElementsByClassName("main-container")[0];
    
    navPanel = document.getElementsByClassName("nav-panel")[0];
    floorBtn = document.getElementsByClassName("floor-btn")[0];
    
    room1 = document.getElementsByClassName("room-input")[0];
    room2 = document.getElementsByClassName("room-input")[1];
    
    findPathButton = document.getElementsByClassName("find-path")[0];
    
    pauseContainer = document.getElementsByClassName("pause-container")[0];
    pauseText = document.getElementsByClassName("pause")[0];
    
    modelContainer = document.getElementsByClassName("model-container")[0];
    modelContainer.appendChild(renderer.domElement);
    
    togglePanelBtn = document.getElementById("togglePanel");

    // Allow camera to be maneuvered
    
    controls = new THREE.TrackballControls(camera, renderer.domElement);
    controls.rotateSpeed = 0; // Prevent camera rotation 
    
    // Create lights for environment
    
    const color = 0xFFFFFF;
    const intensity = 1.5;
    const light = new THREE.HemisphereLight( 0xffffff, 0xf7f8f9, 0.6  );
    light.position.set( 0, 0, 500 );
    scene.add( light );
    
    const connect = model["connect"];
   
    for (let i = 0; i < numFloors; i++) { // For each floor
        mid_x = connect[i][0];
        mid_y = connect[i][1];
        let list_of_text = model[(i + 1).toString()]["rooms"];
        let list_of_points = model[(i + 1).toString()]["points"];
        group = new THREE.Group();
        var newOption = document.createElement("option");
        newOption.setAttribute("value", i);
        node = document.createTextNode("Floor " + String(i + 1));
        newOption.appendChild(node);
        document.getElementById("currentFloor").appendChild(newOption);
        for (let j = 0; j < list_of_points.length; j++) {
            addLines(list_of_points[j], group, i);
        }
        for (let j = 0; j < list_of_text.length; j++) {
            addText(list_of_text[j][0], list_of_text[j][1], list_of_text[j][2], group, i, mid_x, mid_y);
        }
        // Create floor
        const plane_geometry = new THREE.PlaneGeometry( mid_x*20, mid_x*20 );
        const plane_material = new THREE.MeshBasicMaterial( {color: 0xeeeeee, side: THREE.DoubleSide} );
        const plane = new THREE.Mesh( plane_geometry, plane_material );
        plane_geometry.translate(0, 0, i*floorHeight)
        group.add(plane)
        scene.add(group);
        groups.push(group);
    }

    pathPoints = [];
    pathPointsFloors= [];
    
    for (let i = 0; i < groups.length; i++) {
        scene.add(groups[i]);
    }
    
    changeFloor();
    resize();
    animate();
    renderer.domElement.addEventListener("click", mouse_input);
    window.addEventListener("resize", resize);
    window.addEventListener("orientationchange", resize);
    if (screen.orientation) {
        screen.orientation.addEventListener("change", resize); // Mobile devices
    }
    
    setTimeout(() => {
      $('#loadingScreen').remove();
    }, 2000);
    
}