import os
from pathlib import Path
import yaml
import tempfile
import shutil
import uuid
import io
import base64
import asyncio
from asyncio import BoundedSemaphore

from fastapi import FastAPI, Body, HTTPException, status, File, Depends
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from starlette.config import Config as Configure
from starlette.requests import Request
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import HTMLResponse, RedirectResponse

from authlib.integrations.starlette_client import OAuth

from typing import List, Optional, Literal

import motor.motor_asyncio

from pydatarecognition.powdercif import PydanticPowderCif
from pydatarecognition.utils import xy_resample
from pydatarecognition.cif_io import user_input_read

from skbeam.core.utils import twotheta_to_q

import scipy.stats

import numpy as np

import psutil

filepath = Path(os.path.abspath(__file__))

STEPSIZE_REGULAR_QGRID = 10**-3

COLLECTION = "cif"
MAX_MONGO_FIND = 1000000

app = FastAPI(docs_url=None, redoc_url=None)
app.mount("/static", StaticFiles(directory="static"), name="static")
app.add_middleware(SessionMiddleware, secret_key='!secret')
templates = Jinja2Templates(directory="templates")

# Connect to mongodb

with open(os.path.join(filepath.parent, 'secret_password.yml'), 'r') as f:
    user_secrets = yaml.safe_load(f)
username = user_secrets['username']
password = user_secrets['password']
client = motor.motor_asyncio.AsyncIOMotorClient(f'mongodb+srv://{username}:{password}@sidewinder.uc5ro.mongodb.net/?retryWrites=true&w=majority')
db = client.test

# Setup cif mapping reference
CIF_DIR = filepath.parent.parent / 'docs' / 'examples' / 'cifs'
doifile = CIF_DIR / 'iucrid_doi_mapping.txt'
dois = np.genfromtxt(doifile, dtype='str')
doi_dict = {}
for i in range(len(dois)):
    doi_dict[dois[i][0]] = dois[i][1]

# Create an app level semaphore to prevent overloading the RAM. Assume ~100KB per cif, *5000 = 0.5GB
semaphore = BoundedSemaphore(5000)

@app.route('/')
async def home(request: Request):
    # user = request.session.get('user')
    # if user is not None:
    #     email = user['email']
    #     html = (
    #         f'<pre>Email: {email}</pre><br>'
    #         '<a href="/docs">documentation</a><br>'
    #         '<a href="/logout">logout</a>'
    #     )
    #     return HTMLResponse(html)
    if request.session.get('login_status'):
        if request.session['login_status'] == "authorized":
            return templates.TemplateResponse('landing.html',
                                              {"request": request, "user": request.session.get('username'), "img": request.session.get('photourl')})
        else:
            return templates.TemplateResponse('landing.html', {"request": request, "user": None})
    else:
         return templates.TemplateResponse('landing.html', {"request": request, "user": None})

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

    return templates.TemplateResponse('login.html')


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

    return RedirectResponse(url='/')


# @app.post("/", response_description="Add new CIF", response_model=PydanticPowderCif)
# async def create_cif(powdercif: PydanticPowderCif = Body(...)):
#     powdercif = jsonable_encoder(powdercif)
#     new_cif = await db[COLLECTION].insert_one(powdercif)
#     created_cif = await db[COLLECTION].find_one({"_id": new_cif.inserted_id})
#     return JSONResponse(status_code=status.HTTP_201_CREATED, content=created_cif)


# @app.get(
#     "/", response_description="List all cifs", response_model=List[PydanticPowderCif]
# )
# async def list_cifs():
#     cifs = await db[COLLECTION].find().to_list(5)
#     return cifs

# Try to get the logged in user
async def get_user(request: Request) -> Optional[dict]:
    user = request.session.get('user')
    if user is not None:
        return user
    else:
        raise HTTPException(status_code=403, detail='Could not validate credentials.')

    return None


@app.route('/openapi.json')
async def get_open_api_endpoint(request: Request, user: Optional[dict] = Depends(get_user)):  # This dependency protects our endpoint!
    response = JSONResponse(get_openapi(title='FastAPI', version=1, routes=app.routes))
    return response


@app.get('/docs', tags=['documentation'])  # Tag it as "documentation" for our docs
async def get_documentation(request: Request, user: Optional[dict] = Depends(get_user)):  # This dependency protects our endpoint!
    response = get_swagger_ui_html(openapi_url='/openapi.json', title='Documentation')
    return response


@app.get(
    "/{id}", response_description="Get a single CIF", response_model=PydanticPowderCif
)
async def show_cif(id: str):
    if (cif := await db[COLLECTION].find_one({"_id": id})) is not None:
        return cif

    raise HTTPException(status_code=404, detail=f"CIF {id} not found")


