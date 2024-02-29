from flask import Flask, request, jsonify
from langchain.chat_models import ChatOpenAI
from langchain.agents import create_json_agent
from langchain.agents.agent_toolkits import JsonToolkit
from langchain.tools.json.tool import  JsonSpec
import json

app = Flask(__name__)

# Route with a query parameter as a string
@app.route('/greet', methods=['GET'])
def greet_user():
    # Get the 'name' query parameter from the request
    query = request.args.get('name')
    print(query)
    if query:
        file="myData.json"
        with open(file,"r") as f1:
            data=json.load(f1)
            f1.close()
        spec=JsonSpec(dict_=data,max_value_length=4000)
        toolkit=JsonToolkit(spec=spec)
        agent=create_json_agent(llm=ChatOpenAI(temperature=0,openai_api_key="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",model="gpt-3.5-turbo"),toolkit=toolkit,max_iterations=1000,verbose=True)
        result=agent.run(query)
       
        return jsonify({"message": f"Reply: {result}"})
    else:
        return jsonify({"error": "Name query parameter is required"}), 400

if __name__ == '__main__':
    app.run(debug=True)
