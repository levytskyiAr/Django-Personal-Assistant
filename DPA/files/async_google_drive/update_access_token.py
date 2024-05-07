#!/usr/bin/python3.7

import sys
import webbrowser

from aiohttp.web import RouteTableDef, Application, run_app, Response, json_response, HTTPFound

from aiogoogle import Aiogoogle
from aiogoogle.auth.utils import create_secret

try:
    import yaml
except:
    print('couldn\'t import yaml. Install "pyyaml" first')
    sys.exit(-1)

sys.path.append("../..")

try:
    with open("keys.yaml", "r") as stream:
        config = yaml.load(stream, Loader=yaml.FullLoader)
except Exception as e:
    print("Rename _keys.yaml to keys.yaml")
    raise e

EMAIL = config["user_creds"]["email"]
CLIENT_CREDS = {
    "client_id": config["client_creds"]["client_id"],
    "client_secret": config["client_creds"]["client_secret"],
    "scopes": config["client_creds"]["scopes"],
    "redirect_uri": "http://localhost:5000/callback/aiogoogle",
}
state = create_secret()

LOCAL_ADDRESS = "localhost"
LOCAL_PORT = 5000

routes = RouteTableDef()
aiogoogle = Aiogoogle(client_creds=CLIENT_CREDS)


@routes.get("/authorize")
def authorize(request):
    if aiogoogle.oauth2.is_ready(CLIENT_CREDS):
        uri = aiogoogle.oauth2.authorization_url(
            client_creds=CLIENT_CREDS,
            state=state,
            access_type="offline",
            include_granted_scopes=True,
            login_hint=EMAIL,
            prompt="select_account",
        )
        # Step A
        raise HTTPFound(uri)
    else:
        return Response(text="Client doesn't have enough info for Oauth2", status=500)


@routes.get("/callback/aiogoogle")
async def callback(request):
    if request.query.get("error"):
        error = {
            "error": request.query.get("error"),
            "error_description": request.query.get("error_description"),
        }
        return json_response(error)
    elif request.query.get("code"):
        returned_state = request.query["state"]

        if returned_state != state:
            return Response(text="NO", status=500)

        full_user_creds = await aiogoogle.oauth2.build_user_creds(
            grant=request.query.get("code"), client_creds=CLIENT_CREDS
        )
        with open('keys.yaml', 'r') as file:
            keys = yaml.safe_load(file)

        keys['user_creds'] = {
            'email': 'barsujkoanatoliy@gmail.com',
            'access_token': full_user_creds['access_token'],
            'refresh_token': full_user_creds['refresh_token'],
            'expires_at': full_user_creds['expires_at']}

        with open('keys.yaml', 'w') as file:
            yaml.dump(keys, file)

        return Response(text='access_token has been updated')
    else:
        return Response(text="Something's probably wrong with your callback", status=400)


if __name__ == "__main__":
    app = Application()
    app.add_routes(routes)

    webbrowser.open("http://" + LOCAL_ADDRESS + ":" + str(LOCAL_PORT) + "/authorize")
    run_app(app, host=LOCAL_ADDRESS, port=LOCAL_PORT)
