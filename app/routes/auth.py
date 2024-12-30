from flask import Blueprint, request, jsonify
from app.models import db, User
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
from datetime import timedelta

auth_bp = Blueprint('auth', __name__, url_prefix="/auth")

def require_admin():
    """Helper funksjon for å sjekke admin-tilgang"""
    claims = get_jwt()
    if not claims or claims.get('role') != 'admin':
        return jsonify({"message": "Admin access required"}), 403
    return None

@auth_bp.route('/register', methods=['POST'])
@jwt_required(optional=True)
def register():
    """
    Register a new user
    ---
    tags:
      - Authentication
    parameters:
      - in: body
        name: user
        description: User to create
        required: true
        schema:
          type: object
          required:
            - username
            - password
          properties:
            username:
              type: string
              example: testuser
            password:
              type: string
              example: test-123
            role:
              type: string
              enum: [admin, user]
              default: user
              example: user
    responses:
      201:
        description: User created successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: User created successfully
            user:
              type: object
              properties:
                username:
                  type: string
                role:
                  type: string
      400:
        description: Invalid request
      403:
        description: Forbidden - only admin can create admin users
      415:
        description: Invalid content type
    """
    if not request.is_json:
        return jsonify({"message": "Content-Type must be application/json"}), 415

    data = request.get_json()
    
    if not data or not all(k in data for k in ('username', 'password')):
        return jsonify({"message": "Username and password are required"}), 400

    # Valider brukernavn
    username = data['username'].strip()
    if not username or len(username) < 3:
        return jsonify({"message": "Username must be at least 3 characters"}), 400

    # Valider passord
    password = data['password']
    if len(password) < 8:
        return jsonify({"message": "Password must be at least 8 characters"}), 400

    # Sjekk om brukernavn allerede eksisterer
    if User.query.filter_by(username=username).first():
        return jsonify({"message": "Username already exists"}), 400

    # Håndter rolletilordning
    requested_role = data.get('role', 'user')
    claims = get_jwt() if get_jwt_identity() else None
    
    # Bare admin kan opprette admin-brukere
    if requested_role == 'admin' and (not claims or claims.get('role') != 'admin'):
        return jsonify({"message": "Only admin can create admin users"}), 403

    user = User(
        username=username,
        role=requested_role
    )
    user.set_password(password)
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({
        "message": "User created successfully",
        "user": {
            "username": user.username,
            "role": user.role
        }
    }), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Log in a user
    ---
    tags:
      - Authentication
    parameters:
      - in: body
        name: credentials
        required: true
        schema:
          type: object
          required:
            - username
            - password
          properties:
            username:
              type: string
              example: testuser
            password:
              type: string
              example: test-123
    responses:
      200:
        description: Login successful
        schema:
          type: object
          properties:
            access_token:
              type: string
            token_type:
              type: string
              example: Bearer
            expires_in:
              type: integer
              example: 86400
            user:
              type: object
              properties:
                username:
                  type: string
                role:
                  type: string
      400:
        description: Missing credentials
      401:
        description: Invalid credentials
      415:
        description: Invalid content type
    """
    if not request.is_json:
        return jsonify({"message": "Content-Type must be application/json"}), 415

    data = request.get_json()
    
    if not data or not all(k in data for k in ('username', 'password')):
        return jsonify({"message": "Username and password are required"}), 400

    user = User.query.filter_by(username=data['username'].strip()).first()
    if not user or not user.check_password(data['password']):
        return jsonify({"message": "Invalid credentials"}), 401

    # Opprett token med brukerinfo og utløpstid
    expires = timedelta(days=1)
    access_token = create_access_token(
        identity=user.username,
        additional_claims={'role': user.role},
        expires_delta=expires
    )
    
    return jsonify({
        "message": "Login successful",
        "access_token": access_token,
        "token_type": "Bearer",
        "expires_in": expires.total_seconds(),
        "user": {
            "username": user.username,
            "role": user.role
        }
    }), 200

@auth_bp.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    """
    Get all users (Admin only)
    ---
    tags:
      - Authentication
    security:
      - Bearer: []
    responses:
      200:
        description: List of all users
        schema:
          type: array
          items:
            type: object
            properties:
              username:
                type: string
              role:
                type: string
      401:
        description: Unauthorized
      403:
        description: Forbidden - admin access required
    """
    # Sjekk admin-tilgang
    admin_check = require_admin()
    if admin_check:
        return admin_check

    users = User.query.all()
    return jsonify([{
        "username": user.username,
        "role": user.role,
        "created_at": user.created_at.isoformat() if hasattr(user, 'created_at') else None
    } for user in users])

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    """
    Get user profile
    ---
    tags:
      - Authentication
    security:
      - Bearer: []
    responses:
      200:
        description: User profile
        schema:
          type: object
          properties:
            username:
              type: string
            role:
              type: string
            last_login:
              type: string
              format: date-time
      401:
        description: Missing or invalid token
      404:
        description: User not found
    """
    username = get_jwt_identity()
    user = User.query.filter_by(username=username).first()
    
    if not user:
        return jsonify({"message": "User not found"}), 404
        
    return jsonify({
        "username": user.username,
        "role": user.role,
        "last_login": user.last_login.isoformat() if hasattr(user, 'last_login') else None
    })

@auth_bp.route('/users/<username>', methods=['PUT'])
@jwt_required()
def update_user(username):
    """
    Update user (Admin or self only)
    ---
    tags:
      - Authentication
    security:
      - Bearer: []
    parameters:
      - name: username
        in: path
        type: string
        required: true
        description: Username to update
      - in: body
        name: user
        required: true
        schema:
          type: object
          properties:
            role:
              type: string
              enum: [admin, user]
            password:
              type: string
              minLength: 8
    responses:
      200:
        description: User updated successfully
      400:
        description: Invalid request
      403:
        description: Forbidden
      404:
        description: User not found
    """
    current_identity = get_jwt_identity()
    claims = get_jwt()
    
    # Bruker kan bare oppdatere seg selv, med mindre det er admin
    if current_identity != username and claims.get('role') != 'admin':
        return jsonify({"message": "Forbidden"}), 403

    user = User.query.filter_by(username=username).first_or_404()
    data = request.get_json()

    # Valider og oppdater passord
    if 'password' in data:
        if len(data['password']) < 8:
            return jsonify({"message": "Password must be at least 8 characters"}), 400
        user.set_password(data['password'])

    # Bare admin kan endre roller
    if 'role' in data:
        if claims.get('role') != 'admin':
            return jsonify({"message": "Only admin can change roles"}), 403
        # Admin kan ikke degradere seg selv
        if user.username == current_identity and data['role'] != 'admin':
            return jsonify({"message": "Admin cannot remove their own admin role"}), 403
        user.role = data['role']

    db.session.commit()

    return jsonify({
        "message": "User updated successfully",
        "user": {
            "username": user.username,
            "role": user.role
        }
    })

@auth_bp.route('/users/<username>', methods=['DELETE'])
@jwt_required()
def delete_user(username):
    """
    Delete user (Admin only)
    ---
    tags:
      - Authentication
    security:
      - Bearer: []
    parameters:
      - name: username
        in: path
        type: string
        required: true
        description: Username to delete
    responses:
      200:
        description: User deleted successfully
      400:
        description: Bad request - cannot delete yourself
      403:
        description: Forbidden - admin access required
      404:
        description: User not found
    """
    # Sjekk admin-tilgang
    admin_check = require_admin()
    if admin_check:
        return admin_check

    current_username = get_jwt_identity()
    if username == current_username:
        return jsonify({"message": "Cannot delete yourself"}), 400

    user = User.query.filter_by(username=username).first_or_404()
    
    # Slett alle relaterte data først (kommentarer, albums, etc.)
    # TODO: Implementer sletting av relatert data
    
    db.session.delete(user)
    db.session.commit()

    return jsonify({"message": "User deleted successfully"})