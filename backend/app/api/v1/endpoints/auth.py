import boto3
import hmac
import hashlib
import base64
from botocore.exceptions import ClientError
import logging
from fastapi import HTTPException,APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
# from api.v1.endpoints.payment import get_credits
from app.db.crud.credits import get_credits,add_credits
from app.db.base import get_db
from app.db.models.credits import Credits
from app.schemas.auth import SignUpRequest, AuthenticateUserRequest, ConfirmSignUpRequest
from app.core.config.settings import settings
logger = logging.getLogger(__name__)

class CognitoAuth:
    def __init__(self, user_pool_id, client_id, client_secret=None, region='us-east-1'):
        self.cognito_client = boto3.client('cognito-idp', region_name=region)
        self.user_pool_id = user_pool_id
        self.client_id = client_id
        self.client_secret = client_secret
    
    def _secret_hash(self, username):
        """Calculate secret hash if client secret is provided"""
        if not self.client_secret:
            return None
        key = self.client_secret.encode()
        msg = bytes(username + self.client_id, 'utf-8')
        return base64.b64encode(
            hmac.new(key, msg, digestmod=hashlib.sha256).digest()
        ).decode()

    # 1. USER REGISTRATION (SignUp)
    def sign_up(self, username, password, email, name=None):
        """
        Register a new user in Cognito User Pool
        Returns: Dict with UserSub and confirmation status
        """
        try:
            user_attributes = [
                {'Name': 'email', 'Value': email}
            ]
            if name:
                user_attributes.append({'Name': 'name', 'Value': name})
            
            kwargs = {
                'ClientId': self.client_id,
                'Username': username,
                'Password': password,
                'UserAttributes': user_attributes
            }
            
            if self.client_secret:
                kwargs['SecretHash'] = self._secret_hash(username)
            
            response = self.cognito_client.sign_up(**kwargs)
            
            return {
                'success': True,
                'user_sub': response['UserSub'],
                'user_confirmed': response['UserConfirmed'],
                'code_delivery_details': response.get('CodeDeliveryDetails', {})
            }
            
        except ClientError as e:
            logger.error(f"SignUp failed: {e.response['Error']['Code']} - {e.response['Error']['Message']}")
            return {'success': False, 'error': e.response['Error']}

    # 2. CONFIRM REGISTRATION (ConfirmSignUp)
    def confirm_sign_up(self, username, confirmation_code):
        """
        Confirm user registration with verification code
        Returns: Success status
        """
        try:
            kwargs = {
                'ClientId': self.client_id,
                'Username': username,
                'ConfirmationCode': confirmation_code
            }
            
            if self.client_secret:
                kwargs['SecretHash'] = self._secret_hash(username)
            
            self.cognito_client.confirm_sign_up(**kwargs)
            
            return {'success': True, 'message': 'User confirmed successfully'}
            
        except ClientError as e:
            logger.error(f"ConfirmSignUp failed: {e.response['Error']['Code']} - {e.response['Error']['Message']}")
            return {'success': False, 'error': e.response['Error']}

    # 3. USER AUTHENTICATION (AdminInitiateAuth)
    def authenticate_user(self, username, password):
        """
        Authenticate user with username and password
        Returns: Authentication result with tokens or challenge
        """
        try:
            kwargs = {
                'UserPoolId': self.user_pool_id,
                'ClientId': self.client_id,
                'AuthFlow': 'ADMIN_USER_PASSWORD_AUTH',
                'AuthParameters': {
                    'USERNAME': username,
                    'PASSWORD': password
                }
            }
            
            if self.client_secret:
                kwargs['AuthParameters']['SECRET_HASH'] = self._secret_hash(username)
            
            response = self.cognito_client.admin_initiate_auth(**kwargs)
            
            # Check if there's a challenge (like MFA)
            if 'ChallengeName' in response:
                return {
                    'success': True,
                    'challenge_name': response['ChallengeName'],
                    'challenge_parameters': response.get('ChallengeParameters', {}),
                    'session': response.get('Session'),
                    'requires_challenge': True
                }
            else:
                # Successful authentication
                auth_result = response['AuthenticationResult']
                return {
                    'success': True,
                    'access_token': auth_result['AccessToken'],
                    'id_token': auth_result['IdToken'],
                    'refresh_token': auth_result['RefreshToken'],
                    'token_type': auth_result['TokenType'],
                    'expires_in': auth_result['ExpiresIn'],
                    'requires_challenge': False
                }
                
        except ClientError as e:
            logger.error(f"Authentication failed: {e.response['Error']['Code']} - {e.response['Error']['Message']}")
            return {'success': False, 'error': e.response['Error']}

    # 4. REFRESH TOKEN (AdminInitiateAuth with REFRESH_TOKEN_AUTH)
    def refresh_access_token(self, refresh_token):
        """
        Refresh access token using refresh token
        Returns: New authentication tokens
        """
        try:
            response = self.cognito_client.admin_initiate_auth(
                UserPoolId=self.user_pool_id,
                ClientId=self.client_id,
                AuthFlow='REFRESH_TOKEN_AUTH',
                AuthParameters={
                    'REFRESH_TOKEN': refresh_token
                }
            )
            
            auth_result = response['AuthenticationResult']
            return {
                'success': True,
                'access_token': auth_result['AccessToken'],
                'id_token': auth_result['IdToken'],
                'token_type': auth_result['TokenType'],
                'expires_in': auth_result['ExpiresIn']
            }
            
        except ClientError as e:
            logger.error(f"Token refresh failed: {e.response['Error']['Code']} - {e.response['Error']['Message']}")
            return {'success': False, 'error': e.response['Error']}

    # 5. PASSWORD RESET (ForgotPassword + ConfirmForgotPassword)
    def forgot_password(self, username):
        """
        Initiate password reset process
        Returns: Code delivery details
        """
        try:
            kwargs = {
                'ClientId': self.client_id,
                'Username': username
            }
            
            if self.client_secret:
                kwargs['SecretHash'] = self._secret_hash(username)
            
            response = self.cognito_client.forgot_password(**kwargs)
            
            return {
                'success': True,
                'code_delivery_details': response['CodeDeliveryDetails']
            }
            
        except ClientError as e:
            logger.error(f"ForgotPassword failed: {e.response['Error']['Code']} - {e.response['Error']['Message']}")
            return {'success': False, 'error': e.response['Error']}

    def confirm_forgot_password(self, username, confirmation_code, new_password):
        """
        Confirm password reset with verification code and new password
        Returns: Success status
        """
        try:
            kwargs = {
                'ClientId': self.client_id,
                'Username': username,
                'ConfirmationCode': confirmation_code,
                'Password': new_password
            }
            
            if self.client_secret:
                kwargs['SecretHash'] = self._secret_hash(username)
            
            self.cognito_client.confirm_forgot_password(**kwargs)
            
            return {'success': True, 'message': 'Password reset successfully'}
            
        except ClientError as e:
            logger.error(f"ConfirmForgotPassword failed: {e.response['Error']['Code']} - {e.response['Error']['Message']}")
            return {'success': False, 'error': e.response['Error']}
    
    # validate token
    def validate_token(self, token):
        try:
            self.cognito_client.get_user(AccessToken=token)
            return {'success': True, 'message': 'Token is valid'}
        except ClientError as e:
            logger.error(f"ValidateToken failed: {e.response['Error']['Code']} - {e.response['Error']['Message']}")
            return {'success': False, 'error': e.response['Error']}

    # logout
    def logout(self, token):
        try:
            # First try to use the token as an access token for global sign out
            try:
                self.cognito_client.global_sign_out(AccessToken=token)
                return {'success': True, 'message': 'User signed out successfully'}
            except ClientError as e:
                # If global_sign_out fails, try revoke_token (for refresh tokens)
                if e.response['Error']['Code'] == 'UnsupportedTokenTypeException':
                    self.cognito_client.revoke_token(
                        Token=token,
                        ClientId=self.client_id,
                        ClientSecret=self.client_secret
                    )
                    return {'success': True, 'message': 'Token revoked successfully'}
                raise
        except ClientError as e:
            logger.error(f"Logout failed: {e.response['Error']['Code']} - {e.response['Error']['Message']}")
            return {'success': False, 'error': e.response['Error']}
    
    # get details
    def get_user_details(self, token):
        try:
            response = self.cognito_client.get_user(AccessToken=token)
            return {'success': True, 'user_details': response['UserAttributes']}
        except ClientError as e:
            logger.error(f"GetUserDetails failed: {e.response['Error']['Code']} - {e.response['Error']['Message']}")
            return {'success': False, 'error': e.response['Error']}

    # BONUS: Handle MFA Challenge Response
    def respond_to_mfa_challenge(self, username, session, mfa_code):
        """
        Respond to MFA challenge during authentication
        Returns: Authentication result with tokens
        """
        try:
            kwargs = {
                'ClientId': self.client_id,
                'ChallengeName': 'SOFTWARE_TOKEN_MFA',
                'Session': session,
                'ChallengeResponses': {
                    'USERNAME': username,
                    'SOFTWARE_TOKEN_MFA_CODE': mfa_code
                }
            }
            
            if self.client_secret:
                kwargs['ChallengeResponses']['SECRET_HASH'] = self._secret_hash(username)
            
            response = self.cognito_client.respond_to_auth_challenge(**kwargs)
            auth_result = response['AuthenticationResult']
            
            return {
                'success': True,
                'access_token': auth_result['AccessToken'],
                'id_token': auth_result['IdToken'],
                'refresh_token': auth_result['RefreshToken'],
                'token_type': auth_result['TokenType'],
                'expires_in': auth_result['ExpiresIn']
            }
            
        except ClientError as e:
            logger.error(f"MFA Challenge failed: {e.response['Error']['Code']} - {e.response['Error']['Message']}")
            return {'success': False, 'error': e.response['Error']}
