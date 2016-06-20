function RTM(url){
    this.url = url || "/"

    // Connect to socketserver
    this.ws = io.connect(this.url);
    this.handlers = [];
    this.listening = [];

    // This is just sha512(sha512("")). Don't trip, yo.
    this.blank_sha512 =
      "8fb29448faee18b656030e8f5a8b9e9a695900f36a3b7d7ebb0d9d51e06c8569" +
      "d81a55e39b481cf50546d697e7bde1715aa6badede8ddc801c739777be77f166"

    this.keys_exist = function(keys, obj){
        for (var i in keys){
            var key = keys[i];
            if (obj[key] == undefined){
                return false;
            }
        }
        return true;
    }

    // Tells the server to listen for database changes and send them to us
    this.listen = function(conf, callback) {
        if (!this.keys_exist([
                    'collection', 'sender_pair', 'recipient_pairs', 'backlog'
                ], conf)){
            return false;
        }
        // emit request
        this.ws.emit('listen', conf, function(data) {
          console.log(data);
          if (typeof callback !== "undefined") {
            callback(data);
          }
        });
        this.listening.push(conf);
    }

    this.send = function(conf, callback) {
        if (!this.keys_exist([
                    'collection', 'sender_pair', 'recipient', 'data'
                ], conf)){
            return false;
        }
        this.ws.emit('send', conf, function(data) {
          console.log(data);
          if (typeof callback !== "undefined") {
            callback(data);
          }
        });
    }

    this.update = function(conf, callback) {
        if (!this.keys_exist([
                    'collection', 'sender_pair', 'document_id', 'data'
                ], conf)){
            return false;
        }
        this.ws.emit('update', conf, function(data) {
          console.log(data);
          if (typeof callback !== "undefined") {
            callback(data);
          }
        });
    }

    this.ws.on("connect", function() {
      $.each(function(key, value) {
        this.listen(value);
      })
    })

    //
}
