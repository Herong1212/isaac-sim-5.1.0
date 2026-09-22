"""
Generate object caption from 4 different view angles of an object. The views are rendered through ORO normal process.
Only images and prim usd path is provided.

Prompts reference:
https://gitlab-master.nvidia.com/omniverse/deeptag/vision-endpoint/-/tree/main/vision_endpoint/metadata.
"""

import asyncio
import base64
import hashlib
import io
import json
import logging
import os
import re

import omni
import yaml

# set OPENAI_API_KEY in environment variables if not set
if os.getenv("OPENAI_API_KEY") is None:
    os.environ["OPENAI_API_KEY"] = "placeholder"
if os.getenv("MONGODB_URI") is None:
    os.environ["MONGODB_URI"] = "placeholder"

from openai import AzureOpenAI
from PIL import Image
from pymongo import MongoClient

from ..utils import retrieve_api_token

MODUEL_DIR = os.path.dirname(__file__)

DB_NAME = "dsbench"
COLLECTION_NAME = "usd_caption"


class GenObjectCap:
    """
    Generate object caption from 4 different view angles of an object. The views are rendered through IRO.

    """

    def __init__(self, model_name):
        """
        Attributes:
            model_name (str): The model name to use for generating the caption.
        """

        openai_api_key = os.getenv("OPENAI_API_KEY")
        if openai_api_key == "placeholder":
            response_dict = retrieve_api_token()
            if response_dict is not None:
                openai_api_key = response_dict["access_token"]

        if os.getenv("MONGODB_URI") is None or os.getenv("MONGODB_URI") == "placeholder":
            print("[WARNING] MONGODB_URI is not set")

        if openai_api_key != "placeholder":  # TODO: support other models by LangChain
            self.vlm_client = AzureOpenAI(
                azure_endpoint="https://prod.api.nvidia.com/llm/v1/azure/",
                api_key=openai_api_key,
                api_version="2024-09-01-preview",
            )
        else:
            self.vlm_client = None

        mongodb_uri = os.getenv("MONGODB_URI")
        db_name = DB_NAME
        collection_name = COLLECTION_NAME

        try:
            # Connect to MongoDB
            self.mongodb_client = MongoClient(mongodb_uri)
            print(f"[IRC] Connected to MongoDB")

            # Select the database and collection
            db = self.mongodb_client[db_name]
            self.collection = db[collection_name]
        except Exception as e:
            print(f"[Error] An error occurred: {e}")

        self.model_name = model_name
        self.image_base64 = None
        self.system_prompt = None

    async def __encode_image(self, image_path: str):
        with Image.open(image_path) as img:
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format="PNG")
            img_byte_arr = img_byte_arr.getvalue()
            base64_image = base64.b64encode(img_byte_arr).decode("utf-8")
        return base64_image

    async def __encode_images(self, image_paths):
        result = [self.__encode_image(image_path) for image_path in image_paths]
        encoded_images = await asyncio.gather(*result)
        return encoded_images

    async def upload_to_database(self, response_dict, usd_path):
        """
        Uploads a dictionary (map) to the specified MongoDB database collection.

        response_dict (dict): The dictionary to upload to the database.
        prim_usd_path (str): The path to the primary USD file associated with the map.
        """
        usd_name = os.path.basename(usd_path)
        upload_dict = {"usd_name": usd_name}
        sha256_hash = await get_file_unique_identifier_async(usd_path)
        upload_dict["usd_sha256"] = sha256_hash
        upload_dict.update(response_dict)

        try:
            # Insert the map into the collection
            result = self.collection.insert_one(upload_dict)
            print(f"Map of {usd_name} successfully uploaded to collection. Inserted ID: {result.inserted_id}")

        except Exception as e:
            print(f"An error occurred: {e}")

    def generate_system_prompt(self):
        """
        Prepares the system prompt for the object caption generation.
        """

        with open(f"{MODUEL_DIR}/metadata/metadata_fields.yaml", "r") as stream:
            try:
                metadata_fields: dict[str, str] = yaml.safe_load(stream)
            except yaml.YAMLError as e:
                logging.error(e, exc_info=True)
                raise Exception(f"Reading YAML Exception: {str(e)}") from e

        metadata_keys = json.dumps({k: "" for k in metadata_fields.keys()}, indent=2)
        metadata_fields = json.dumps(metadata_fields, indent=2)

        with open(f"{MODUEL_DIR}/metadata/image_prompt.txt", "r") as file:
            string = file.read()
        self.system_prompt = string.format(metadata_keys=metadata_keys, metadata_fields=metadata_fields)

        # self.system_prompt += f' <img src="data:image/png;base64,{self.image_base64}"/>'

    async def prepare_image_str(self, image_paths=[]):
        """
        Converts image files to base64 strings and concatenates them into a single string for prompts.

        image_paths (list): A list of paths to the image files to convert to base64 strings.
        """
        if not image_paths:
            raise Exception("No image paths provided")
        if len(image_paths) != 4:
            raise Exception("Please provide 4 image paths")
        # self.image_base64 = self.__concat_images_2x2(image_paths)
        # self.image_base64 = self.__encode_image(image_paths[0])
        self.image_base64 = await self.__encode_images(image_paths)

    async def generate_caption(self):
        """
        Generates object caption using the VLM model.
        """
        if self.vlm_client is None:
            raise Exception("VLM client is not set")

        self.generate_system_prompt()

        content = [{"type": "text", "text": self.system_prompt}]

        for img_str in self.image_base64:
            content.append({"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_str}"}})
        messages = [{"role": "user", "content": content}]
        chat_response = self.vlm_client.chat.completions.create(
            messages=messages,
            model=self.model_name,
            temperature=0.2,
            top_p=0.7,
            max_tokens=1024,
            stream=False,
        )

        return chat_response.choices[0].message.content

    async def check_usd_record(self, usd_path):
        """
        Check if the prim usd exists in the database.

        usd_path (str): The path to the primary USD file to check.
        """
        # usd_name = os.path.basename(usd_path)
        hash256 = await get_file_unique_identifier_async(usd_path)  # unique identifier
        query = {"usd_sha256": hash256}  # unique identifier is enough
        if self.collection.find_one(query) is None:
            return False
        else:
            return True

    async def run(self, prim_usd_path, image_paths):
        """
        Runs the object caption generation process.
        """
        # check if prim_usd_path exists in database
        flag = await self.check_usd_record(prim_usd_path)
        if flag:
            print(f"Prim usd path {prim_usd_path} already exists in database")
        else:
            # check image paths
            for img_path in image_paths:
                if not os.path.exists(img_path):
                    raise Exception(f"Image path {img_path} does not exist")

            await self.prepare_image_str(image_paths=image_paths)
            try:
                response = await self.generate_caption()
            except Exception as e:
                # the code has expired
                response_dict = retrieve_api_token()

                self.vlm_client = AzureOpenAI(
                    azure_endpoint="https://prod.api.nvidia.com/llm/v1/azure/",
                    api_key=response_dict["access_token"],
                    api_version="2024-09-01-preview",
                )
                # try again
                response = await self.generate_caption()

            try:

                json_data = json.loads(response)
            except:
                json_data = extract_json_from_text(response)

            await self.upload_to_database(json_data, prim_usd_path)