# # Example usage
# if __name__ == "__main__":
#     # Initialize the auth class
#     auth = CognitoAuth(
#         user_pool_id='your-user-pool-id',
#         client_id='your-client-id',
#         client_secret='your-client-secret',  # Optional
#         region='us-east-1'
#     )
    
#     # 1. Register a new user
#     result = auth.sign_up(
#         username='testuser',
#         password='TempPassword123!',
#         email='user@example.com'
#     )
#     print("Sign up result:", result)
    
#     # 2. Confirm registration
#     if result['success'] and not result['user_confirmed']:
#         confirm_result = auth.confirm_sign_up(
#             username='testuser',
#             confirmation_code='123456'  # Code from email
#         )
#         print("Confirmation result:", confirm_result)
    
#     # 3. Authenticate user
#     auth_result = auth.authenticate_user(
#         username='testuser',
#         password='TempPassword123!'
#     )
#     print("Authentication result:", auth_result)
    
#     # 4. Refresh token (if you have a refresh token)
#     if auth_result['success'] and not auth_result['requires_challenge']:
#         refresh_result = auth.refresh_access_token(
#             refresh_token=auth_result['refresh_token']
#         )
#         print("Token refresh result:", refresh_result)
    
#     # 5. Password reset
#     forgot_result = auth.forgot_password(username='testuser')
#     print("Forgot password result:", forgot_result)
    
