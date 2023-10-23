
from starlette.routing import Mount

from auth_privileged.urls import routes as privileged_routes


routes = [
    Mount("/privileged", routes=privileged_routes),

]
