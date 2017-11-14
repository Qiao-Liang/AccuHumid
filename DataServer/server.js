var http = require('http');
var url = require('url');
var fs = require('fs');
var qs = require('querystring');
var client = require('mongodb').MongoClient;
var db_url = "mongodb://localhost:27017/local";

http.createServer(function (req, res) {
    var parsed_url = url.parse(req.url);

    switch(parsed_url.pathname) {
        case "/":
            fs.readFile('default.html', function(err, data) {
                if (err) throw err;
                
                res.writeHead(200, {'Content-Type': 'text/html'});
                res.write(data);
                res.end();
            });
            break;
        case "/temp_humid":
        case "/switch_log":
            client.connect(db_url, function(err, db) {
                if (err) throw err;

                try {
                    var query = {'dt': {}};
                    var params = qs.parse(decodeURIComponent(parsed_url.query));
                    if (params.srt) {
                        query['dt']['$gte'] = params.srt;
                    }
                    if (params.end) {
                        query['dt']['$lt'] = params.end;
                    }

                    db.collection(parsed_url.pathname.substring(1)).find(query).toArray(function(err, result) {
                        if (err) throw err;
                        res.writeHead(200, {'Content-Type': 'application/json'});
                        res.write(JSON.stringify(result));
                        db.close();
                        res.end();
                    });
                }
                catch (err) {
                    res.writeHead(500, {'Content-Type': 'text/html'});
                    res.end(err.message);
                }
            });
            break;
        default:
            res.writeHead(404, {'Content-Type': 'text/html'});
            res.end('404 Not Found');
    }

}).listen(8080);