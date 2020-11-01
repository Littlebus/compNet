import os
from app import app
from pprint import pprint
pprint(app.config)
if __name__ == "__main__":
    port = os.environ.get('PORT', 8000)
    app.run('0.0.0.0', port=port, debug=True, threaded=True)
