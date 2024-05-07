#!/usr/bin/python3.7
import os
import sys
import webbrowser

from aiohttp.web import RouteTableDef, Application, run_app, Response, json_response, HTTPFound

from aiogoogle import Aiogoogle
from aiogoogle.auth.utils import create_secret
from dotenv import dotenv_values, set_key, load_dotenv
load_dotenv()

sys.path.append("../..")

EMAIL = os.getenv('EMAIL')
CLIENT_CREDS = {
    "client_id": os.getenv('CLIENT_ID'),
    "client_secret": os.getenv('CLIENT_SECRETS'),
    "scopes": ['https://www.googleapis.com/auth/drive.file',
               'https://www.googleapis.com/auth/drive.install', 'email'],
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
        config = dotenv_values("../../.env")
        new_data = {
            'EMAIL': 'barsujkoanatoliy@gmail.com',
            'ACCESS_TOKEN': full_user_creds['access_token'],
            'REFRESH_TOKEN': full_user_creds['refresh_token'],
            'EXPIRES_AT': full_user_creds['expires_at'],
        }

        for key, value in new_data.items():
            if key in config:
                set_key("../../.env", key, value)
            else:
                set_key("../../.env", key, value, quote_mode='never')

        return Response(text='access_token has been updated')
    else:
        return Response(text="Something's probably wrong with your callback", status=400)


if __name__ == "__main__":
    app = Application()
    app.add_routes(routes)

    webbrowser.open("http://" + LOCAL_ADDRESS + ":" + str(LOCAL_PORT) + "/authorize")
    run_app(app, host=LOCAL_ADDRESS, port=LOCAL_PORT)
