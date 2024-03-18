from django.views.generic import TemplateView
from django.core.mail import send_mail
from django.shortcuts import render, redirect


class ContactPageView(TemplateView):
    template_name = 'contact_and_help/contact_page.html'


class ContactUsPageView(TemplateView):
    template_name = 'contact_and_help/contact_us.html'


def post_contact_us_form(request):
    if request.method == 'POST':
        content = request.POST['content']
        if content != '':

            if request.user.is_authenticated:
                to_email = request.user.email
            else:
                to_email = request.POST['email']

            send_mail(
                subject='Обращение с сайта',
                message=content,
                from_email='info_dev@24wbinside.ru',
                recipient_list=[to_email],
                fail_silently=False,
            )

            return redirect('contact_us')

    #template_name = 'contact_and_help/contact_us.html'


class ContactPoliciesPageView(TemplateView):
    template_name = 'contact_and_help/data_policies.html'
