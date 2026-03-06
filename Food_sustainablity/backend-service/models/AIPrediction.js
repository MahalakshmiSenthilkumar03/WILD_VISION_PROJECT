const mongoose = require('mongoose');

const AI_PredictionSchema = new mongoose.Schema({
    donorId: { type: mongoose.Schema.Types.ObjectId, ref: 'User', required: true },
    dateAnalyzed: { type: Date, default: Date.now },
    historicalDataPoints: { type: Number, default: 0 },
    dayOfWeek: { type: String },
    eventContext: { type: String },
    season: { type: String },
    predictedSurplusLbs: { type: Number, required: true },
    confidenceScore: { type: Number, required: true },
    predictionReasoning: { type: String },
}, { timestamps: true });

module.exports = mongoose.model('AIPrediction', AI_PredictionSchema);
