import environs
from django.core.mail import send_mail
from django.shortcuts import redirect
from django.views.generic import TemplateView

env = environs.Env()
environs.Env.read_env()


class ContactPageView(TemplateView):
    template_name = 'contact_and_help/contact_page.html'


class ContactUsPageView(TemplateView):
    template_name = 'contact_and_help/contact_us.html'


class ContactUsSuccessPageView(TemplateView):
    template_name = 'contact_and_help/contact_us_success.html'


def post_contact_us_form(request):
    if request.method == 'POST':
        content = request.POST['content']
        if content != '':

            if request.user.is_authenticated:
                to_email = request.user.email
            else:
                to_email = request.POST['email']
            message = f"C сайта поступило обращение \nответный email: {to_email} \nСодержание: {content}"
            EMAIL = env('EMAIL_HOST_USER')
            CONTACT_EMAIL = env('CONTACT_EMAIL')
            send_mail(
                subject='Обращение с сайта',
                message=message,
                from_email=EMAIL,
                recipient_list=[CONTACT_EMAIL],
                fail_silently=False,
            )

            return redirect('contact_us_send_success')

    #template_name = 'contact_and_help/contact_us.html'


class ContactPoliciesPageView(TemplateView):
    template_name = 'contact_and_help/data_policies.html'
