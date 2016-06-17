function Dshbrd() {
  this.get_cards = function(callback){
    site.plugin_api('dshbrd', 'get-cards', {}, callback);
  }
  // subscribes to a list of all events matching a regex
  this.search_events = function(term, callback){
    var rtm = new RTM();
    rtm.listen({
        collection: 'events',
        recipientID_type: "username",
        senderID_type: "username",
        sender_pair: ["Public", rtm.blank_sha512],
        recipient_pairs: [['Public', rtm.blank_sha512]],
        recipient_senders: ['Public'],
        where_sender: {'data.title': {'$regex': ".*" + term + ".*"}},
        backlog: true
    });
    rtm.ws.on('data_sent', function(data){
        callback(data, rtm);
    });
    return rtm;
  }
  // adds an event
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
    return rtm;
  }
  // updates the data on an event
  this.update_event = function(event_id, update){
    var rtm = new RTM();
    rtm.update({
        document_id: event_id,
        sender_pair: ["Public", rtm.blank_sha512],
        collection: 'events',
        data: update,
        senderID_type: "username"
    });
    return rtm;
  }
  // starts listening for updates on a single event
  this.get_event_updates = function(event_id){
    var rtm = RTM();
    rtm.listen({                                                     
      collection: 'events',
      recipientID_type: "username",
      senderID_type: "username",
      sender_pair: ["Public", rtm.blank_sha512],
      recipient_pairs: [['Public', rtm.blank_sha512]],
      recipient_senders: ['Public'],
      where_recipient: {'_id': event_id},
      backlog: false
    });
    return rtm;
  }
}

window.dshbrd = new Dshbrd();
