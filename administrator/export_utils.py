from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter
from django.http import HttpResponse
import datetime

def export_to_excel(queryset, fields, filename, sheet_name='Data'):
    """
    Fungsi untuk mengekspor queryset ke file Excel
    
    Parameters:
    - queryset: QuerySet yang akan diekspor
    - fields: List berisi nama field yang akan diekspor
    - filename: Nama file untuk hasil ekspor
    - sheet_name: Nama sheet di Excel (default: 'Data')
    """
    # Buat workbook dan worksheet
    wb = Workbook()
    ws = wb.active
    ws.title = sheet_name
    
    # Buat header
    header_font = Font(bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="4F81BD", end_color="4F81BD", fill_type="solid")
    header_alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
    
    # Tulis header
    for col_num, field in enumerate(fields, 1):
        col_letter = get_column_letter(col_num)
        cell = ws.cell(row=1, column=col_num, value=field['name'])
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = header_alignment
        ws.column_dimensions[col_letter].width = field.get('width', 20)
    
    # Tulis data
    for row_num, obj in enumerate(queryset, 2):  # Mulai dari baris 2
        for col_num, field in enumerate(fields, 1):
            value = getattr(obj, field['field'], '')
            
            # Handle method callable
            if callable(value):
                value = value()
                
            # Handle ForeignKey
            if hasattr(value, '__str__'):
                value = str(value)
                
            # Handle datetime
            if hasattr(value, 'strftime'):
                if hasattr(value, 'time') and value.time() != datetime.time(0, 0):
                    value = value.strftime('%d/%m/%Y %H:%M')
                else:
                    value = value.strftime('%d/%m/%Y')
            
            # Handle boolean
            if isinstance(value, bool):
                value = 'Ya' if value else 'Tidak'
            
            ws.cell(row=row_num, column=col_num, value=value)
    
    # Buat border untuk data
    thin_border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )
    
    for row in ws.iter_rows(min_row=1, max_row=ws.max_row, min_col=1, max_col=len(fields)):
        for cell in row:
            cell.border = thin_border
    
    # Buat response
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename={filename}.xlsx'
    
    # Simpan workbook ke response
    wb.save(response)
    return response

def export_model_to_excel(model_admin, request, queryset):
    """
    Fungsi untuk mengekspor model ke Excel dari admin
    """
    # Dapatkan model dari queryset
    model = model_admin.model
    
    # Dapatkan semua field yang bisa ditampilkan
    field_names = [field.name for field in model._meta.fields if field.name != 'id']
    
    # Buat daftar field dengan konfigurasi
    fields = []
    for field_name in field_names:
        field = model._meta.get_field(field_name)
        fields.append({
            'field': field_name,
            'name': field.verbose_name.capitalize(),
            'width': 25 if field.get_internal_type() in ['TextField', 'CharField'] else 15
        })
    
    # Nama file berdasarkan nama model
    filename = f"export_{model._meta.verbose_name_plural.lower().replace(' ', '_')}"
    
    # Panggil fungsi export_to_excel
    return export_to_excel(queryset, fields, filename, model._meta.verbose_name_plural)
