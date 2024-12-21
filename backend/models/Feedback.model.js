const mongoose = require("mongoose");

const feedBackSchema = new mongoose.Schema({
    userId: {
        type: mongoose.Schema.Types.ObjectId,
        ref: "User",
    },
    feedbackText: {
        type: String,
        required: true,
    },
    rating: {
        type: Number,
        required: true,
    },
    resolved: {
        type: Boolean,
        default: false,
    },
    createdAt: {
        type: Date,
        default: Date.now,
    },
});
const Feedback = mongoose.model("Feedback", feedBackSchema);
module.exports = Feedback;