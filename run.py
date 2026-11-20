"""Start the ShopKart Order API.

    python run.py                       -> development settings
    SHOPKART_ENV=prod python run.py     -> production settings (Mac/Linux)
"""
from shopkart import create_app

app = create_app()

if __name__ == "__main__":
    app.run(port=8000, debug=app.config["SETTINGS"].app.debug)
