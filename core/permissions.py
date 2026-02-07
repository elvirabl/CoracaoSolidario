from functools import wraps
from django.http import HttpResponseForbidden


def role_required(*allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return HttpResponseForbidden("Acesso negado.")

            profile = getattr(request.user, "profile", None)
            if not profile:
                return HttpResponseForbidden("Perfil não encontrado.")

            if profile.role not in allowed_roles:
                return HttpResponseForbidden("Sem permissão.")

            return view_func(request, *args, **kwargs)
        return _wrapped
    return decorator