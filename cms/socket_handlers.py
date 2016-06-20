import os
import re
import time
import json

from flask import request, jsonify

from binascii import b2a_hex, a2b_hex
from hashlib import sha512

from bson.objectid import ObjectId
from pymongo.errors import DuplicateKeyError

from . import app, config, socket
from flask_socketio import emit, send
from .api import util, make_error_response, make_success_response, make_error

# SocketIO handlers that allow limited database access to the front end

# Object that represents a socket connection
class Socket:
    def __init__(self, sid, query):
        self.sid = sid
        self.query = query
        self.connected = True
        self.recipient_sender = query["recipient_sender"] \
                if "recipient_sender" in query else False
        self.where_recipient = query["where_recipient"]\
                if "where_recipient" in query else False,
        self.where_sender = query["where_sender"]\
                if "where_sender" in query else False

    # Emits data to a socket"s unique room
    def emit(self, event, data):
        emit(event, data, room=self.sid)

live_sockets = {"senders": {}, "recipients": {}}
all_listeners = {}

@socket.on("listen", namespace="/component")
def listen_handler(data):
    print(data)
    if not util.keys_exist([
                "backlog", "sender_pair", "collection", "recipient_pairs"
            ], data) or \
            len(data["sender_pair"]) != 2:
        return make_error("data_missing", "unknown")
    # convert usernames to ids if requested
    recipientID_type = data["recipientID_type"] if "recipientID_type"\
            in data else "id"
    if recipientID_type == "username":
        # convert recipient usernames to ids
        users = util.get_collection("users", db=util.config["auth_db"])
        for pair in data["recipient_pairs"]:
            recipient = users.find_one({"username": pair[0]})
            if recipient and len(recipient) > 0:
                pair[0] = str(recipient["_id"])
            else:
                return make_error("data_missing", "recipient")
    senderID_type = data["senderID_type"] if "senderID_type" \
            in data else "id"
    # send the user backlogs if requested
    if senderID_type == "username":
        # convert sender usernames to ids
        users = util.get_collection("users", db=util.config["auth_db"])
        sender = users.find_one({"username": data["sender_pair"][0]})
        if len(sender) > 0:
            data["sender_pair"][0] = str(recipient["_id"])
        else:
            # emit("error", "Sender username not found")
            return make_error("user_not_found")
    recipient_senders = []
    if "recipient_senders" in data:
        for sender in data["recipient_senders"]:
            recipient_senders.append(
                str(users.find_one({"username": sender})["_id"])
            )
        data["recipient_senders"] = recipient_senders
    # authenticate the data (and get a sneaky recipients list)
    auth, recipients = util.auth_listen(data)
    if not auth:
        return make_error("unknown_error", "no auth")
    # replace id searches with object id searches
    if "where_sender" in data:
        for clause in data["where_sender"]:
            if clause == "_id":
                data["where_sender"][clause] = ObjectId(
                    data["where_sender"][clause]
                )
    if "where_recipient" in data:
        for clause in data["where_recipient"]:
            if clause == "_id":
                data["where_recipient"][clause] = ObjectId(
                    data["where_recipient"][clause]
                )
    # send the user backlogs if requested
    if "backlog" in data and data["backlog"]:
        # get previously sent documents
        senders_log, recipients_log = util.get_documents(
            data["sender_pair"][0],
            recipients,
            data["collection"],
            time_order=True,
            recipient_senders=recipient_senders if recipient_senders else False,
            recipientID_type=recipientID_type,
            where_recipient=data["where_recipient"]\
                    if "where_recipient" in data else False,
            where_sender=data["where_sender"]\
                    if "where_sender" in data else False
        )
        for document in senders_log:
            if document["visible"]:
                document_tidy = {
                    "sender": document["sender"],
                    "recipient": document["recipient"],
                    "data": document["data"],
                    "id": str(document["_id"]),
                    "ts": document["ts"]
                }
                emit("data_sent", document_tidy)
        for document in recipients_log:
            if document["visible"]:
                document_tidy = {
                    "sender": document["sender"],
                    "recipient": document["recipient"],
                    "data": document["data"],
                    "id": str(document["_id"]),
                    "ts": document["ts"]
                }
                emit("data_received", document_tidy)
    # add socket to dict of sockets to keep updated
    # (Choosing speed over memory here)
    # create a socket object to represent us
    socket = Socket(request.sid, data)
    # add us to a list of all listener sockets
    live_sockets[socket.sid] = socket
    # make sure the list exists first
    if not data["sender_pair"][0] in live_sockets["senders"]:
        live_sockets["senders"][data["sender_pair"][0]] = []
    # append us to the list of senders subscribed to changes
    live_sockets["senders"][data["sender_pair"][0]].append(socket)
    # append us to a list of subscribers for each recipient we"re following
    for recipient in recipients:
        if not recipient in live_sockets["recipients"]:
            live_sockets["recipients"][recipient] = []
        live_sockets["recipients"][recipient].append(socket)

