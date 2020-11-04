import os
from app import app

if __name__ == "__main__":
    port = os.environ.get('PORT', 8000)
    app.run('127.0.0.1', port=port, debug=True, threaded=True)
