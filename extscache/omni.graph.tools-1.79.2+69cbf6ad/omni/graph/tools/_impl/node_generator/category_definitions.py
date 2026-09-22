"""Handle the mapping of OGN types onto the various generated code types"""

import json
from io import TextIOWrapper
from pathlib import Path
from typing import IO, Dict, List

from .keys import NodeTypeKeys
from .utils import ParseError, is_comment

CategoryListType = Dict[str, List[str]]


# ==============================================================================================================
def get_category_definitions(category_information: str | dict | IO | Path | None) -> CategoryListType:
    """Get the set of category definitions specified in the category file, JSON string, or dictionary

    Args:
        category_information: Reference to a file containing a category dictionary or the dictionary itself

    Returns:
        Dictionary of MainCategory:SubCategories of category types found in the file

    Raises:
        ParseError if the file could not be parsed
    """
    try:
        definitions = {}
        if category_information is None:
            pass
        elif isinstance(category_information, str):
            definitions = json.loads(category_information)[NodeTypeKeys.CATEGORY_DEFINITIONS]
        elif isinstance(category_information, TextIOWrapper):
            definitions = json.load(category_information)[NodeTypeKeys.CATEGORY_DEFINITIONS]
        elif isinstance(category_information, Path):
            with category_information.open("r") as fp:
                definitions = json.load(fp)[NodeTypeKeys.CATEGORY_DEFINITIONS]
        elif isinstance(category_information, dict):
            definitions = category_information
        else:
            raise ParseError(f"Category definition file type not handled - {category_information}")
    except OSError as error:
        raise ParseError(f"File error when parsing category definitions {category_information} - {error}") from None
    except json.decoder.JSONDecodeError as error:
        raise ParseError(f"Invalid JSON formatting in file {category_information} - {error}") from None

    # Filter out the comments before returning the dictionary
    definitions = {key: value for key, value in definitions.items() if not is_comment(key)}

    return definitions


# ==============================================================================================================
def merge_category_definitions(
    merged_definitions: CategoryListType, definitions_to_merge: str | dict | IO | Path | None
):
    """Merge the second set of category definitions with the first one"""
    merged_definitions.update(get_category_definitions(definitions_to_merge))
