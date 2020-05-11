def init_apis(app):
    from app.apis.api_db import api_db
    from app.apis.api_auth import api_auth
    from app.apis.api_rasp import api_rasp
    api_db.init_app(app)
    api_auth.init_app(app)
    api_rasp.init_app(app)
