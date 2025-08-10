
from .utils import get_google_avatar

def add_user_avatar(request):
    avatar_url = None
    if request.user.is_authenticated:
        avatar_url = get_google_avatar(request.user)
    return {'user_avatar_url': avatar_url}
