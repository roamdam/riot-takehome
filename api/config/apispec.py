"""OpenAPI v3 Specification."""
from apispec import APISpec
from apispec_webframeworks.flask import FlaskPlugin


# Create an APISpec
spec = APISpec(
    title="Riot takehome API",
    version="0.1.0",
    openapi_version="3.0.2",
    plugins=[FlaskPlugin()]
)

# add swagger tags that are used for endpoint annotation
tags = [
    {"name": "encryption"},
    {"name": "signature"}
]

for tag in tags:
    spec.tag(tag)
