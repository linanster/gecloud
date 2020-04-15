def init_views(app):
    from .blue_main import blue_main
    app.register_blueprint(blue_main)
