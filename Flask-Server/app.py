from flask import Flask, request, jsonify
import base64
import requests
import os
import logging
import time
from dotenv import load_dotenv
from flask_cors import CORS

# Gemini imports
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain import PromptTemplate

app = Flask(__name__)
CORS(app)

# Load environment variables
load_dotenv()
os.environ["GOOGLE_API_KEY"] = os.environ.get('GOOGLE_API_KEY')

logger = logging.getLogger()
logging.basicConfig(level=logging.INFO)

def mm(graph, save_as_png=False, file_name="output.png"):
    """Converts MermaidJS graph code to an image URL."""
    graphbytes = graph.encode("ascii")
    base64_bytes = base64.b64encode(graphbytes)
    base64_string = base64_bytes.decode("ascii")
    img_url = "https://mermaid.ink/img/" + base64_string
    response = requests.get(img_url)

    if response.status_code != 200:
        raise ValueError("Sorry, unable to generate flowchart")

    if save_as_png:
        with open(file_name, "wb") as f:
            f.write(response.content)

    return img_url

# Configure the Gemini model
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

# Initialize the Gemini model
llm = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0)

memory_list = [ConversationBufferMemory()]

def create_conversation_chain(memory, verbose=True):
    """Creates a conversation chain with the specified memory."""
    return ConversationChain(
        llm=llm, 
        verbose=verbose, 
        memory=memory,
        prompt=PromptTemplate(
            input_variables=['history', 'input'],
            template="""You are a MermaidJS code generator that generates code for flowcharts. You will be provided with inputs in natural language or input along with previous code and instructions. Your job is to return the MermaidJS code that can be directly used to generate a flowchart without any extra characters causing errors.
            Points to note:
            1. Output will contain code only not other text.
            2. Output will not contain the word 'mermaid'.
            3. Output should be in a single line; hence don't use \\n in the final output.
            
            Example output format: 
            flowchart TD;A[Home] -->|Morning Routine| B(Towards Office);B --> C{{Mode of transportation}};C -->|Cab if available| D[Cab mini];C -->|metro if have time| E[Metro];C -->|friend call| F[fa:fa-car Car];D --> G[Office];E --> G[Office];F --> G[Office];

            Current conversation:
            {history}
            Human: {input}
            AI:""", 
            template_format='f-string', 
            validate_template=True)
    )

conversation = create_conversation_chain(memory_list[0])


@app.route('/generate', methods=['POST'])
def generate_flowchart():
    """Generates a flowchart based on user input."""
    global conversation  # Declare conversation as global to modify it
    try:
        data = request.json
        input_text = data.get('query')

        if input_text is None or input_text.strip() == "":
            return jsonify({"message": "Input query cannot be empty."}), 400

        if input_text == "reset":
            # Clear previous memories and create a new conversation chain
            memory_list.clear()  
            new_memory = ConversationBufferMemory()
            memory_list.append(new_memory)
            conversation = create_conversation_chain(new_memory)
            return jsonify({"message": "Conversation reset."}), 200

        elif input_text != "exit":
            # Ensure conversation is initialized before using it
            if not conversation:
                conversation = create_conversation_chain(memory_list[0])

            mermaid_code = conversation.predict(input=input_text)
            img_url = mm(mermaid_code, save_as_png=False, file_name=f"{int(time.time())}.png")
            logger.info(f"Mermaid output: {mermaid_code}")
            return jsonify({"img_url": img_url, "message": "Flowchart generated successfully."}), 200

    except Exception as e:
        logger.error(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)), debug=False)

