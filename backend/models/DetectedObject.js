const mongoose = require("mongoose");

const detectedObjectSchema = new mongoose.Schema({
    userId: {
        type: mongoose.Schema.Types.ObjectId,
        ref: "User",
    },
    objectType: {
        type: String,
        required: true,
    },
    position: {
        type: String,
        required: true,
    },
    confidenceScore: {
        type: Number,
        required: true,
    },
    image: {
        type: String,
        required: true,
    },
    createdAt: {
        type: Date,
        default: Date.now,
    },
});

const DetectedObject = mongoose.model("DetectedObject", detectedObjectSchema);
module.exports = DetectedObject;
