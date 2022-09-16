function read_file(file_name){
    const {readFileSync} = require('fs');

    const contents = readFileSync(file_name, 'utf-8').toString();
    const rows = contents.split('\n');
    var list_of_points = new Array();
    for (let i = 0; i < rows.length; i++){
        const temp = rows[i].split(' ');
        var point = new Array()
        for (let j = 0; j < temp.length; j++){
            point[j] = (parseInt(temp[j]))
        }
        list_of_points[i] = point
    }
    return list_of_points
}