def extract_json_from_text(text):
    """
    Extracts JSON content from a text block enclosed in triple backticks (```) and returns it as a Python dictionary.
    """
    # Use regex to capture the JSON block within the backticks (```)
    json_pattern = "```json(.*?)```"

    # Search for the JSON block in the text
    json_match = re.search(json_pattern, text, re.DOTALL)

    if json_match:
        json_str = json_match.group(1).strip()  # Extract JSON string
        try:
            # Parse the JSON string into a Python dictionary
            json_data = json.loads(json_str)
            return json_data
        except json.JSONDecodeError:
            print("Error: The extracted content is not valid JSON.")
            return None
    else:
        print("No JSON found in the provided text.")
        return None


async def get_file_unique_identifier_async(file_path):
    """Returns a unique identifier (SHA256 hash) for the file content.

    file_path (str): The path to the USD file for which to generate the unique identifier.
    """
    if file_path == "None" or file_path is None:
        return
    sha256_hash = hashlib.sha256()
    _, _, cached_file_path = await omni.client.open_cached_file_async(file_path, download=False)
    if not cached_file_path:
        return None
    # Open the file in binary mode and read in chunks to avoid memory issues with large files
    with open(cached_file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)

    # Return the hexadecimal representation of the hash
    return sha256_hash.hexdigest()
