import logging
import azure.functions as func
import os
import requests

app = func.FunctionApp()

@app.function_name(name="HttpExample")
@app.route(route="hello", auth_level=func.AuthLevel.ANONYMOUS)
def main(req: func.HttpRequest) -> func.HttpResponse:
    name = req.params.get('name')
    if not name:
        try:
            req_body = req.get_json()
        except ValueError:
            req_body = {}
        name = req_body.get('name')

    if name:
        return func.HttpResponse(f"Hello, {name}! Welcome to the Community Hub Function App.", status_code=200)
    else:
        return func.HttpResponse("Please pass a name on the query string or in the request body.", status_code=400)
