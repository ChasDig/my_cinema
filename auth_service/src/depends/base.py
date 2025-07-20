from fastapi import Request, HTTPException, status


def get_user_agent(request: Request) -> str:
    try:
        return request.headers["user-agent"]

    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing 'User-Agent' header"
        )
