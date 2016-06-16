function Dshbrd() {
  this.get_cards = function(callback){
    site.plugin_api('dshbrd', 'get-cards', {}, callback);
  }
  this.search_events = function(term, callback){
    var rtm = new RTM();
    rtm.listen({
        collection: 'events',
        recipientID_type: "username",
        senderID_type: "username",
        sender_pair: ["Public", rtm.blank_sha512],
        recipient_pairs: [['Public', rtm.blank_sha512]],
        recipient_senders: ['Public'],
        where_sender: {'data.title': {'$regex': ".*" + term + "/*"}},
        backlog: true
    });
    rtm.ws.on('data_sent', function(data){
        callback(data);
    });
    rtm.ws.on('error', function(data){
      console.log(data);
    });
  }
  this.add_event = function(event){
    var rtm = new RTM();
    rtm.send({
        collection: 'events',
        senderID_type: 'username',
        recipientID_type: 'username',
        sender_pair: ["Public", rtm.blank_sha512],
        recipient: "Public",
        data: event
    });
    rtm.ws.on('error', function(data){
      console.log(data);
    });
  }
}

window.dshbrd = new Dshbrd();