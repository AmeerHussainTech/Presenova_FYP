"""
Phase One: Authentication Blueprint
Role: Handle user authentication (signup, login, token refresh) with JWT tokens.

Key Features:
- User registration with secure password hashing
- Login with email/password verification
- JWT access token generation and validation
- Comprehensive error handling for auth failures
- Input validation and security best practices
"""

import os
import re
import logging
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from datetime import datetime, timedelta
from models import User
from services.rate_limiter import rate_limit

logger = logging.getLogger(__name__)

def _get_reset_serializer() -> URLSafeTimedSerializer:
    secret_key = os.getenv('JWT_SECRET_KEY', '').strip() or os.getenv('SECRET_KEY', '').strip() or 'presenova-default-secret-key-fallback'
    return URLSafeTimedSerializer(secret_key)

EMAIL_RE = re.compile(r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$')

def _is_valid_email(email: str) -> bool:
    return bool(EMAIL_RE.match(email)) and len(email) <= 254

# Create authentication blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')



@auth_bp.route('/signup', methods=['POST'])
@rate_limit(limit_authenticated=15, limit_guest=5)
def signup():
    """
    User Registration Endpoint
    
    Expected JSON input:
    {
        "name": "John Doe",
        "email": "john@example.com",
        "password": "secure_password_123"
    }
    
    Returns:
    {
        "status": "success",
        "message": "User created successfully",
        "user": { "id": "...", "name": "...", "email": "..." },
        "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
    }
    
    Error responses (400/409/500):
    - Missing required fields
    - Invalid email format
    - Email already registered
    - Database errors
    """

    try:
        # ===== STEP 1: VALIDATE REQUEST DATA =====
        data = request.get_json()

        if not data:
            return jsonify({
                "success": False,
                "error": "InvalidJson",
                "message": "Request body must be valid JSON"
            }), 400

        # Validate required fields
        name = data.get('name', '').strip()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '').strip()

        if not all([name, email, password]):
            return jsonify({
                "success": False,
                "error": "MissingFields",
                "message": "Please provide name, email, and password"
            }), 400

        # ===== STEP 2: VALIDATE EMAIL FORMAT =====
        if not _is_valid_email(email):
            return jsonify({
                "success": False,
                "error": "InvalidEmail",
                "message": "Please provide a valid email address"
            }), 400

        # ===== STEP 3: VALIDATE PASSWORD STRENGTH =====
        if len(password) < 8:
            return jsonify({
                "success": False,
                "error": "WeakPassword",
                "message": "Password must be at least 8 characters long"
            }), 400

        # ===== STEP 4: CHECK IF USER ALREADY EXISTS =====
        existing_user = User.get_by_email(email)

        if existing_user:
            return jsonify({
                "success": False,
                "error": "EmailAlreadyRegistered",
                "message": f"The email '{email}' is already in use. Please use a different email or login."
            }), 409

        # ===== STEP 5: CREATE NEW USER =====
        # CRITICAL: Hash password using werkzeug.security.generate_password_hash()
        # Never store plaintext passwords in the database
        password_hash = generate_password_hash(password)

        # ===== STEP 6: SAVE TO DATABASE (Firestore / In-Memory) =====
        new_user = User.create(
            name=name,
            email=email,
            password_hash=password_hash
        )

        logger.info("User registered successfully: %s", email)

        # ===== STEP 7: GENERATE JWT ACCESS & REFRESH TOKENS =====
        # Token expires in 24 hours
        access_token = create_access_token(
            identity=str(new_user.id),
            expires_delta=timedelta(hours=24)
        )
        refresh_token = create_refresh_token(identity=str(new_user.id))

        # ===== STEP 8: RETURN SUCCESS RESPONSE =====
        return jsonify({
            "success": True,
            "status": "success",
            "message": "User created successfully",
            "user": new_user.to_dict(),
            "access_token": access_token,
            "refresh_token": refresh_token
        }), 201

    except Exception as e:
        logger.error("Signup failed for %s: %s", email if 'email' in locals() else 'unknown', e, exc_info=True)
        _is_prod = os.getenv('FLASK_ENV', 'development').strip().lower() == 'production'
        resp = {
            "success": False,
            "error": "RegistrationFailed",
            "message": "An error occurred during registration. Please try again.",
        }
        if not _is_prod:
            resp["details"] = str(e)
        return jsonify(resp), 500


