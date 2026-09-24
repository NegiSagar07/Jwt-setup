🚀 JWT Auth Template (FastAPI + MongoDB/Beanie, async)

## Layout
```
app/
  config.py        # Settings (.env) -> MONGODB_URI, MONGODB_DB_NAME, JWT, SMTP/SES settings
  db.py             # Motor client, init_db() (Beanie init), check_database_health()
  security.py       # password hashing (bcrypt), JWT creation, OTP generation
  models/user.py    # Beanie Document User model (incl. password-reset OTP fields)
  schemas/user.py   # UserCreate, UserResponse, Token, change/forgot/reset-password schemas
  crud/user.py      # get_user_by_email, get_user_by_id, create_user, update_password, OTP helpers
  email/
    base.py         # EmailSender interface — the only contract callers depend on
    smtp.py         # SMTPEmailSender (active today)
    ses.py          # SESEmailSender stub — fill in when switching to Amazon SES
    __init__.py     # get_email_sender() picks a backend by EMAIL_PROVIDER; send_password_reset_otp_email()
  router/
    auth.py         # /auth/signup, /auth/login, /auth/change-password,
                     # /auth/forgot-password, /auth/reset-password
    health.py        # /health (database connectivity check)
  dependency.py      # get_current_user (JWT -> User)
  main.py            # FastAPI app wiring everything together
```

## Setup
1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
2. Copy `.env.example` to `.env` and fill in your MongoDB Atlas
   connection string (Atlas dashboard -> Connect -> Drivers), a
   generated `SECRET_KEY` (`openssl rand -hex 32`), and SMTP credentials
   (for Gmail, use an App Password, not your login password).
3. Run it:
   ```
   uvicorn app.main:app --reload
   ```
   On startup Beanie is initialized against the `users` collection
   (created automatically on first insert — no manual migration needed).

## Endpoints
- `POST /auth/signup` — body: `{"email": ..., "password": ...}` → `UserResponse`
- `POST /auth/login` — form-encoded `username`/`password` (OAuth2 password flow) → `Token`
- `GET /users/me` — Bearer token required → `UserResponse`
- `POST /auth/change-password` — Bearer token required, body: `{"old_password": ..., "new_password": ...}`
- `POST /auth/forgot-password` — body: `{"email": ...}` → always returns a generic
  message (doesn't leak whether the email is registered); emails a 6-digit OTP if it is
- `POST /auth/reset-password` — body: `{"email": ..., "otp": ..., "new_password": ...}`
- `GET /health` — pings MongoDB, returns 200 or 503

## Switching the email provider to Amazon SES later
Nothing outside `app/email/` needs to change:
1. `pip install aioboto3`, add it to `requirements.txt`.
2. Fill in `app/email/ses.py` (stub already sketched out there) and add
   AWS settings to `config.py` (commented placeholders already there).
3. In `app/email/__init__.py`, register `"ses"` in `get_email_sender()`.
4. Set `EMAIL_PROVIDER=ses` in `.env`.
`router/auth.py` only calls `send_password_reset_otp_email()`, which is
provider-agnostic, so no call sites change.

## Using this in a bigger project
If dropping this into an existing project, either:
- keep this whole `app/` folder as your app package, or
- merge `models/user.py`, `schemas/user.py`, `crud/user.py` into your
  existing equivalents, and adjust the imports in `router/auth.py`,
  `dependency.py`, `email/`, and `db.py` accordingly.
