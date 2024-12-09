from flask import Flask, request, jsonify
from google.cloud import aiplatform
import os

app = Flask(__name__)

# Vertex AI configurations
PROJECT_ID = "453150507971"  # Replace with your Google Cloud project ID
LOCATION = "us-central1"        # Replace with your model's region (e.g., "us-central1")
ENDPOINT_ID = "4126081210461978624"  # Replace with your Vertex AI endpoint ID
CLIENT_OPTIONS = {"api_endpoint": f"{LOCATION}-aiplatform.googleapis.com"}

# Initialize the Prediction Service Client
prediction_client = aiplatform.gapic.PredictionServiceClient(client_options=CLIENT_OPTIONS)

# Scorer function
def scorer(prompts):
    sentiments = ['positive', 'neutral', 'negative']

    # Call Vertex AI to get predictions
    endpoint = f"projects/{PROJECT_ID}/locations/{LOCATION}/endpoints/{ENDPOINT_ID}"

    try:
        response = prediction_client.predict(
            endpoint=endpoint,
            instances=[{"input_text": prompt} for prompt in prompts]
        )

        # Extract logits from response
        logits = response.predictions  # Assuming predictions return logits
        sentiment_scores = []

        for i, prompt_logits in enumerate(logits):
            probabilities = torch.softmax(torch.tensor(prompt_logits), dim=-1)
            sentiments_prob = [probabilities[tokenizer.convert_tokens_to_ids(s)].item() for s in sentiments]

            # Standardized Positive - Standardized Negative
            sentiment_score = (sentiments_prob[0] - sentiments_prob[2]) / sum(sentiments_prob)
            sentiment_scores.append(sentiment_score)

        return sentiment_scores
    except Exception as e:
        raise RuntimeError(f"Error during prediction: {str(e)}")

# API Endpoint
@app.route('/score', methods=['POST'])
def score():
    try:
        # Parse input JSON
        content = request.json
        prompts = content.get("prompts", [])

        if not prompts:
            return jsonify({"error": "No prompts provided"}), 400

        # Call scorer function
        scores = scorer(prompts)
        return jsonify({"sentiment_scores": scores}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get(PORT)))
