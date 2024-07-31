from typing import final, Union
from jsonschema import validate
from jsonschema.exceptions import ValidationError
from genson import SchemaBuilder
import requests, json

class BaseAlgorithm:
    version: str = ""
    description: str = ""
    input_parameters: dict = {}
    output_algorithm: dict = {}
    error: dict = {}
    example_input: dict = {}
    example_output: dict = {}
    input_schema: dict = {}
    output_schema: dict = {}
    
    def __init__(self) -> None:
        # Update JSON Schemas
        # example input & example output must be defined
        if self.example_input == {} or self.example_output == {}:
            self.input_schema = {}
            self.output_schema = {}
        else:
            self.input_schema = self.json_to_schema(self.example_input)
            self.output_schema = self.json_to_schema(self.example_output)
        pass

    def run(self, callback_id: Union[int, None], ip_client: str):
        pass

    @final
    def get_info(self):
        return self.name

    @final
    def onFinish(self, callback_id, ip_client):
        # Validate output_json
        if self.validate_output() == False:
            self.error = {
                "success": False,
                "type": "validation output",
                "detail": "output doesnt follow the JSON Schema"
            }
        else:
            self.error = {
                "success": True
            }

        # Send info to api [callback]
        self.send_callback(callback_id=callback_id, ip_client=ip_client, message=self.output_algorithm)

    @final
    def to_dict(self):
        algorithm_dict = {
            "name": self.__class__.__name__,
            "version": self.version,
            "description": self.description,
            "module": self.__module__,
            #"input_parameters": self.input_parameters,
            "input_schema": self.input_schema,
            "output_schema": self.output_schema,
        }
        return algorithm_dict

    @final
    def json_to_schema(self, input):
        builder = SchemaBuilder()
        builder.add_object(input) # Input must be a dict
        schema = builder.to_schema()
        return schema

    @final
    def validate_schema(self, json_obj, schema):
        try:
            validate(instance=json_obj, schema=schema)
        except ValidationError:
            return False
        return True

    @final
    def validate_input(self):
        return self.validate_schema(self.input_parameters, self.input_schema)

    @final
    def validate_output(self):
        return self.validate_schema(self.output_algorithm, self.output_schema)

    @final
    def send_callback(self, callback_id: Union[int, None], ip_client: str, message: dict):
        if callback_id != None:
            url_callback = f"http://{ip_client}:5000/callback/{callback_id}"
            headers = {'Content-type': 'application/json'}
            try:
                print(f"Callback message sent to: {url_callback}")
                print(f"Type message: {type(message)}. Content: {message}")
                post = requests.post(url=url_callback, data=json.dumps(message), headers=headers)
                print(f"Status code: {post.status_code}")
                print(f"Content: {post.content}")
                return
            except Exception as ex:
                print(ex)
                print("Connection refused.")
                return
        print("CallbackID not defined.")
        
