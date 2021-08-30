import os
from pathlib import Path
import yaml
import uuid
import io
import base64
import asyncio
from asyncio import BoundedSemaphore

from fastapi import FastAPI, HTTPException, status, File, Form, Depends, UploadFile
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from starlette.config import Config as Configure
from starlette.requests import Request
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import RedirectResponse

from authlib.integrations.starlette_client import OAuth

from typing import Optional, Literal

import pydatarecognition.rest_api as rest_api
from pydatarecognition.dependencies import get_user
from pydatarecognition.mongo_client import mongo_client
from pydatarecognition.rank import rank_db_cifs
from pydatarecognition.cif_io import rank_write

filepath = Path(os.path.abspath(__file__))

STEPSIZE_REGULAR_QGRID = 10**-3


app = FastAPI(docs_url=None, redoc_url=None)
app.add_event_handler("startup", mongo_client.connect_db)
app.add_event_handler("shutdown", mongo_client.close_mongo_connection)
app.include_router(rest_api.router)
app.mount("/static", StaticFiles(directory="static"), name="static")
app.add_middleware(SessionMiddleware, secret_key='!secret')
templates = Jinja2Templates(directory="templates")


@app.route('/')
async def home(request: Request):
    if request.session.get('login_status'):
        if request.session['login_status'] == "authorized":
            return templates.TemplateResponse('landing.html',
                                              {"request": request, "user": request.session.get('username'), "img": request.session.get('photourl')})
        else:
            return templates.TemplateResponse('landing.html', {"request": request, "user": None})
    else:
         return templates.TemplateResponse('landing.html', {"request": request, "user": None})


@app.route('/about')
def footer_about(request: Request):
    """
    Route function for about in the footer.

    Returns
    -------
    render_template
        Renders the footer-about page.
    """
    return templates.TemplateResponse('footer-about.html',
                                      {"request": request, "user": request.session.get('username'), "img": request.session.get('photourl')})


@app.route('/privacy')
def footer_privacy(request: Request):
    """
    Route function for privacy policy in the footer.

    Returns
    -------
    render_template
        Renders the privacy-policy page.
    """
    return templates.TemplateResponse('footer-privacy.html',
                                      {"request": request, "user": request.session.get('username'), "img": request.session.get('photourl')})


@app.route('/terms')
async def footer_term(request: Request):
    """
    Route function for terms of use in the footer.

    Returns
    -------
    render_template
        Renders the footer-term page.
    """
    return templates.TemplateResponse('footer-term.html',
                                      {"request": request, "user": request.session.get('username'), "img": request.session.get('photourl')})


# Initialize our OAuth instance from the client ID and client secret specified in our .env file
config = Configure('.env')
oauth = OAuth(config)

CONF_URL = 'https://accounts.google.com/.well-known/openid-configuration'
oauth.register(
    name='google',
    server_metadata_url=CONF_URL,
    client_kwargs={
        'scope': 'openid email profile'
    }
)

@app.get('/login', tags=['authentication'])  # Tag it as "authentication" for our docs
async def login(request: Request):

    return templates.TemplateResponse('login.html', {"request": request, "user": None})


@app.get('/google_login', tags=['authentication'])  # Tag it as "authentication" for our docs
async def google_login(request: Request):
    # Redirect Google OAuth back to our application
    redirect_uri = request.url_for('auth')

    return await oauth.google.authorize_redirect(request, redirect_uri)


@app.route('/auth')
async def auth(request: Request):
    # Perform Google OAuth
    token = await oauth.google.authorize_access_token(request)
    user = await oauth.google.parse_id_token(request, token)

    # Save the user
    request.session['user'] = dict(user)
    request.session['photourl'] = request.session['user']['picture']
    request.session['username'] = request.session['user']['given_name'] if ('given_name' in request.session['user']) else "Anonymous"
    request.session['login_status'] = 'authorized'

    return RedirectResponse(url='/')


@app.get('/logout', tags=['authentication'])  # Tag it as "authentication" for our docs
async def logout(request: Request):
    # Remove the user
    request.session.pop('user', None)
    request.session.pop('photourl', None)
    request.session.pop('username', None)
    request.session.pop('login_status', None)

    return RedirectResponse(url='/')


@app.get('/cif_search', tags=['Web Interface'])
async def cif_search(request: Request, user: Optional[dict] = Depends(get_user)):
    """
        Route function for cif search.

        Returns
        -------
        render_template
            Renders the cif search page.
        """
    return templates.TemplateResponse('cif_search.html',
                                      {"request": request, "user": request.session.get('username'),
                                       "img": request.session.get('photourl'),
                                       "result": None
                                       })


@app.post('/cif_search', tags=['Web Interface'])
async def upload_data_cif(request: Request, user_input: bytes = File(...), wavelength: str = Form(...),
                    filter_key: str = Form(None), filter_value: str = Form(None),
                    datatype: Literal["twotheta", "q"] = Form(...), user: Optional[dict] = Depends(get_user)):
    db_client = await mongo_client.get_db_client()
    db = db_client.test
    ranks = await rank_db_cifs(db, datatype, wavelength, user_input, filter_key, filter_value)
    result = rank_write(ranks).replace('\t\t', '&emsp;&emsp;&emsp;&emsp;&emsp;')
    return templates.TemplateResponse('cif_search.html',
                                      {"request": request, "user": request.session.get('username'),
                                       "img": request.session.get('photourl'),
                                       "result": result.replace('\t', '&emsp;&emsp;')
                                       })


@app.route('/prepare_data_viz_cif')
def prepare_data_viz_cif(request: Request, user: Optional[dict] = Depends(get_user)):
    pass


@app.route('/cif_results')
async def data_viz_cif_search(request: Request, user: Optional[dict] = Depends(get_user)):
    # fig1 = plotting
    # creates an in-memory buffer in which to store the file
    file_object1 = io.BytesIO()
    # fig1.savefig(file_object1, format='png')
    # encodes byte object so it can be embedded directly in html
    base64img1 = "data:image/png;base64," + base64.b64encode(file_object1.getvalue()).decode('ascii')
    return templates.TemplateResponse('cif_search_visualization.html',
                                      {"request": request, "user": request.session.get('user'), "img": request.session.get('photourl'),
                                       "base64img1": base64img1})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)