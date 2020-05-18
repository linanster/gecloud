def init_ext(app):
    from app.ext.bootstrap import bootstrap
    from app.ext.cache import cache
    bootstrap.init_app(app)
    cache.init_app(app)
