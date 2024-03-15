from django.views.generic import TemplateView

class ContactPageView(TemplateView):
    template_name = 'contactAndHelp/contact_page.html'
    
    
class ContactUsPageView(TemplateView):
    template_name = 'contactAndHelp/contact_us.html'
    
    
class ContactPoliciesPageView(TemplateView):
    template_name = 'contactAndHelp/data_policies.html'
