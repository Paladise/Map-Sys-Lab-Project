from flask import Flask

app = Flask(__name__)

@app.route("/")
def hello_world():
    return """<!DOCTYPE html>
<html>
	<head>
		<meta charset="utf-8">
		<title>My first three.js app</title>
		<style>
			body { margin: 0; }
		</style>
		</script>
	</head>
	<body>
		<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r83/three.js"></script>
        <script type="module">
			const scene = new THREE.Scene();
			const camera = new THREE.PerspectiveCamera( 75, window.innerWidth / window.innerHeight, 0.1, 1000 );

			const renderer = new THREE.WebGLRenderer();
			renderer.setSize( window.innerWidth, window.innerHeight );
			document.body.appendChild( renderer.domElement );
			const loader = new THREE.FileLoader();
			THREE.Cache.enabled = true;
			loader.load('list_of_points.txt', function(data){console.log(data)});
            const list_of_points = [[1, 2, 0], [0, 0, 0], [1, 0, 0], [2, 0, 0], [2, 2, 0], [2, 1, 0], [0, 1, 0], [0, 2, 0]];

			for (let i = 0; i < list_of_points.length; i++){
				const geometry = new THREE.BoxGeometry( 1, 1, 1 );
				geometry.translate(list_of_points[i][0], list_of_points[i][1], list_of_points[i][2]);
				const material = new THREE.MeshBasicMaterial( { color: 0xe3e19f } );
				const cube = new THREE.Mesh( geometry, material );
				cube.rotation.x = -.25;
				scene.add( cube );
			}
			camera.position.z = 10;
			camera.position.y = 1;
			camera.position.x = 1;

			function animate() {
				requestAnimationFrame( animate );
				renderer.render( scene, camera );
			};

			animate();
		</script>
	</body>
</html>"""

@app.route("/list_of_points.txt")
def points():
    return "0 0 0"

if __name__ == "__main__":
    app.run(debug=True)