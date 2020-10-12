def init_views(app):
    from app.views.blue_main import blue_main
    from app.views.blue_rasp import blue_rasp
    from app.views.blue_auth import blue_auth
    app.register_blueprint(blue_main)
    app.register_blueprint(blue_rasp)
    app.register_blueprint(blue_auth)
