from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect
from django.urls import resolve, reverse
from django.contrib import messages
from django.utils import timezone
from .models import LogAktivitas
import json


class AdminRoleMiddleware(MiddlewareMixin):
    """ 
    Middleware untuk admin panel kustom (/administrator/):
    - Wajib login.
    - Wajib punya AdminPanelUser profile.
    - Halaman tertentu hanya boleh diakses superadmin (User Management, Penerima Telegram).
    """

    RESTRICTED_VIEW_NAMES = {
        # User Management
        'active_users', 'add_admin_user', 'edit_admin_user', 'delete_admin_user',
        # Telegram Recipients custom pages
        'telegram_list', 'telegram_create', 'telegram_edit', 'telegram_delete',
    }

    def process_view(self, request, view_func, view_args, view_kwargs):
        path = request.path
        if not path.startswith('/administrator/'):
            return None


class ActivityLogMiddleware(MiddlewareMixin):
    """Middleware untuk mencatat setiap akses user (audit trail).
    Merekam: user, path, method, status_code, ip, user_agent, waktu mulai/selesai, durasi, dan payload ringkas.
    Dibuat ringan dan aman: skip static/media/admin dan path tertentu.
    """

    SKIP_PREFIXES = (
        '/static/', '/media/', '/favicon.ico', '/robots.txt',
    )

    def process_request(self, request):
        # Tandai start time
        request._log_started_at = timezone.now()
        return None

    def process_response(self, request, response):
        try:
            path = getattr(request, 'path', '') or ''
            if any(path.startswith(p) for p in self.SKIP_PREFIXES):
                return response
            # Opsional: skip admin bawaan Django
            if path.startswith('/admin/'):  # admin bawaan Django
                return response

            started_at = getattr(request, '_log_started_at', timezone.now())
            finished_at = timezone.now()
            duration_ms = int((finished_at - started_at).total_seconds() * 1000)

            # IP address
            ip = request.META.get('HTTP_X_FORWARDED_FOR', '')
            if ip:
                ip = ip.split(',')[0].strip()
            else:
                ip = request.META.get('REMOTE_ADDR')

            # User agent
            ua = request.META.get('HTTP_USER_AGENT', '')

            # Ringkas request data (hindari data besar/sensitif)
            req_data = None
            if request.method in ('POST', 'PUT', 'PATCH'):
                try:
                    # Ambil hingga 2KB saja
                    data_dict = request.POST.dict() if hasattr(request, 'POST') else {}
                    req_data = json.dumps({k: (v if len(str(v)) < 200 else str(v)[:200] + '…') for k, v in data_dict.items()})
                except Exception:
                    req_data = None

            LogAktivitas.objects.create(
                user=request.user if getattr(request, 'user', None) and request.user.is_authenticated else None,
                path=path[:500],
                method=request.method[:10],
                status_code=getattr(response, 'status_code', 0) or 0,
                ip_address=(ip or '')[:64],
                user_agent=ua[:500],
                action_type='ACCESS',
                started_at=started_at,
                finished_at=finished_at,
                duration_ms=max(duration_ms, 0),
                request_data=req_data,
                extra=None,
            )
        except Exception:
            # Jangan ganggu response jika logging gagal
            return response

        return response

        # 1) Wajib login
        if not request.user.is_authenticated:
            return redirect(reverse('login'))

        # 2) Wajib punya profil admin panel
        try:
            admin_profile = request.user.admin_panel_profile
        except Exception:
            messages.error(request, 'Anda tidak memiliki akses ke admin panel.')
            return redirect(reverse('error_page'))

        # 3) Batasi akses jika bukan superadmin
        try:
            match = resolve(path)
            view_name = match.url_name or ''
        except Exception:
            view_name = ''

        if not getattr(admin_profile, 'is_superadmin', False) and view_name in self.RESTRICTED_VIEW_NAMES:
            messages.warning(request, 'Akses dibatasi untuk Superadmin.')
            return redirect(reverse('administrator:berandaadmin'))

        return None