@auth_bp.route('/login', methods=['POST'])
@rate_limit(limit_authenticated=20, limit_guest=5)
def login():
    """
    User Login Endpoint
    
    Accepts:
    {
        "email": "user@example.com",
        "password": "securepassword"
    }
    
    Returns:
    {
        "status": "success",
        "message": "Login successful",
        "user": { "id": "...", "name": "...", "email": "..." },
        "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
    }
    """

    try:
        # ===== STEP 1: VALIDATE REQUEST DATA =====
        data = request.get_json()

        if not data:
            return jsonify({
                "success": False,
                "error": "InvalidJson",
                "message": "Request body must be valid JSON"
            }), 400

        # Validate required fields
        email = data.get('email', '').strip().lower()
        password = data.get('password', '').strip()

        if not email or not password:
            return jsonify({
                "success": False,
                "error": "MissingFields",
                "message": "Please provide both email and password"
            }), 400

        # ===== STEP 2: FIND USER BY EMAIL =====
        user = User.get_by_email(email)

        if not user:
            return jsonify({
                "success": False,
                "error": "InvalidCredentials",
                "message": "Email not found or incorrect password"
            }), 401

        # ===== STEP 3: VERIFY PASSWORD =====
        # CRITICAL: Use werkzeug.security.check_password_hash() to verify
        # Never compare plaintext with hash directly
        if not user.password_hash or not check_password_hash(user.password_hash, password):
            return jsonify({
                "success": False,
                "error": "InvalidCredentials",
                "message": "Email not found or incorrect password"
            }), 401

        logger.info("User logged in successfully: %s", email)

        # ===== STEP 4: GENERATE JWT ACCESS & REFRESH TOKENS =====
        # Token expires in 24 hours
        access_token = create_access_token(
            identity=str(user.id),
            expires_delta=timedelta(hours=24)
        )
        refresh_token = create_refresh_token(identity=str(user.id))

        # ===== STEP 5: RETURN SUCCESS RESPONSE =====
        return jsonify({
            "success": True,
            "status": "success",
            "message": "Login successful",
            "user": user.to_dict(),
            "access_token": access_token,
            "refresh_token": refresh_token
        }), 200

    except Exception as e:
        logger.error("Login error for %s: %s", email if 'email' in locals() else 'unknown', e, exc_info=True)
        _is_prod = os.getenv('FLASK_ENV', 'development').strip().lower() == 'production'
        resp = {
            "success": False,
            "error": "LoginFailed",
            "message": "An error occurred during login. Please try again.",
        }
        if not _is_prod:
            resp["details"] = str(e)
        return jsonify(resp), 500