#     # Confirm password reset
#     if forgot_result['success']:
#         reset_result = auth.confirm_forgot_password(
#             username='testuser',
#             confirmation_code='654321',  # Code from email
#             new_password='NewPassword123!'
#         )
#         print("Password reset result:", reset_result)

# api



router = APIRouter()
@router.post("/sign-up")
def sign_up(request: SignUpRequest, db: Session = Depends(get_db)):

    auth = CognitoAuth(
        user_pool_id='us-east-1_bdBzy57Vz',
        client_id='1j9ja7bfvr94bf86n0o17sklcv',
        client_secret='1hgfa89g5n5n3m877b8e7dvaoqoef9dmu2nl8bv627r482diu2tm',  # Optional
        region='us-east-1'
    )
    result = auth.sign_up(request.username, request.password,request.username, request.name)

    # add new row to credits table
    user = db.query(Credits).filter(Credits.email == request.username).first()
    if not user:
        db.add(Credits(email=request.username, credits=50))
        db.commit()
    return result



def cognito_auth():
    auth = CognitoAuth(
        user_pool_id=settings.COGNITO_USER_POOL_ID,
        client_id=settings.COGNITO_CLIENT_ID,
        client_secret=settings.COGNITO_CLIENT_SECRET,
        region=settings.AWS_DEFAULT_REGION
    )
    return auth

