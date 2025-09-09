#1st iteration: checking a JSON for "location" attribute and its validity according to GeoJSON format
#2nd version: checking if the context field exists and is valid (NGSI-LD)

import json
from flask import Flask, request, jsonify, render_template
from flask_swagger import swagger
from flask_swagger_ui import get_swaggerui_blueprint


app = Flask(__name__)

def validate_location_format(location):
    """
    Validates if the location follows FIWARE Smart Data Model specifications (GeoJSON format).
    """

    # Check if 'type' and 'coordinates' exist
    if "type" not in location or "coordinates" not in location:
        return False, "Missing 'type' or 'coordinates' in location."

    # Check if the type is one of the allowed GeoJSON types
    allowed_types = {"Point", "Polygon", "LineString"}
    location_type = location["type"]
    
    if location_type not in allowed_types:
        return False, f"Invalid type: {location_type}. Allowed types are: {allowed_types}."

    coordinates = location["coordinates"]

    # Validation for 'Point'
    if location_type == "Point":
        if len(coordinates) != 2:
            return False, "Point coordinates must contain exactly two elements (longitude, latitude)."
        longitude, latitude = coordinates
        if not (-180 <= longitude <= 180 and -90 <= latitude <= 90):
            return False, f"Invalid coordinates for 'Point'. Longitude must be in [-180, 180] and latitude in [-90, 90]."

    # Validation for 'LineString'
    elif location_type == "LineString":
        if len(coordinates) < 2:
            return False, "LineString must have at least two points (each point is a pair of coordinates)."
        for point in coordinates:
            if len(point) != 2:
                return False, "Each point in LineString must have exactly two elements (longitude, latitude)."
            longitude, latitude = point
            if not (-180 <= longitude <= 180 and -90 <= latitude <= 90):
                return False, f"Invalid point in LineString. Longitude must be in [-180, 180] and latitude in [-90, 90]."

    # Validation for 'Polygon'
    elif location_type == "Polygon":
        if len(coordinates) < 1:
            return False, "Polygon must have at least one linear ring (an array of arrays of coordinates)."
        for ring in coordinates:
            if len(ring) < 4:
                return False, "Each linear ring in Polygon must have at least four points (coordinate pairs)."
            if ring[0] != ring[-1]:
                return False, "The first and last point in each linear ring must be the same to close the Polygon."
            for point in ring:
                if len(point) != 2:
                    return False, "Each point in a Polygon ring must have exactly two elements (longitude, latitude)."
                longitude, latitude = point
                if not (-180 <= longitude <= 180 and -180 <= latitude <= 180):
                    return False, f"Invalid point in Polygon. Longitude must be in [-180, 180] and latitude in [-90, 90]."

    return True, "Location format is valid."


def check_location_in_json(json_data):
    """
    Checks if the JSON has a 'location' attribute and validates it.
    """

    if "location" not in json_data:
        return False, "The 'location' attribute is missing."

    # Validate location format
    location = json_data["location"]
    is_valid, message = validate_location_format(location)
    return is_valid, message


def validate_context_format(context):
    """
    Validates if the '@context' attribute follows the expected URL structure.
    """
    if not isinstance(context, list) or len(context) == 0:
        return False, "The '@context' attribute should be a non-empty list"
    
    context_url = context[0]
    
    # Check if the context URL starts with the expected prefix
    expected_prefix = "https://raw.githubusercontent.com/smart-data-models/"
    if not context_url.startswith(expected_prefix):
        return False, f"Invalid @context URL."
    
    return True, "Context format is valid."


def check_context_in_json(json_data):
    """
    Checks if the JSON has a '@context' attribute and validates it.
    """
    if "@context" not in json_data:
        return False, "The '@context' attribute is missing."
    
    # Validate context format
    context = json_data["@context"]
    is_valid, message = validate_context_format(context)
    return is_valid, message


def validate_json_data(json_data):
    """
    Validates the JSON data by applying a series of validation functions.
    """
    # List of validation functions to apply
    validation_functions = [
        check_location_in_json,
        check_context_in_json,
        # Future validation functions can be added here
    ]

    # Loop through each validation function
    for validate_func in validation_functions:
        is_valid, message = validate_func(json_data)
        if not is_valid:
            return False, message  # Stop at the first validation failure

    return True, "Data model is valid."


# Web route for file upload and validation
@app.route('/upload', methods=['POST'])
def upload_file():
    """
    File Upload API
    ---
    consumes:
      - multipart/form-data
    parameters:
      - in: formData
        name: file
        type: file
        description: The JSON file to upload.
        required: true
    responses:
      200:
        description: Successfully validated the data model.
      400:
        description: Failed to validate the JSON or incorrect file format.
    """
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    try:
        json_data = json.load(file)
        is_valid, message = validate_json_data(json_data)
        
        if is_valid:
            return jsonify({"message": "Data model is valid."}), 200
        else:
            return jsonify({"error": f"Validation failed: {message}"}), 400
    except json.JSONDecodeError:
        return jsonify({"error": "Invalid JSON file."}), 400

# Route to serve the frontend
@app.route('/')
def index():
    return render_template('index.html')


# API route for validating JSON data through a POST request
@app.route('/api/validate', methods=['POST'])
def validate_api():
    """
    JSON Validation API
    ---
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            location:
              type: object
              description: Location object in GeoJSON format
              properties:
                type:
                  type: string
                  description: Type of GeoJSON object (Point, LineString, Polygon)
                coordinates:
                  type: array
                  items:
                    type: number
                  description: Array of coordinates in [longitude, latitude] format
    responses:
      200:
        description: Successfully validated the data model.
      400:
        description: Failed to validate the JSON or incorrect format.
    """
    try:
        json_data = request.get_json()

        if json_data is None:
            return jsonify({"error": "No JSON provided"}), 400

        is_valid, message = validate_json_data(json_data)
        
        if is_valid:
            return jsonify({"message": "Data model is valid."}), 200
        else:
            return jsonify({"error": f"Validation failed: {message}"}), 400

    except json.JSONDecodeError:
        return jsonify({"error": "Invalid JSON data."}), 400
    

# Swagger documentation
@app.route('/swagger.json')
def swagger_json():
    swag = swagger(app)
    swag['info']['title'] = "Waterverse FAIRness Evaluator"
    swag['info']['description'] = "API for validating a data model according to WATERVERSE FAIR guidelines."
    swag['info']['version'] = "1.0"
    return jsonify(swag)


# Setup Swagger UI
SWAGGER_URL = '/swagger'  # URL for exposing Swagger UI
API_URL = '/swagger.json'  # Swagger JSON documentation endpoint

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,  # Swagger UI endpoint
    API_URL,  # Swagger JSON endpoint
    config={  # Swagger UI config
        'app_name': "Waterverse FAIRness Evaluator",
        'displayRequestDuration': True,
        'tryItOutEnabled': True
    }
)

app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)