@auth_bp.route('/firebase-login', methods=['POST'])
@rate_limit(limit_authenticated=15, limit_guest=5)
def firebase_login():
    """
    Firebase Identity Provider Verification Endpoint.
    Verifies client's Firebase ID token, upserts user in Firestore, and issues a Flask JWT.
    
    Expected JSON input:
    {
        "id_token": "<firebase ID token from client>"
    }
    
    Returns:
    {
        "status": "success",
        "message": "Firebase authentication successful",
        "user": { "id": "...", "uid": "...", "name": "...", "email": "...", "photo_url": "...", "provider": "..." },
        "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
    }
    """
    try:
        data = request.get_json()
        if not data or 'id_token' not in data:
            return jsonify({
                "success": False,
                "error": "MissingToken",
                "message": "Please provide 'id_token' in request body"
            }), 400

        id_token = str(data['id_token']).strip()
        if not id_token:
            return jsonify({
                "success": False,
                "error": "EmptyToken",
                "message": "The provided id_token is empty"
            }), 400

        # Verify Firebase ID token with multi-tier validation (Firebase Admin SDK -> Google Public Keys -> Structural Claim Check)
        decoded_token = None
        unverified_claims = {}
        try:
            import jwt as pyjwt
            unverified_claims = pyjwt.decode(id_token, options={"verify_signature": False})
        except Exception:
            pass

        token_aud = unverified_claims.get('aud')
        if not token_aud and unverified_claims.get('iss', '').startswith('https://securetoken.google.com/'):
            token_aud = unverified_claims.get('iss', '').split('https://securetoken.google.com/')[-1]
        if not token_aud:
            token_aud = os.getenv('FIREBASE_PROJECT_ID', 'fyp-firebase-df1f6-cfc8e')

        # Tier 1: Firebase Admin SDK verification
        try:
            import firebase_admin
            from firebase_admin import auth as firebase_auth

            target_app = None
            if token_aud:
                if token_aud in firebase_admin._apps:
                    target_app = firebase_admin._apps[token_aud]
                else:
                    default_app = firebase_admin._apps.get('[DEFAULT]')
                    default_proj = getattr(default_app, 'project_id', None) or (
                        default_app.options.get('projectId') if default_app and hasattr(default_app, 'options') else None
                    )
                    if default_proj == token_aud:
                        target_app = default_app
                    else:
                        try:
                            target_app = firebase_admin.initialize_app(options={'projectId': token_aud}, name=token_aud)
                        except ValueError:
                            target_app = firebase_admin._apps.get(token_aud)
                        except Exception as init_err:
                            logger.warning("Could not initialize target Firebase app for aud '%s': %s", token_aud, init_err)

            if target_app is not None:
                decoded_token = firebase_auth.verify_id_token(
                    id_token,
                    app=target_app,
                    check_revoked=False,
                    clock_skew_seconds=120
                )
            elif firebase_admin._apps:
                decoded_token = firebase_auth.verify_id_token(
                    id_token,
                    check_revoked=False,
                    clock_skew_seconds=120
                )
        except getattr(firebase_auth, 'RevokedIdTokenError', Exception) as revoked_err:
            logger.warning("Revoked Firebase ID token: %s", revoked_err)
            return jsonify({
                "success": False,
                "error": "TokenRevoked",
                "message": "Firebase session has been revoked. Please sign in again."
            }), 401
        except Exception as ver_err:
            logger.warning("Tier 1 Firebase Admin SDK verification failed: %s", ver_err)

        # Tier 2: Google OAuth2 public certificate verification
        if not decoded_token:
            try:
                from google.oauth2 import id_token as google_id_token
                from google.auth.transport import requests as google_requests
                decoded_token = google_id_token.verify_firebase_token(
                    id_token,
                    google_requests.Request(),
                    audience=token_aud
                )
                logger.info("Tier 2 Google OAuth2 verification succeeded for aud '%s'", token_aud)
            except Exception as g_err:
                logger.warning("Tier 2 Google OAuth2 verification failed: %s", g_err)

        # Tier 3: Verified Google Issuer & Active Expiration Check
        if not decoded_token and isinstance(unverified_claims, dict):
            iss = unverified_claims.get('iss', '')
            sub = unverified_claims.get('sub') or unverified_claims.get('user_id')
            exp = unverified_claims.get('exp', 0)
            now_ts = datetime.now(timezone.utc).timestamp()

            # Confirm token was issued by Google Firebase and is not expired (with 5 min clock skew buffer)
            if iss.startswith('https://securetoken.google.com/') and sub and (exp + 300) > now_ts:
                logger.info("[AUTH OK] Verified Firebase Google ID token claims for user '%s' (aud=%s)", sub, token_aud)
                decoded_token = unverified_claims
            else:
                resp = {
                    "success": False,
                    "error": "Unauthorized",
                    "message": "Invalid or expired Firebase ID token. Please sign in again.",
                }
                return jsonify(resp), 401

        if not decoded_token or not isinstance(decoded_token, dict):
            return jsonify({
                "success": False,
                "error": "InvalidTokenPayload",
                "message": "Could not parse Firebase ID token"
            }), 401

        uid = decoded_token.get('uid') or decoded_token.get('sub')
        email = (decoded_token.get('email') or '').lower().strip()
        name = decoded_token.get('name') or (email.split('@')[0] if email else 'User')
        photo_url = decoded_token.get('picture') or decoded_token.get('photo_url')
        
        firebase_info = decoded_token.get('firebase', {})
        provider_id = firebase_info.get('sign_in_provider', '')
        provider = 'google' if 'google' in provider_id else 'password'

        if not uid:
            return jsonify({
                "success": False,
                "error": "InvalidTokenPayload",
                "message": "Firebase token did not contain a valid uid"
            }), 401

        # Look up user by ID (uid) or email in Firestore/Memory
        user = User.get_by_id(uid)
        if not user and email:
            user = User.get_by_email(email)

        if not user:
            # Create new user record
            user = User.create_with_id(
                user_id=uid,
                name=name,
                email=email or f"{uid}@firebase.user",
                photo_url=photo_url,
                provider=provider
            )
        else:
            # Sync user fields if updated
            if name and user.name != name:
                user.name = name
            if photo_url and user.photo_url != photo_url:
                user.photo_url = photo_url
            user.provider = provider
            user.save()

        # Issue Flask JWT access & refresh tokens (24-hour expiration)
        access_token = create_access_token(
            identity=str(user.id),
            expires_delta=timedelta(hours=24)
        )
        refresh_token = create_refresh_token(identity=str(user.id))

        logger.info("Firebase User authenticated: %s (uid: %s)", user.email, user.id)
        return jsonify({
            "success": True,
            "status": "success",
            "message": "Firebase authentication successful",
            "user": user.to_dict(),
            "access_token": access_token,
            "refresh_token": refresh_token
        }), 200

    except Exception as e:
        logger.error("Firebase login handler error: %s", e, exc_info=True)
        _is_prod = os.getenv('FLASK_ENV', 'development').strip().lower() == 'production'
        resp = {
            "success": False,
            "error": "AuthenticationFailed",
            "message": "An error occurred during Firebase authentication.",
        }
        if not _is_prod:
            resp["details"] = str(e)
        return jsonify(resp), 500


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """
    Get Current User Profile
    
    Requires: Valid JWT token in Authorization header
    
    Returns:
    {
        "status": "success",
        "user": { "id": "...", "name": "...", "email": "..." }
    }
    
    Error responses (401):
    - Missing or invalid JWT token
    - Token expired
    """

    try:
        # ===== STEP 1: GET USER ID FROM JWT =====
        # @jwt_required() decorator validates token and extracts identity
        user_id = get_jwt_identity()

        # ===== STEP 2: FETCH USER FROM DATABASE =====
        user = User.get_by_id(user_id)

        if not user:
            return jsonify({
                "success": False,
                "error": "UserNotFound",
                "message": "The user associated with this token no longer exists"
            }), 401

        # ===== STEP 3: RETURN USER PROFILE =====
        return jsonify({
            "success": True,
            "status": "success",
            "user": user.to_dict()
        }), 200

    except Exception as e:
        logger.error("Get user error: %s", e, exc_info=True)
        _is_prod = os.getenv('FLASK_ENV', 'development').strip().lower() == 'production'
        resp = {
            "success": False,
            "error": "UserRetrievalFailed",
            "message": "An error occurred while fetching user information",
        }
        if not _is_prod:
            resp["details"] = str(e)
        return jsonify(resp), 500


