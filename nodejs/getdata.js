var mysql = require('mysql');
 
var connection = mysql.createConnection(
    {
      host     : 'localhost',
      user     : 'root',
      password : 'eves1981',
      database : 'node_db',
    }
);
 
connection.connect();
 
var queryString = 'SELECT * FROM products';
 
connection.query(queryString, function(err, rows, fields) {
    if (err) throw err;
 
    for (let i in rows) {
        console.log('Post Titles: ', rows[i].item_code);
        console.log('Post quantity: ', `${rows[i].item_quantity}`);
        
    }
});

let x = [1,2,3,4,5,6,8,9,10,12,100,20];

console.log(x.filter(function (val) {
    return val % 2 == 0
}))

console.log(x.map(function(v, k){
    if (v % 2 == 0)
        return {index:k, value:v*2}
    else
        return {index:k, value:v}
}))

console.log(x)

console.log('Closing connection!')
connection.end();