@socket.on("send", namespace="/component")
def send_handler(data):
    # validate data
    if not "sender_pair" in data or not "recipient" in data or \
            not "collection" in data or not "data" in data:
        return make_error(
            "unknown_error",
            "Invalid Arguments"
        )
    sender_pair = data["sender_pair"]
    recipient = data["recipient"]
    collection = data["collection"]
    message = data["data"]
    if "senderID_type" in data and data["senderID_type"] == "username":
        users = util.get_collection("users", db=util.config["auth_db"])
        user = users.find_one({"username": sender_pair[0]})
        if user:
            sender_pair[0] = str(user["_id"])
        else:
            return make_error(
                "unknown_error",
                "Sender username does not exist"
            )
    if "recipientID_type" in data and data["recipientID_type"] == \
            "username":
        users = util.get_collection("users", db=util.config["auth_db"])
        user = users.find_one({"username": recipient})
        if user:
            recipient = str(user["_id"])
            data["recipient"] = recipient
        else:
            return make_error(
                "unknown_error",
                "Recipient username does not exist"
            )
    # store document
    document = util.send(message, sender_pair, recipient, collection)
    if not document:
        return make_error(
            'unknown_error',
            "Data was not added to the DB for some reason"
        )
    # send Updates
    document_tidy = {
        "sender": document["sender"],
        "recipient": document["recipient"],
        "data": document["data"],
        "id": str(document["_id"]),
        "ts": document["ts"],
        "update": False
    }
    util.emit_to_relevant_sockets(data, document_tidy, live_sockets)

    #TODO: convert to make_success
    return {"success": True, "message": "Data was sent"}

@socket.on("update", namespace="/component")
def update_handler(data):
    print(data)
    # validate data
    if not "sender_pair" in data or not "document_id" in data or \
            not "collection" in data or not "data" in data:
        emit("error", "Invalid Arguments")
        return False
    sender_pair = data["sender_pair"]
    document_id = data["document_id"]
    collection = data["collection"]
    document = data["data"]
    # convert usernames to ids
    if "senderID_type" in data and data["senderID_type"] == "username":
        users = util.get_collection("users", db=util.config["auth_db"])
        user = users.find_one({"username": sender_pair[0]})
        if user:
            sender_pair[0] = str(user["_id"])
        else:
            emit("error", "Sender username does not exist")
            return False
    # update document
    document = util.update_document(
        document, sender_pair, document_id, collection
    )
    if not document:
        emit('error', make_error(
            'unknown_error',
            "Sender was not authenticated to make changes"
        ))
        return False
    # send Updates
    document_tidy = {
        "sender": document["sender"],
        "recipient": document["recipient"],
        "data": document["data"],
        "id": str(document["_id"]),
        "ts": document["ts"],
        "update": True
    }
    util.emit_to_relevant_sockets(data, document_tidy, live_sockets)
    emit("data_sent", "Data was updated")

@socket.on("disconnect")
def disconnect():
    # if socket is listening
    if request.sid in all_listeners:
        # remove from listeners
        all_listeners[request.sid].connected = False
        del all_listeners[request.sid]
