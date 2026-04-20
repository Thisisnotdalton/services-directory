from pathlib import Path
from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from app.utils.settings import get_settings, ServiceOptions

settings = get_settings()
app = FastAPI(root_path=settings.root_path, redirect_slashes=settings.redirect_slashes)
if settings.absolute_static_path and Path(settings.absolute_static_path).is_dir():
    app.mount("/static", StaticFiles(directory=settings.absolute_static_path), name="static")
templates = Jinja2Templates(directory=settings.absolute_templates_path)


@app.get("/")
async def root(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request, name="index.html", context={"settings": settings}
    )


@app.get("/services/", response_model=ServiceOptions)
async def get_service(request: Request):
    return ServiceOptions(services=settings.services)


@app.get("/services/{service_id}", response_class=RedirectResponse)
async def get_service(request: Request, service_id: str):
    if settings.case_insensitive:
        service_id = service_id.lower()
    if service_id not in settings.services:
        raise HTTPException(status_code=404, detail=f'Service not found: "{service_id}"')
    return RedirectResponse(settings.services[service_id].url)
