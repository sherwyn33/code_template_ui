from flask import Blueprint
from . import object_details
from .object_details import object_details_namespace

index_blueprint = Blueprint('index', __name__)

# ... import other namespaces

def register_routes(api):
    api.add_namespace(object_details_namespace, path='/api/object_details')
    # ... add other namespaces