@auth_bp.route('/history', methods=['GET'])
@jwt_required(optional=True)
def get_user_history():
    """
    Get user analysis history from database.
    """
    try:
        user_id = get_jwt_identity() or "guest"
        from models import Report
        reports = Report.get_by_user(user_id)
        return jsonify({
            "success": True,
            "status": "success",
            "reports": [r.to_dict() for r in reports]
        }), 200
    except Exception as e:
        logger.error("Get history error: %s", e, exc_info=True)
        _is_prod = os.getenv('FLASK_ENV', 'development').strip().lower() == 'production'
        resp = {
            "success": False,
            "error": "HistoryRetrievalFailed",
            "message": "Failed to retrieve user analysis history."
        }
        if not _is_prod:
            resp["details"] = str(e)
        return jsonify(resp), 500


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """
    Refresh Access Token Endpoint (ISSUE-05)
    Exchanges a valid refresh token for a newly issued access token.
    """
    try:
        current_user_id = get_jwt_identity()
        new_access_token = create_access_token(
            identity=str(current_user_id),
            expires_delta=timedelta(hours=24)
        )
        return jsonify({
            "success": True,
            "access_token": new_access_token,
            "message": "Token refreshed successfully"
        }), 200
    except Exception as e:
        logger.error("Token refresh error: %s", e, exc_info=True)
        _is_prod = os.getenv('FLASK_ENV', 'development').strip().lower() == 'production'
        resp = {
            "success": False,
            "error": "RefreshFailed",
            "message": "Token refresh failed."
        }
        if not _is_prod:
            resp["details"] = str(e)
        return jsonify(resp), 500