@router.post("/confirm-sign-up")
def confirm_sign_up(request: ConfirmSignUpRequest):
    auth = cognito_auth()
    result = auth.confirm_sign_up(request.username, request.confirmation_code)
    return result

@router.post("/authenticate-user")
def authenticate_user(request: AuthenticateUserRequest):
    auth = cognito_auth()
    result = auth.authenticate_user(request.username, request.password)
    return result

@router.post("/refresh-token")
def refresh_access_token(refresh_token: str):
    auth = cognito_auth()
    result = auth.refresh_access_token(refresh_token)
    return result

@router.post("/forgot-password")
def forgot_password(username: str):
    auth = cognito_auth()
    result = auth.forgot_password(username)
    return result

@router.post("/confirm-forgot-password")
def confirm_forgot_password(username: str, confirmation_code: str, new_password: str):
    auth = cognito_auth()
    result = auth.confirm_forgot_password(username, confirmation_code, new_password)
    return result

# protected routes
from fastapi import Request
@router.get("/protected")
def protected_route(request: Request):
    # token validation
    token = request.headers.get("Authorization")
    token = token.split(" ")[1]
    print(token)
    if not token:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    try:
        auth = cognito_auth()
        result = auth.validate_token(token)
        if result['success']:
            return True
        else:
            raise HTTPException(status_code=401, detail="Unauthorized")
    except Exception as e:
        raise HTTPException(status_code=401, detail="Unauthorized")

@router.post("/logout")
def logout(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    
    token = auth_header.split(" ")[1]
    auth = cognito_auth()
    
    try:
        result = auth.logout(token=token)
        return result
    except Exception as e:
        logger.error(f"Logout failed: {str(e)}")
        raise HTTPException(status_code=400, detail="Logout failed")



@router.get("/me")
def me(request: Request, db: Session = Depends(get_db)):
    auth_header = request.headers.get("Authorization")
    print(auth_header)
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    
    token = auth_header.split(" ")[1]
    auth = cognito_auth()
    
    try:
        result = auth.get_user_details(token=token)
        credits = get_credits(result['user_details'][0]['Value'], db)
        return {"user": result['user_details'], "credits": credits["credits"]}
    except Exception as e:
        logger.error(f"GetUserDetails failed: {str(e)}")
        raise HTTPException(status_code=400, detail="GetUserDetails failed")


def get_email(request: Request):
    auth_header = request.headers.get("Authorization")
    print(auth_header)
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    
    token = auth_header.split(" ")[1]
    auth = cognito_auth()
    
    try:
        result = auth.get_user_details(token=token)
        return result['user_details'][0]['Value']
    except Exception as e:
        logger.error(f"GetUserDetails failed: {str(e)}")
        raise HTTPException(status_code=400, detail="GetUserDetails failed")