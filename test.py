import cherrypy
from langchain.chat_models import ChatOpenAI
from langchain.agents import create_json_agent
from langchain.agents.agent_toolkits import JsonToolkit
from langchain.tools.json.tool import JsonSpec
import json
import sys
import logging

# Define a CORS tool
class CORSTool(cherrypy.Tool):
    def __init__(self):
        cherrypy.Tool.__init__(self, 'before_handler', self.cors_handler, priority=20)

    def cors_handler(self):
        cherrypy.response.headers['Access-Control-Allow-Origin'] = '*'
        cherrypy.response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        cherrypy.response.headers['Access-Control-Allow-Headers'] = 'Content-Type'

cherrypy.tools.CORS = CORSTool()

class HelloWorld:
    def index(self):
        query = "What is the address of Justus Steak House?"
        logging.info(f"Received query: {query}")

        if query:
            file = "/content/sample_data/myData.json"
            try:
                with open(file, "r") as f1:
                    data = json.load(f1)
                spec = JsonSpec(dict_=data, max_value_length=4000)
                toolkit = JsonToolkit(spec=spec)
                agent = create_json_agent(llm=ChatOpenAI(temperature=0, openai_api_key="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", model="gpt-3.5-turbo"), toolkit=toolkit, max_iterations=1000, verbose=True)
                result = agent.run(query)
                return result
            except FileNotFoundError:
                return "File not found"
            except json.JSONDecodeError:
                return "Error decoding JSON"
        else:
            return "Query parameter is required"
    index.exposed = True

    @cherrypy.expose
    def ask(self, question):
        return f"You asked: {question}"

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python your_script.py <port_number>")
        sys.exit(1)

    port_number = int(sys.argv[1])
    config = {
        'server.socket_host': '0.0.0.0',
        'server.socket_port': port_number,
        '/': {
            'tools.CORS.on': False,  # Enable CORS for the entire application
        }
    }
    cherrypy.config.update({'tools.cors.origin': 'http://localhost:3000'})
    cherrypy.config.update(config)
    cherrypy.quickstart(HelloWorld())