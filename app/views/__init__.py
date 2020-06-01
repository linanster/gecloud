def init_views(app):
    from app.views.blue_main import blue_main
    app.register_blueprint(blue_main)
