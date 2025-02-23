import json
import re
from langchain.schema import BaseOutputParser
from pydantic import BaseModel  # Import BaseModel if you haven't already

class JsonExtractor(BaseOutputParser):
    def parse(self, text: str):
        json_match = re.search(r'```json\s*({.*?})\s*```', text, re.DOTALL | re.IGNORECASE)
        if json_match:
            json_string = json_match.group(1)
        else:
            json_match = re.search(r'({.*})', text, re.DOTALL | re.IGNORECASE)
            if json_match:
                json_string = json_match.group(1)
            else:
                raise ValueError("JSON not found in content.")
        return json_string

def parse_llm_output(llm_output, pydantic_model: type[BaseModel]):
    """
    Parses LLM output into a specified Pydantic model.

    Args:
        llm_output (str): The LLM output string containing JSON.
        pydantic_model (type[BaseModel]): The Pydantic model to parse the JSON into.

    Returns:
        dict: A dictionary representation of the parsed Pydantic model.
    """
    extracted_json = JsonExtractor().parse(llm_output)
    json_dict = json.loads(extracted_json)
    json_log = pydantic_model(**json_dict)
    json_response = json_log.model_dump()
    return json_response