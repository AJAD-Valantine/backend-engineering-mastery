from fastapi import Depends, FastAPI, Request, Form, status 
from fastapi.exceptions import RequestValidationError 
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse

from sqlalchemy import select
from sqlalchemy.orm import Session

from starlette.exceptions import HTTPException as StarletteHTTPException

from model import Tickets
from database import Base, engine, get_db

from typing import Annotated

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

@app.get("/")
def home(request : Request, db: Annotated[Session, Depends(get_db)]):
    
    tickets = db.execute(select(Tickets)).scalars().all()

    total_tickets = len(tickets)
    open_tickets = len([ticket for ticket in tickets if ticket.status == "Open"])
    in_progress_tickets = len([ticket for ticket in tickets if ticket.status == "In Progress"])
    resolved_tickets = len([ticket for ticket in tickets if ticket.status == "Resolved"])

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"request" : request,
                 "total_tickets": total_tickets, 
                 "open_tickets" : open_tickets,
                 "in_progress_tickets" : in_progress_tickets,
                 "resolved_tickets" : resolved_tickets}
    )

@app.get("/tickets")
def view_all_tickets(request : Request, db: Annotated[Session, Depends(get_db)]):
    
    tickets = db.execute(select(Tickets)).scalars().all()

    return templates.TemplateResponse(
        request=request,
        name="ticket_list.html",
        context={"request" : request,
                 "tickets" : tickets}
                 )

@app.get("/tickets/new")
def get_ticket_form(request: Request):
    
    return templates.TemplateResponse(
        request=request,
        name="ticket_create.html",
        context={"request": request}
    ) 

@app.post("/tickets/new")
def send_ticket_form(
    request: Request, 
    db: Annotated[Session, Depends(get_db)],

    requester_name: str = Form(...),
    email: str = Form(...),
    category: str = Form(...),
    title: str = Form(...),
    description: str = Form(...),
    priority: str = Form(...)
):
    
    new_ticket = Tickets(
        requester_name=requester_name,
        email=email,
        category=category,
        title=title,
        description=description,
        priority=priority
    )
    
    db.add(new_ticket)
    db.commit()
    db.refresh(new_ticket)
    
    return RedirectResponse(url="/tickets", status_code=303)

@app.get("/tickets/{ticket_id}")
def view_ticket_details(request: Request, ticket_id: int, db: Annotated[Session, Depends(get_db)]):

    ticket = db.execute(select(Tickets).where(Tickets.id == ticket_id)).scalar_one_or_none()

    if ticket is None:

        return templates.TemplateResponse(
            request=request,
            name="error.html",
            context={"request": request, "message": "Ticket not found"}
        )

    return templates.TemplateResponse(
        request=request,
        name="ticket_details.html",
        context={"request": request,
                 "ticket": ticket}
    )

@app.post("/tickets/{ticket_id}/status")
def update_status(request: Request, ticket_id: int, db: Annotated[Session, Depends(get_db)], status: str = Form(...)):

    ticket = db.execute(select(Tickets).where(Tickets.id == ticket_id)).scalar_one_or_none()

    if ticket is None:

        return templates.TemplateResponse(
            request=request,
            name="error.html",
            context={"request": request, "message": "Ticket not found"}
        )

    ticket.status = status
    db.commit()
    db.refresh(ticket)

    return RedirectResponse(url=f"/tickets/{ticket_id}", status_code=303)

@app.get("/tickets/{ticket_id}/edit")
def get_edit_page(request : Request, ticket_id : int, db: Annotated[Session, Depends(get_db)]):
    
    ticket = db.execute(select(Tickets).where(Tickets.id == ticket_id)).scalar_one_or_none()
    
    if ticket is None:
        
        return templates.TemplateResponse(
            request=request,
            name="error.html",
            context={"request": request, "message": "Ticket not found"}
        )

    return templates.TemplateResponse(
        request=request,
        name="ticket_edit.html",
        context={
            "request": request,
            "ticket": ticket
        }
    )

@app.post("/tickets/{ticket_id}/edit")
def get_post_page(    
    request: Request, 
    db: Annotated[Session, Depends(get_db)],
    ticket_id : int,

    requester_name: str = Form(...),
    email: str = Form(...),
    category: str = Form(...),
    title: str = Form(...),
    description: str = Form(...),
    priority: str = Form(...),
    status: str = Form(...)
):

    ticket = db.execute(select(Tickets).where(Tickets.id == ticket_id)).scalar_one_or_none()


    if ticket is None:

        return templates.TemplateResponse(
            request=request,
            name="error.html",
            context={"request": request, "message": "Ticket not found"}
        )
    
    ticket.requester_name = requester_name
    ticket.email = email
    ticket.category = category
    ticket.title = title
    ticket.description = description
    ticket.priority = priority
    ticket.status = status

    db.commit()
    db.refresh(ticket)

    return RedirectResponse(url="/tickets", status_code=303)


@app.get("/tickets/{ticket_id}/delete")
def get_delete_page(request : Request, ticket_id : int, db: Annotated[Session, Depends(get_db)]):
    
    ticket = db.execute(select(Tickets).where(Tickets.id == ticket_id)).scalar_one_or_none()
    
    if ticket is None:
        
        return templates.TemplateResponse(
            request=request,
            name="error.html",
            context={"request": request, "message": "Ticket not found"}
        )

    return templates.TemplateResponse(
        request=request,
        name="ticket_delete.html",
        context={
            "request": request,
            "ticket": ticket
        }
    )

@app.post("/tickets/{ticket_id}/delete")
def delete_post_page(request: Request, db: Annotated[Session, Depends(get_db)], ticket_id : int):

    ticket = db.execute(select(Tickets).where(Tickets.id == ticket_id)).scalar_one_or_none()

    if ticket is None:

        return templates.TemplateResponse(
            request=request,
            name="error.html",
            context={"request": request, "message": "Ticket not found"}
        )
    
    db.delete(ticket)
    db.commit()

    return RedirectResponse(url="/tickets", status_code=303)

@app.exception_handler(StarletteHTTPException)
def http_exception_handler(request: Request, exception: StarletteHTTPException):

    message = (
        exception.detail
        if exception.detail
        else "An error occurred. Please check your request and try again."
    )

    return templates.TemplateResponse(
        request=request,
        name="error.html",
        context={
            "status_code": exception.status_code,
            "title": exception.status_code,
            "message": message,
        },
        status_code=exception.status_code,
    )


@app.exception_handler(RequestValidationError)
def validation_exception_handler(request: Request, exception: RequestValidationError):

    return templates.TemplateResponse(
        request=request,
        name="error.html",
        context={
            "status_code": status.HTTP_422_UNPROCESSABLE_CONTENT,
            "title": status.HTTP_422_UNPROCESSABLE_CONTENT,
            "message": "Invalid request. Please check your input and try again.",
        },
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
    )