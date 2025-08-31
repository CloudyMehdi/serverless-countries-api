import json
import os

# Load the JSON file that contains the country data
# __file__ = path of this script
# os.path.dirname(__file__) = directory of this script
# os.path.join(..., "data", "countries.json") = full path to the data file
with open(os.path.join(os.path.dirname(__file__), "data", "countries.json"), "r", encoding="utf-8") as f:
    COUNTRIES = json.load(f)

def handler(event, context):
    """
    AWS Lambda handler
    
    - event: contains request data (path, query parameters, etc.)
    - context: contains runtime information (not used here)

    This function will route incoming HTTP requests to the correct logic
    depending on the request path.
    """
    path = event.get("rawPath", "") # e.g. "/countries/FR"
    query = event.get("queryStringParameters") or {} # query params (?limit=10, ?name=france, etc.)

    if path == "/": # Case: GEt /
        return respond(200, {"message": "API is running 🚀"})

    # Handle routes starting with /countries
    if path.startswith("/countries"):
        parts = path.strip("/").split("/") # split into ["countries"] or ["countries", "FR"]

        if len(parts) == 1:  # Case: GET /countries
            limit = int(query.get("limit", len(COUNTRIES))) # optional ?limit
            return respond(200, COUNTRIES[:limit])

        elif len(parts) == 2:  # Case: GET /countries/{alpha2}
            code = parts[1].upper() # ensure uppercase, e.g. "fr" → "FR"
            # Find the first country with matching alpha2 code
            country = next((c for c in COUNTRIES if c["alpha2"] == code), None)
            if country:
                return respond(200, country)
            else:
                return respond(404, {"error": "Country not found"})

    # Handle route: /search?name=...
    if path.startswith("/search"):
        name = query.get("name", "").lower()
        if not name: # missing query param
            return respond(400, {"error": "Missing 'name' query param"})
        # Search in both English and French names
        results = [
            c for c in COUNTRIES
            if name in c["name"].lower() or name in c["name_fr"].lower()
        ]
        return respond(200, results)

    # Default response: route not found
    return respond(404, {"error": "Not Found"})

def respond(status, body):
    """
    Helper function to format the HTTP response in API Gateway/Lambda format.

    - status: HTTP status code (200, 404, etc.)
    - body: response body (dict, list, etc. will be converted to JSON)
    """
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json"},
        # ensure_ascii=False keeps accents (é, ç, etc.) in the output
        "body": json.dumps(body, ensure_ascii=False)
    }
