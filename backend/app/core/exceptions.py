from fastapi import HTTPException, status

class AgentConnectException(HTTPException):
    def __init__(self, status_code: int, detail: str):
        super().__init__(status_code=status_code, detail=detail)

class EntityNotFoundException(AgentConnectException):
    def __init__(self, entity_name: str, identifier: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{entity_name} with identifier '{identifier}' not found."
        )

class AuthenticationFailedException(AgentConnectException):
    def __init__(self, detail: str = "Invalid authentication credentials"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail
        )

class AuthorizationFailedException(AgentConnectException):
    def __init__(self, detail: str = "Not enough permissions to perform this action"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail
        )

class SSRFSecurityException(AgentConnectException):
    def __init__(self, detail: str = "Target webhook URL points to a restricted IP address or internal host."):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail
        )

class PromptInjectionDetectedException(AgentConnectException):
    def __init__(self, detail: str = "Potential prompt injection or instruction override detected in content."):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail
        )
