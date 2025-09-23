from ninja.main import NinjaAPI

from incredible_data.mood.ninja.api import router as mood_router

api = NinjaAPI(version="2.0.0")

api.add_router("/mood/", mood_router)
