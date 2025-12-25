from django.contrib.admin import AdminSite
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.contrib import admin
from .models import AdminPanelUser

# Cek apakah model Kategori dan Berita ada
try:
    from .models import Kategori, Berita
    HAS_KATEGORI_BERITA = True
except ImportError:
    HAS_KATEGORI_BERITA = False

class AdminPanelSite(AdminSite):
    site_header = 'Admin Panel'
    site_title = 'Admin Panel'
    index_title = 'Dashboard Admin Panel'
    
    def has_permission(self, request):
        # Cek apakah user memiliki akses ke admin panel
        if not request.user.is_authenticated:
            return False
        
        # Cek apakah user adalah admin panel user
        try:
            admin_profile = request.user.admin_panel_profile
            return True
        except AdminPanelUser.DoesNotExist:
            return False
    
    def get_app_list(self, request):
        """
        Override untuk filter model berdasarkan permission user
        """
        app_list = super().get_app_list(request)
        
        try:
            admin_profile = request.user.admin_panel_profile
            
            # Jika bukan superadmin, filter model yang bisa diakses
            if not admin_profile.is_superadmin:
                filtered_app_list = []
                
                for app in app_list:
                    # Filter model dalam setiap app
                    filtered_models = []
                    
                    for model in app['models']:
                        model_name = model['object_name'].lower()
                        
                        # Admin biasa hanya bisa akses model tertentu
                        allowed_models = ['menupilihan']
                        if HAS_KATEGORI_BERITA:
                            allowed_models.extend(['kategori', 'berita'])
                        
                        if model_name in allowed_models:
                            filtered_models.append(model)
                    
                    if filtered_models:
                        app['models'] = filtered_models
                        filtered_app_list.append(app)
                
                return filtered_app_list
            
        except AdminPanelUser.DoesNotExist:
            return []
        
        return app_list

admin_panel_site = AdminPanelSite(name='admin_panel')

# Custom Admin Classes dengan pengecekan permission
class RestrictedMenuPilihanAdmin(admin.ModelAdmin):
    list_display = ['nama', 'deskripsi', 'aktif']
    search_fields = ['nama']
    list_filter = ['aktif']
    
    def has_module_permission(self, request):
        try:
            admin_profile = request.user.admin_panel_profile
        except AdminPanelUser.DoesNotExist:
            return False
    
    def has_view_permission(self, request, obj=None):
        return self.has_module_permission(request)
    
    def has_add_permission(self, request):
        return self.has_module_permission(request)
    
    def has_change_permission(self, request, obj=None):
        return self.has_module_permission(request)
    
    def has_delete_permission(self, request, obj=None):
        try:
            admin_profile = request.user.admin_panel_profile
            return admin_profile.is_superadmin  # Hanya superadmin yang bisa delete
        except AdminPanelUser.DoesNotExist:
            return False

# Admin untuk Kategori jika ada
if HAS_KATEGORI_BERITA:
    class RestrictedKategoriAdmin(admin.ModelAdmin):
        list_display = ('id', 'nama', 'aktif')
        prepopulated_fields = {"slug": ("nama",)}
        
        def has_module_permission(self, request):
            try:
                admin_profile = request.user.admin_panel_profile
                return True  # Admin dan superadmin bisa akses Kategori
            except AdminPanelUser.DoesNotExist:
                return False
        
        def has_view_permission(self, request, obj=None):
            return self.has_module_permission(request)
        
        def has_add_permission(self, request):
            return self.has_module_permission(request)
        
        def has_change_permission(self, request, obj=None):
            return self.has_module_permission(request)
        
        def has_delete_permission(self, request, obj=None):
            try:
                admin_profile = request.user.admin_panel_profile
                return admin_profile.is_superadmin  # Hanya superadmin yang bisa delete
            except AdminPanelUser.DoesNotExist:
                return False

    class RestrictedBeritaAdmin(admin.ModelAdmin):
        list_display = ('id', 'judul', 'kategori', 'tanggal_upload')
        prepopulated_fields = {"slug": ("judul",)}
        list_filter = ('kategori', 'tanggal_upload')
        
        def has_module_permission(self, request):
            try:
                admin_profile = request.user.admin_panel_profile
                return True  # Admin dan superadmin bisa akses Berita
            except AdminPanelUser.DoesNotExist:
                return False
        
        def has_view_permission(self, request, obj=None):
            return self.has_module_permission(request)
        
        def has_add_permission(self, request):
            return self.has_module_permission(request)
        
        def has_change_permission(self, request, obj=None):
            return self.has_module_permission(request)
        
        def has_delete_permission(self, request, obj=None):
            try:
                admin_profile = request.user.admin_panel_profile
                return admin_profile.is_superadmin  # Hanya superadmin yang bisa delete
            except AdminPanelUser.DoesNotExist:
                return False

class RestrictedCustomUserAdmin(UserAdmin):
    def has_module_permission(self, request):
        try:
            admin_profile = request.user.admin_panel_profile
            return admin_profile.is_superadmin  # Hanya superadmin yang bisa akses User
        except AdminPanelUser.DoesNotExist:
            return False
    
    def has_view_permission(self, request, obj=None):
        return self.has_module_permission(request)
    
    def has_add_permission(self, request):
        return self.has_module_permission(request)
    
    def has_change_permission(self, request, obj=None):
        return self.has_module_permission(request)
    
    def has_delete_permission(self, request, obj=None):
        return self.has_module_permission(request)

class RestrictedAdminPanelUserAdmin(admin.ModelAdmin):
    list_display = ['user', 'is_superadmin']
    list_filter = ['is_superadmin']
    
    def has_module_permission(self, request):
        try:
            admin_profile = request.user.admin_panel_profile
            return admin_profile.is_superadmin  # Hanya superadmin yang bisa akses AdminPanelUser
        except AdminPanelUser.DoesNotExist:
            return False
    
    def has_view_permission(self, request, obj=None):
        return self.has_module_permission(request)
    
    def has_add_permission(self, request):
        return self.has_module_permission(request)
    
    def has_change_permission(self, request, obj=None):
        return self.has_module_permission(request)
    
    def has_delete_permission(self, request, obj=None):
        return self.has_module_permission(request)

# Register models ke admin panel
admin_panel_site.register(User, RestrictedCustomUserAdmin)
admin_panel_site.register(AdminPanelUser, RestrictedAdminPanelUserAdmin)

# Register Kategori dan Berita jika ada
if HAS_KATEGORI_BERITA:
    admin_panel_site.register(Kategori, RestrictedKategoriAdmin)
    admin_panel_site.register(Berita, RestrictedBeritaAdmin)