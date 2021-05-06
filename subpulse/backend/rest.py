"""Sample RESTful Framework."""
from sanic import Blueprint
from sanic.request import Request
from sanic.response import HTTPResponse, json
from sanic_openapi import doc

from subpulse.routines import composite, simple

# NOTE: The URL Prefix for your backend has to be the name of the backend
blueprint = Blueprint("subpulse Backend", url_prefix="/")


@doc.summary("Hello from /subpulse!")
@blueprint.get("/")
async def hello(request: Request) -> HTTPResponse:
    """Hello World.

    Parameters
    ----------
    request : Request
        Request object from sanic app

    Returns
    -------
    HTTPResponse
    """
    return json("Hello from /subpulse 🦧")


@doc.summary("Seeder Routine")
@blueprint.get("/simple")
async def get_seeder(request: Request) -> HTTPResponse:
    """Run Seeder Routine.

    Parameters
    ----------
    request : Request
        Request object from sanic app

    Returns
    -------
    HTTPResponse
    """
    example = simple.Simple("hex")
    return json(example.seedling())


@doc.summary("Composite Routine")
@blueprint.get("/composite")
async def get_composite(request: Request) -> HTTPResponse:
    """Run Composite Routine.

    Parameters
    ----------
    request : Request
        Request object from sanic app

    Returns
    -------
    HTTPResponse
    """
    example = composite.Composite(1.0, 10.0, "hex")
    return json(example.get_random_integer())
