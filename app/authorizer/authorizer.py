import logging
import os
from typing import Annotated

from fastapi import HTTPException
from fastapi.param_functions import Header


logger = logging.getLogger(__name__)
logger.setLevel(os.environ.get("LOG_LEVEL", "INFO"))


# Custom authorizer
async def authenticate_user(Authorization: Annotated[str, Header()]):
    if Authorization == "":
        raise HTTPException(status_code=401, detail="Authentication Token Missing.")

    logger.debug(f"Validating token: {Authorization}")

    # TODO: Write authorizer base class and solution

    return {
        "sub": "abc",
        "tenant": "123"
    }