def init_views(app):
    from app.views.blue_main import blue_main
    from app.views.blue_rasp import blue_rasp
    from app.views.blue_auth import blue_auth
    from app.views.blue_account import blue_account
    from app.views.blue_error import blue_error
    from app.views.blue_about import blue_about
    from app.views.blue_contact import blue_contact
    app.register_blueprint(blue_main)
    app.register_blueprint(blue_rasp)
    app.register_blueprint(blue_auth)
    app.register_blueprint(blue_account)
    app.register_blueprint(blue_error)
    app.register_blueprint(blue_about)
    app.register_blueprint(blue_contact)
