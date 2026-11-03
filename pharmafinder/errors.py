# To return consistent JSON error responses
from flask import jsonify, request
from werkzeug.exceptions import HTTPException

class ApiError(Exception):
    def __init__(self, message, status=400, fields=None):
        self.message = message
        self.status = status
        self.fields = fields or {}
# Handle errors caused by our api
def register_error_handlers(app):
    @app.errorhandler(ApiError)
    def handle_api_error(err):
        response = {"error": err.message}

        if err.fields:
            response["fields"] = err.fields

        return jsonify(response), err.status
# Handle standard http errors
@app.errorhandler(HttpException)
def handle_http_error(err):
    
    if request.path.startswith("/api/"):
        return jsonify({"error": err.description}), err.code

    return err

# Handle unexpected error
@app.errorhandler(Exception)
def handle_unexpected_error(err):

    app.logger.exception("Unhandled error")

    return jsonify({
        "error": "international server error"
    }), 500

