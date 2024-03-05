# class ProfileUpdateView(UpdateView):
#     model = CustomUser
#     form_class = CustomUserForm
#     second_form_class = ProfileForm
#     template_name = 'posts/users/edit_profile.html'

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         if 'form2' not in context:
#             context['form2'] = self.second_form_class
#         return context

#     def get_object(self, queryset=None):
#         return self.request.user

#     def form_valid(self, form):
#         form2 = self.second_form_class(self.request.POST, self.request.FILES, instance=self.request.user.profile)

#         if form2.is_valid():
#             form2.save()
#             return super().form_valid(form)
#         else:
#             return self.render_to_response(self.get_context_data(form=form, form2=form2))

#     def get_success_url(self):
#         return reverse('user_profile', kwargs={'pk': self.request.user.pk})