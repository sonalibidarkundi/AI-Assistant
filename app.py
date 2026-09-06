from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from groq import Groq
from dotenv import load_dotenv
import os
import asyncio


# Load environment variables
load_dotenv()


# Create Flask application
app = Flask(__name__)


# Enable CORS for frontend
CORS(app)


# -----------------------------
# Environment variables
# -----------------------------

mongo_uri = os.getenv("MONGO_URI")
groq_api_key = os.getenv("GROQ_API_KEY")

if not mongo_uri:
    raise RuntimeError("MONGO_URI is not set")

if not groq_api_key:
    raise RuntimeError("GROQ_API_KEY is not set")


# -----------------------------
# MongoDB connection
# -----------------------------

client = MongoClient(mongo_uri)

db = client["intucate_db"]

prompts_collection = db["prompts"]
history_collection = db["history"]


# -----------------------------
# Groq connection
# -----------------------------

groq_client = Groq(
    api_key=groq_api_key
)

MODEL_NAME = "openai/gpt-oss-20b"


# -----------------------------
# Helper function
# -----------------------------

def get_prompt_template():
    """
    Fetch the education prompt template from MongoDB.
    """

    prompt_document = prompts_collection.find_one(
        {"_id": "Education_Prompt"}
    )

    if not prompt_document:
        raise ValueError("Prompt template not found")

    return prompt_document["template"]


# -----------------------------
# Home route
# -----------------------------

@app.route("/", methods=["GET"])
def home():

    return jsonify({
        "message": "Intucate API is running"
    })


# -----------------------------
# POST /ask
# -----------------------------
# Supports both:
# Local:  /ask
# Vercel: /api/ask
# -----------------------------

@app.route("/ask", methods=["POST"])
@app.route("/api/ask", methods=["POST"])
def ask_question():

    try:

        # Get JSON request
        data = request.get_json(silent=True) or {}


        # Get user input
        user_input = data.get("userInput")


        # Validate input
        if not isinstance(user_input, str) or not user_input.strip():

            return jsonify({
                "error": "userInput is required and must be a non-empty string"
            }), 400


        # Get prompt from MongoDB
        prompt_template = get_prompt_template()


        # Replace {{userInput}} with actual question
        prompt = prompt_template.replace(
            "{{userInput}}",
            user_input
        )


        # Call Groq AI
        response = groq_client.chat.completions.create(

            model=MODEL_NAME,

            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )


        # Get AI response
        ai_response = response.choices[0].message.content


        # Save history
        history_collection.insert_one({

            "userInput": user_input,

            "response": ai_response

        })


        # Return response
        return jsonify({

            "response": ai_response

        })


    except ValueError as error:

        return jsonify({

            "error": str(error)

        }), 404


    except Exception as error:

        print("Error:", error)

        return jsonify({

            "error": "Internal server error"

        }), 500


# =====================================================
# ASYNC PROCESSING
# =====================================================

async def process_question(
    user_input,
    prompt_template
):

    # Replace {{userInput}} with actual question
    prompt = prompt_template.replace(
        "{{userInput}}",
        user_input
    )


    # Run synchronous Groq API call
    # inside a separate thread
    response = await asyncio.to_thread(

        groq_client.chat.completions.create,

        model=MODEL_NAME,

        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )


    # Get AI response
    ai_response = response.choices[0].message.content


    return {

        "userInput": user_input,

        "response": ai_response

    }


async def process_multiple_questions(
    user_inputs,
    prompt_template
):

    # Create a task for each question
    tasks = [

        process_question(
            user_input,
            prompt_template
        )

        for user_input in user_inputs

    ]


    # Run all tasks concurrently
    # Results remain in input order
    results = await asyncio.gather(*tasks)


    return results


# -----------------------------
# POST /ask-multiple
# -----------------------------
# Supports both:
# Local:  /ask-multiple
# Vercel: /api/ask-multiple
# -----------------------------

@app.route("/ask-multiple", methods=["POST"])
@app.route("/api/ask-multiple", methods=["POST"])
def ask_multiple():

    try:

        # Get JSON request
        data = request.get_json(silent=True) or {}


        # Get user inputs
        user_inputs = data.get("userInputs")


        # Validate list
        if not isinstance(user_inputs, list) or not user_inputs:

            return jsonify({

                "error": "userInputs must be a non-empty list"

            }), 400


        # Validate every question
        if any(
            not isinstance(item, str) or not item.strip()
            for item in user_inputs
        ):

            return jsonify({

                "error": "Every userInput must be a non-empty string"

            }), 400


        # Get prompt template from MongoDB
        prompt_template = get_prompt_template()


        # Process questions asynchronously
        results = asyncio.run(

            process_multiple_questions(

                user_inputs,

                prompt_template

            )

        )


        # Save all results to MongoDB
        history_collection.insert_many(results)


        # Return responses
        return jsonify({

            "responses": [

                result["response"]

                for result in results

            ]

        })


    except ValueError as error:

        return jsonify({

            "error": str(error)

        }), 404


    except Exception as error:

        print("Error:", error)

        return jsonify({

            "error": "Internal server error"

        }), 500


# -----------------------------
# Run application locally
# -----------------------------

if __name__ == "__main__":

    app.run(
        debug=True
    )