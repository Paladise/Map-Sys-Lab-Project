export default class Sketch {
    constructor(vertex, fragment) {
        this.vertex = vertex;
        this.fragment = fragment;
        this.isPlaying = true;
        
        this.container = document.getElementById("rotatingSphere");
        this.width = this.container.offsetWidth;
        this.height = this.container.offsetHeight;
        
        this.renderer = new THREE.WebGLRenderer( { antialias: true, alpha: true } );
        this.renderer.setPixelRatio(window.devicePixelRatio); //get the correct pixel detail on portable devices
        this.renderer.setSize( this.width, this.height );
        this.renderer.setClearColor( 0x000000, 0 );
        this.renderer.outputEncoding = THREE.sRGBEncoding; // Lighter
        this.container.appendChild(this.renderer.domElement);
        
        this.renderer.shadowMap.enabled = true;
		this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    
        this.camera = new THREE.PerspectiveCamera( 70, window.innerWidth / window.innerHeight, 0.01, 50 );
        this.camera.position.set(3, 3, 3);
        this.controls = new THREE.OrbitControls(this.camera, this.renderer.domElement);
        this.controls.enabled = false;

        this.scene = new THREE.Scene();
        
        this.startProgress = 0.01;
        
        this.addMesh();
        this.resize();
        this.time = 0;
        this.render();
        this.setupResize();
        this.setupScroll();
        this.addLights();
    }
    
    setupResize() {
        window.addEventListener("resize", this.resize.bind(this));
    }
    
    setupScroll () {
        this.scrollY = window.scrollY;
        window.addEventListener('scroll', () =>
        {
            this.scrollY = window.scrollY;
            this.material.uniforms.progress.value = this.startProgress + scrollY / this.container.clientHeight / 2;
        })
    }
    
    resize() {
        this.width = this.container.offsetWidth;
        this.height = this.container.offsetHeight;
        this.renderer.setSize(this.width, this.height);
        this.camera.aspect = this.width / this.height;
        
        this.camera.updateProjectionMatrix();
    }
    
    addMesh() {
        this.geometry = new THREE.SphereGeometry(2, 32, 32);
        
        this.material = THREE.extendMaterial(THREE.MeshStandardMaterial, {
            class: THREE.CustomMaterial,
            
            vertexHeader: `
            attribute float aRandom;
            attribute vec3 aCenter;
            uniform float time;
            uniform float progress;
            
            mat4 rotationMatrix(vec3 axis, float angle) {
                axis = normalize(axis);
                float s = sin(angle);
                float c = cos(angle);
                float oc = 1.0 - c;
                
                return mat4(
                    oc * axis.x * axis.x + c,           oc * axis.x * axis.y - axis.z * s,  oc * axis.z * axis.x + axis.y * s,  0.0,
                    oc * axis.x * axis.y + axis.z * s,  oc * axis.y * axis.y + c,           oc * axis.y * axis.z - axis.x * s,  0.0,
                    oc * axis.z * axis.x - axis.y * s,  oc * axis.y * axis.z + axis.x * s,  oc * axis.z * axis.z + c,           0.0,
                    0.0,                                0.0,                                0.0,                                1.0
                );
            }
            
            vec3 rotate(vec3 v, vec3 axis, float angle) {
                mat4 m = rotationMatrix(axis, angle);
                return (m * vec4(v, 1.0)).xyz;
            }
            `,
            vertex: {
                transformEnd: `
                float prog = (position.y + 100.)/2.;
                float locprog = clamp((progress - 0.8*prog)/0.2, 0., 1.);
                
                locprog = progress;
                
                transformed = transformed - aCenter;
                // transformed += 1000.*normal *aRandom*(locprog);
                transformed += 2.*normal *aRandom*(locprog);
                
                transformed *= (1.-locprog);
                
                transformed += aCenter;
                transformed = rotate(transformed, vec3(0.0, 1.0, 0.0), aRandom*(locprog)*3.14*4.);
                `,
            },
            uniforms: {
                roughness: 0.75,
                time: {
                    mixed: true,
                    linked: true,
                    value: 0
                },
                progress: {
                    mixed: true,
                    linked: true,
                    value: this.startProgress
                }
            }
        });
        
        this.material.uniforms.diffuse.value = new THREE.Color(0xffffff);
        
        this.sphere = new THREE.Mesh(
            this.geometry,
            this.material 
        );
        
        this.scene.add(this.sphere);
        
        this.sphere.customDepthMaterial = THREE.extendMaterial(THREE.MeshDepthMaterial, {
            template: this.material
        }); 
        
        let geometry = this.sphere.geometry.toNonIndexed();
        geometry.computeBoundingBox();
        this.sphere.material = this.material;
        
        let len = geometry.attributes.position.count;
    
        let randoms = new Float32Array(len);
        let centers = new Float32Array(len * 3);
        for(let i = 0; i < len; i+=3) {
            let r = Math.random();
            randoms[i]= r;
            randoms[i+1] = r;
            randoms[i+2] = r;
            
            let x = geometry.attributes.position.array[i*3];
            let y = geometry.attributes.position.array[i*3 + 1];
            let z = geometry.attributes.position.array[i*3 + 2];
            
            let x1 = geometry.attributes.position.array[i*3 + 3];
            let y1 = geometry.attributes.position.array[i*3 + 4];
            let z1 = geometry.attributes.position.array[i*3 + 5];
            
            let x2 = geometry.attributes.position.array[i*3 + 6];
            let y2 = geometry.attributes.position.array[i*3 + 7];
            let z2 = geometry.attributes.position.array[i*3 + 8];
            
            let center = new THREE.Vector3(x, y, z).add(new THREE.Vector3(x1, y1, z1)).add(new THREE.Vector3(x2, y2, z2)).divideScalar(3);
        
            centers.set([center.x, center.y, center.z], i*3)
            centers.set([center.x, center.y, center.z], (i+1)*3)
            centers.set([center.x, center.y, center.z], (i+2)*3)
            
        }
        
        geometry.setAttribute("aRandom", new THREE.BufferAttribute(randoms, 1));     
        geometry.setAttribute("aCenter", new THREE.BufferAttribute(centers, 3));  
        
        this.sphere.geometry = geometry;
    }
	
	addLights() {
	    const hemiLight = new THREE.HemisphereLight( 0xffffff, 0x444444 );
		hemiLight.position.set(0, 20, 0);
		this.scene.add(hemiLight);
	}
	
	render() {
	    if (!this.isPlaying) return;
	    this.material.uniforms.time.value = this.time;
	    this.time++;
	    this.sphere.rotation.y += 0.002;
	    this.renderer.render( this.scene, this.camera );
	    window.requestAnimationFrame(this.render.bind(this));
	}
}

new Sketch();   