# Main entry point of the application
import os 
from dotenv import load_dotenv
from pharmafinder import create_app

# loading environment variables
load_dotenv()
# Creating the flask application
app = create_app()

if __name__ == "__main__":
    debug = os.environ.get("FLASK_DEBUG") == "1"
    port = int(os.environ.get("PORT", "5000"))

    app.run(debug=debug, port=port)
    