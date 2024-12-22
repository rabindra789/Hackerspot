const mongoose = require("mongoose");

const sessionSchema = new mongoose.Schema({
    userid: {
        type: mongoose.Schema.Types.ObjectId,
        ref: "User",
    },
    sessionId: {
        type: String,
        required: true,
    },
    userQuery: {
        type: String,
        required: true,
    },
    systemreponse: {
        type: String,
        required: true,
    },
    systemResponse: String,
    interactionContext: String,
    savedData: { 
        type: Object, 
        default: null 
    },
    createdAt: {
        type: Date,
        default: Date.now,
    },
});

const Session = mongoose.model("Session", sessionSchema);
module.exports = Session;
