def init_apis(app):
    from app.apis.api_db import api_db
    api_db.init_app(app)