@app.put("/{id}", response_description="Update a CIF", response_model=PydanticPowderCif)
async def update_cif(id: str, cif: PydanticPowderCif = Body(...)):
    cif = {k: v for k, v in cif.dict().items() if v is not None}

    if len(cif) >= 1:
        update_result = await db[COLLECTION].update_one({"_id": id}, {"$set": cif})

        if update_result.modified_count == 1:
            if (
                updated_cif := await db[COLLECTION].find_one({"_id": id})
            ) is not None:
                return updated_cif

    if (existing_cif := await db[COLLECTION].find_one({"_id": id})) is not None:
        return existing_cif

    raise HTTPException(status_code=404, detail=f"CIF {id} not found")


@app.delete("/{id}", response_description="Delete a CIF")
async def delete_cif(id: str):
    delete_result = await db[COLLECTION].delete_one({"_id": id})

    if delete_result.deleted_count == 1:
        return JSONResponse(status_code=status.HTTP_204_NO_CONTENT)

    raise HTTPException(status_code=404, detail=f"CIF {id} not found")


@app.put(
    "/rank/", response_description="Rank matches to User Input Data", tags=['rank']
)
async def rank_cif(xtype: Literal["twotheta", "q"], wavelength: float, user_input: bytes = File(...), paper_filter_iucrid: Optional[str] = None):
    cifname_ranks = []
    r_pearson_ranks = []
    doi_ranks = []
    tempdir = tempfile.mkdtemp()
    temp_filename = os.path.join(tempdir, f'temp_{uuid.uuid4()}.txt')
    with open(temp_filename, 'wb') as w:
        w.write(user_input)
    userdata = user_input_read(temp_filename)
    user_x_data, user_intensity = userdata[0, :], userdata[1:, ][0]
    if xtype == 'twotheta':
        user_q = twotheta_to_q(np.radians(user_x_data), wavelength)
    else:
        user_q = user_x_data
    if paper_filter_iucrid:
        cif_cursor = db[COLLECTION].find({"iucrid": paper_filter_iucrid})
    else:
        cif_cursor = db[COLLECTION].find({})
    mem_premongo = psutil.virtual_memory().percent
    unpopulated_cif_list = await cif_cursor.to_list(length=MAX_MONGO_FIND)
    mem_postmongo = psutil.virtual_memory().percent
    print(f"Memory mongo_used in percent: {(mem_postmongo - mem_premongo)}")
    futures = [limited_cif_load(cif) for cif in unpopulated_cif_list]
    for future in asyncio.as_completed(futures):
        mongo_cif = await future
        try:
            data_resampled = xy_resample(user_q, user_intensity, mongo_cif.q, mongo_cif.intensity, STEPSIZE_REGULAR_QGRID)
            pearson = scipy.stats.pearsonr(data_resampled[0][:, 1], data_resampled[1][:, 1])
            r_pearson = pearson[0]
            cifname_ranks.append(mongo_cif.cif_file_name)
            r_pearson_ranks.append(r_pearson)
            doi = doi_dict[mongo_cif.iucrid]
            doi_ranks.append(doi)
        except AttributeError:
            print(f"{mongo_cif.cif_file_name} was skipped.")
        loop_mem = psutil.virtual_memory().percent
        print(f"Memory Used in loop in percent: {(loop_mem - mem_postmongo)}")
        semaphore.release()

    cif_rank_pearson = sorted(list(zip(cifname_ranks, r_pearson_ranks, doi_ranks)), key=lambda x: x[1], reverse=True)
    ranks = [{'IUCrCIF': cif_rank_pearson[i][0],
              'score': cif_rank_pearson[i][1],
              'doi': cif_rank_pearson[i][2]} for i in range(len(cif_rank_pearson))]
    shutil.rmtree(tempdir)
    return ranks

@app.route('/cif_search')
async def cif_search(request: Request, user: Optional[dict] = Depends(get_user)):
    """
        Route function for cif search.

        Returns
        -------
        render_template
            Renders the cif search page.
        """
    return templates.TemplateResponse('cif_search.html',
                                      {"request": request, "user": request.session.get('user'), "img": request.session.get('photourl')})

@app.route('/upload_data_cif', methods=['POST'])
def upload_data_cif(request: Request, user: Optional[dict] = Depends(get_user)):
    file = request.file.getlist('file')
    wavelength = request.form['wavelength']
    xtype = request.form['xtype']

    return request.url_for('prepare_data_viz_NMF')


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

# @app.route('/results_download')
# async def comparison_download(request: Request, user: Optional[dict] = Depends(get_user)):
#     return templates.TemplateResponse('cif_search_visualization.html',
#                                       {"request": request, "user": request.session.get('user'), "img": request.session.get('photourl')})


async def limited_cif_load(cif: dict):
    await semaphore.acquire()
    pcd = PydanticPowderCif(**cif)
    await pcd.resolve_gcs_tokens()
    return pcd

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
                                      {"request": request, "user": request.session.get('user'), "img": request.session.get('photourl')})


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
                                      {"request": request, "user": request.session.get('user'), "img": request.session.get('photourl')})


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
                                      {"request": request, "user": request.session.get('user'), "img": request.session.get('photourl')})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)