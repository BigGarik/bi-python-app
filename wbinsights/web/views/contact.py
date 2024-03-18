from django.views.generic import TemplateView

class ContactPageView(TemplateView):
    template_name = 'contact_and_help/contact_page.html'
    
    
class ContactUsPageView(TemplateView):
    template_name = 'contact_and_help/contact_us.html'
    
    
class ContactPoliciesPageView(TemplateView):
    template_name = 'contact_and_help/data_policies.html'