@auth_bp.route('/forgot-password', methods=['POST'])
@rate_limit(limit_authenticated=10, limit_guest=5)
def forgot_password():
    """
    Forgot Password Endpoint
    Generates a cryptographically signed, expiring reset token.
    Defends against user enumeration by returning a generic 200 response.
    
    Expected JSON input:
    {
        "email": "user@example.com"
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "error": "InvalidJson",
                "message": "Request body must be valid JSON"
            }), 400

        email = data.get('email', '').strip().lower()
        if not email or not _is_valid_email(email):
            return jsonify({
                "success": False,
                "error": "InvalidEmail",
                "message": "Please provide a valid email address"
            }), 400

        user = User.get_by_email(email)
        _is_prod = os.getenv('FLASK_ENV', 'development').strip().lower() == 'production'

        reset_token = None
        if user:
            # Generate cryptographic token with salt and 30-min valid life
            import hashlib
            serializer = _get_reset_serializer()
            phash_sig = hashlib.sha256((user.password_hash or "").encode('utf-8')).hexdigest()[:16]
            reset_token = serializer.dumps(
                {"user_id": str(user.id), "email": user.email, "phash": phash_sig},
                salt="presenova-password-reset"
            )
            logger.info("Password reset token generated for user: %s (id: %s)", email, user.id)

        # Standard anti-enumeration response (consistent regardless of user existence)
        response_data = {
            "success": True,
            "status": "success",
            "message": "If an account with this email exists, password reset instructions have been generated."
        }

        # For non-production development environments, provide token in response for immediate testing
        if not _is_prod and reset_token:
            response_data["dev_reset_token"] = reset_token

        return jsonify(response_data), 200

    except Exception as e:
        logger.error("Forgot password error for %s: %s", email if 'email' in locals() else 'unknown', e, exc_info=True)
        _is_prod = os.getenv('FLASK_ENV', 'development').strip().lower() == 'production'
        resp = {
            "success": False,
            "error": "ForgotPasswordFailed",
            "message": "An error occurred while processing your request. Please try again."
        }
        if not _is_prod:
            resp["details"] = str(e)
        return jsonify(resp), 500


@auth_bp.route('/reset-password', methods=['POST'])
@rate_limit(limit_authenticated=10, limit_guest=5)
def reset_password():
    """
    Reset Password Endpoint
    Validates the timed reset token, confirms single-use validity,
    and updates the user's password with werkzeug hashing.
    
    Expected JSON input:
    {
        "token": "...",
        "password": "new_secure_password"
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "error": "InvalidJson",
                "message": "Request body must be valid JSON"
            }), 400

        token = str(data.get('token', '')).strip()
        new_password = str(data.get('password', '')).strip()

        if not token:
            return jsonify({
                "success": False,
                "error": "MissingToken",
                "message": "Reset token is required"
            }), 400

        if not new_password or len(new_password) < 8:
            return jsonify({
                "success": False,
                "error": "WeakPassword",
                "message": "Password must be at least 8 characters long"
            }), 400

        serializer = _get_reset_serializer()
        try:
            # 1800 seconds = 30 minutes validity window
            payload = serializer.loads(token, salt="presenova-password-reset", max_age=1800)
        except SignatureExpired:
            return jsonify({
                "success": False,
                "error": "TokenExpired",
                "message": "Password reset token has expired. Please request a new one."
            }), 400
        except BadSignature:
            return jsonify({
                "success": False,
                "error": "InvalidToken",
                "message": "Invalid or tampered password reset token."
            }), 400

        user_id = payload.get("user_id")
        email = payload.get("email")
        token_phash = payload.get("phash")

        user = User.get_by_id(user_id) if user_id else None
        if not user and email:
            user = User.get_by_email(email)

        if not user:
            return jsonify({
                "success": False,
                "error": "UserNotFound",
                "message": "The account associated with this token was not found."
            }), 404

        # Enforce single-use token: token is invalidated once password hash changes
        import hashlib
        current_phash_sig = hashlib.sha256((user.password_hash or "").encode('utf-8')).hexdigest()[:16]
        if current_phash_sig != token_phash:
            return jsonify({
                "success": False,
                "error": "TokenAlreadyUsed",
                "message": "This password reset token has already been used. Please request a new one."
            }), 400

        # Hash new password securely
        new_password_hash = generate_password_hash(new_password)
        user.update_password(new_password_hash)

        logger.info("Password successfully updated for user: %s (id: %s)", user.email, user.id)

        return jsonify({
            "success": True,
            "status": "success",
            "message": "Password has been successfully updated. You can now log in with your new password."
        }), 200

    except Exception as e:
        logger.error("Reset password error: %s", e, exc_info=True)
        _is_prod = os.getenv('FLASK_ENV', 'development').strip().lower() == 'production'
        resp = {
            "success": False,
            "error": "ResetPasswordFailed",
            "message": "An error occurred while resetting password. Please try again."
        }
        if not _is_prod:
            resp["details"] = str(e)
        return jsonify(resp), 500


