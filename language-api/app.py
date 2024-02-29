from flask import Flask, request, jsonify
from langchain_openai import ChatOpenAI
from langchain.agents import create_json_agent
from langchain_community.agent_toolkits import JsonToolkit
from langchain.tools.json.tool import  JsonSpec
from langchain.text_splitter import RecursiveJsonSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import LanceDB
from langchain.chains import RetrievalQA
from langchain_openai import OpenAI
from langchain.text_splitter import CharacterTextSplitter
from flask_cors import CORS
import json
import lancedb
from langchain_community.llms import HuggingFacePipeline

app = Flask(__name__)
CORS(app)

# Route with a query parameter as a string
@app.route('/greet', methods=['POST'])
def greet_user():
    # Get the 'name' query parameter from the request
    data = request.get_json()
    if 'name' in data:
        query = data['name']
    print(query)
    if query:
        file="myData.json"
        with open(file,"r") as f1:
            data=json.load(f1)
            f1.close()
        # spec=JsonSpec(dict_=data,max_value_length=4000)
        # toolkit=JsonToolkit(spec=spec)
        # agent=create_json_agent(llm=ChatOpenAI(temperature=0,openai_api_key="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",model="gpt-3.5-turbo"),toolkit=toolkit,max_iterations=1000,verbose=True)
        # result=agent.run(query)
        text_splitter = RecursiveJsonSplitter()
        texts = text_splitter.create_documents(texts=[data])
        db = lancedb.connect("/tmp/lancedb")

        embeddings = OpenAIEmbeddings(openai_api_key="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")

        table = db.create_table(
            "my_table",
             data=[
                {
                    "vector": embeddings.embed_query("Hello World"),
                    "text": "Hello World",
                    "id": "1",
                }
            ],
            mode="overwrite",
            )
        # Create a vectorstore from documents
        db = LanceDB.from_documents(texts, embeddings,connection=table)
        # Create retriever interface
        retriever = db.as_retriever()
        # Create QA chain
        qa = RetrievalQA.from_chain_type(llm=OpenAI(openai_api_key="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"), chain_type='stuff', retriever=retriever)
        result= qa.run(query)
        print(result)
        return jsonify({"message": f"{result}"})
    else:
        return jsonify({"error": "Name query parameter is required"}), 400

if __name__ == '__main__':
    app.run(debug=True)
