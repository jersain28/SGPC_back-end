import io
from django.template.loader import get_template
from xhtml2pdf import pisa 

def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = io.BytesIO()
    
    # Forzamos UTF-8 tanto en el encode como en el motor de pisa
    pisa_status = pisa.CreatePDF(
        io.BytesIO(html.encode("UTF-8")), 
        dest=result,
        encoding='utf-8' # Añade este parámetro explícitamente
    )
    if pisa_status.err:
        return None
    return result.getvalue()