def init_apis(app):
    from app.apis.api_db import api_db
    from app.apis.api_auth import api_auth
    api_db.init_app(app)
    api_auth.init_app(app)