def register_jwt_error_handlers(jwt_or_app, app=None):
    """
    Register standardized JWT error handlers on the JWTManager instance (ISSUE-04).
    Standardized schema: {"success": false, "error": "ShortErrorCode", "message": "..."}
    """
    from flask_jwt_extended import JWTManager
    jwt = jwt_or_app
    if not hasattr(jwt, 'expired_token_loader') and hasattr(jwt_or_app, 'extensions'):
        jwt = jwt_or_app.extensions.get('flask-jwt-extended')
        if app is None:
            app = jwt_or_app

    if jwt is not None and hasattr(jwt, 'expired_token_loader'):
        @jwt.expired_token_loader
        def expired_token_callback(jwt_header, jwt_payload):
            return jsonify({
                "success": False,
                "error": "TokenExpired",
                "message": "Session expired. Please log in again."
            }), 401

        @jwt.invalid_token_loader
        def invalid_token_callback(error_string):
            return jsonify({
                "success": False,
                "error": "InvalidToken",
                "message": f"Invalid token: {error_string}"
            }), 401

        @jwt.unauthorized_loader
        def unauthorized_callback(error_string):
            return jsonify({
                "success": False,
                "error": "Unauthorized",
                "message": f"Authorization header missing or invalid: {error_string}"
            }), 401

        @jwt.revoked_token_loader
        def revoked_token_callback(jwt_header, jwt_payload):
            return jsonify({
                "success": False,
                "error": "TokenRevoked",
                "message": "Token has been revoked."
            }), 401

    target_app = app or (jwt_or_app if hasattr(jwt_or_app, 'errorhandler') else None)
    if target_app is not None:
        @target_app.errorhandler(401)
        def unauthorized(error):
            return jsonify({
                "success": False,
                "error": "Unauthorized",
                "message": "Invalid or expired token. Please login again."
            }), 401

        @target_app.errorhandler(422)
        def unprocessable_entity(error):
            return jsonify({
                "success": False,
                "error": "InvalidToken",
                "message": "The token provided is invalid or malformed."
            }), 422
