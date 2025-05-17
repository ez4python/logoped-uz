import random
import string

from django.contrib import messages
from django.contrib.auth import login, logout, get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.cache import cache
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import FormView, TemplateView, UpdateView

from apps.exercises.models import Assignment, CompletedAssignment
from apps.users.forms import (
    PhoneNumberForm, VerificationCodeForm, FullNameForm,
    UserProfileForm, UserAvatarForm, ContactSupportForm
)

User = get_user_model()


class LandingPageView(TemplateView):
    template_name = 'landing.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('dashboard')
        return super().get(request, *args, **kwargs)


class RegisterView(FormView):
    template_name = 'register.html'
    form_class = PhoneNumberForm
    success_url = reverse_lazy('verify_code')

    def form_valid(self, form):
        phone_number = form.cleaned_data['phone_number']

        # Check if user already exists
        if User.objects.filter(phone_number=phone_number).exists():
            messages.error(self.request, 'Пользователь с таким номером телефона уже существует.')
            return self.form_invalid(form)

        # Generate verification code
        verification_code = ''.join(random.choices(string.digits, k=6))

        # Store phone and code in cache for verification (expires in 10 minutes)
        cache_key = f"verification_{phone_number}"
        cache.set(cache_key, {
            'code': verification_code,
            'is_registration': True,
            'attempts': 0
        }, timeout=600)  # 10 minutes

        # In a real app, send SMS with the code here
        # For development, just print it
        print(f"Verification code for {phone_number}: {verification_code}")

        # Store phone in session for the verification page
        self.request.session['phone_for_verification'] = phone_number

        return super().form_valid(form)


class LoginView(FormView):
    template_name = 'login.html'
    form_class = PhoneNumberForm
    success_url = reverse_lazy('verify_code')

    def form_valid(self, form):
        phone_number = form.cleaned_data['phone_number']

        # Check if user exists
        if not User.objects.filter(phone_number=phone_number).exists():
            messages.error(self.request, 'Пользователь с таким номером телефона не найден.')
            return self.form_invalid(form)

        # Generate verification code
        verification_code = ''.join(random.choices(string.digits, k=6))

        # Store phone and code in cache for verification (expires in 10 minutes)
        cache_key = f"verification_{phone_number}"
        cache.set(cache_key, {
            'code': verification_code,
            'is_registration': False,
            'attempts': 0
        }, timeout=600)  # 10 minutes

        # In a real app, send SMS with the code here
        # For development, just print it
        print(f"Verification code for {phone_number}: {verification_code}")

        # Store phone in session for the verification page
        self.request.session['phone_for_verification'] = phone_number

        return super().form_valid(form)


class VerifyCodeView(FormView):
    template_name = 'verify_code.html'
    form_class = VerificationCodeForm

    def get_success_url(self):
        # Если это регистрация, перенаправляем на страницу ввода имени
        # Иначе на дашборд
        cache_key = f"verification_{self.request.session.get('phone_for_verification', '')}"
        cached_data = cache.get(cache_key, {})

        if cached_data.get('is_registration', False):
            return reverse_lazy('set_fullname')
        return reverse_lazy('dashboard')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['phone'] = self.request.session.get('phone_for_verification', '')
        return context

    def form_valid(self, form):
        phone_number = self.request.session.get('phone_for_verification', '')
        if not phone_number:
            messages.error(self.request, 'Сессия истекла. Пожалуйста, начните процесс заново.')
            return redirect('login')

        # Получаем код подтверждения
        verification_code = form.cleaned_data.get('verification_code', '')

        cache_key = f"verification_{phone_number}"
        cached_data = cache.get(cache_key)

        if not cached_data:
            messages.error(self.request, 'Код подтверждения истек. Пожалуйста, запросите новый код.')
            return redirect('login')

        # Increment attempt counter
        cached_data['attempts'] += 1

        # Check if too many attempts
        if cached_data['attempts'] > 3:
            cache.delete(cache_key)
            messages.error(self.request, 'Слишком много попыток. Пожалуйста, запросите новый код.')
            return redirect('login')

        # Update cache with new attempt count
        cache.set(cache_key, cached_data, timeout=600)

        # Check if code is correct
        if verification_code != cached_data['code']:
            messages.error(self.request, 'Неверный код подтверждения. Пожалуйста, попробуйте еще раз.')
            return self.form_invalid(form)

        # Code is correct, handle login (registration is handled in SetFullNameView)
        if not cached_data.get('is_registration', False):
            # Login existing user
            user = User.objects.get(phone_number=phone_number)
            login(self.request, user)
            messages.success(self.request, 'Вы успешно вошли в систему!')

            # Clean up
            cache.delete(cache_key)
            if 'phone_for_verification' in self.request.session:
                del self.request.session['phone_for_verification']

        return super().form_valid(form)


class SetFullNameView(FormView):
    template_name = 'set_fullname.html'
    form_class = FullNameForm
    success_url = reverse_lazy('dashboard')

    def dispatch(self, request, *args, **kwargs):
        # Проверяем, есть ли в сессии номер телефона для верификации
        phone_number = request.session.get('phone_for_verification', '')
        if not phone_number:
            messages.error(request, 'Сессия истекла. Пожалуйста, начните процесс заново.')
            return redirect('register')

        # Проверяем, что код был подтвержден
        cache_key = f"verification_{phone_number}"
        cached_data = cache.get(cache_key)
        if not cached_data:
            messages.error(request, 'Сессия верификации истекла. Пожалуйста, начните процесс заново.')
            return redirect('register')

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        phone_number = self.request.session.get('phone_for_verification', '')
        full_name = form.cleaned_data['full_name']

        # Create new user
        user = User.objects.create_user(
            phone_number=phone_number,
            full_name=full_name,
            is_student=True  # By default, new users are students
        )

        # Login the user
        login(self.request, user)

        # Clean up
        cache_key = f"verification_{phone_number}"
        cache.delete(cache_key)
        if 'phone_for_verification' in self.request.session:
            del self.request.session['phone_for_verification']

        messages.success(self.request, 'Регистрация успешно завершена!')
        return super().form_valid(form)


class ResendCodeView(View):
    def get(self, request):
        phone_number = request.GET.get('phone', '')
        if not phone_number:
            messages.error(request, 'Номер телефона не указан.')
            return redirect('login')

        # Generate new verification code
        verification_code = ''.join(random.choices(string.digits, k=6))

        # Check if this is for registration or login
        is_registration = not User.objects.filter(phone_number=phone_number).exists()

        # Store phone and code in cache for verification (expires in 10 minutes)
        cache_key = f"verification_{phone_number}"
        cache.set(cache_key, {
            'code': verification_code,
            'is_registration': is_registration,
            'attempts': 0
        }, timeout=600)  # 10 minutes

        # In a real app, send SMS with the code here
        # For development, just print it
        print(f"New verification code for {phone_number}: {verification_code}")

        # Store phone in session for the verification page
        request.session['phone_for_verification'] = phone_number

        messages.success(request, 'Новый код подтверждения отправлен.')
        return redirect('verify_code')


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/index.html'
    login_url = reverse_lazy('login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        completed_assignments = CompletedAssignment.objects.filter(user=self.request.user)
        completed_ids = completed_assignments.values_list('assignment_id', flat=True)

        all_assignments = Assignment.objects.all()
        total = all_assignments.count()
        completed = completed_assignments.count()

        percentage = int((completed / total) * 100) if total > 0 else 0

        context['assignments'] = all_assignments
        context['completed_assignment_ids'] = set(completed_ids)
        context['total_assignments'] = total
        context['completed_assignments'] = completed
        context['completion_percentage'] = percentage
        context['active_page'] = 'dashboard'

        return context


class SettingsView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserProfileForm
    template_name = 'dashboard/settings.html'
    success_url = reverse_lazy('settings')

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['avatar_form'] = UserAvatarForm(instance=self.request.user)
        context['active_page'] = 'settings'
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Профиль успешно обновлен.')
        return super().form_valid(form)


class UpdateAvatarView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserAvatarForm
    template_name = 'dashboard/settings.html'
    success_url = reverse_lazy('settings')

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, 'Аватар успешно обновлен.')
        return super().form_valid(form)


class ChangePhoneView(LoginRequiredMixin, FormView):
    template_name = 'dashboard/change_phone.html'
    form_class = PhoneNumberForm
    success_url = reverse_lazy('verify_phone_change')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_page'] = 'settings'
        return context

    def form_valid(self, form):
        new_phone = form.cleaned_data['phone_number']

        # Check if phone is already in use by another user
        if User.objects.filter(phone_number=new_phone).exclude(id=self.request.user.id).exists():
            messages.error(self.request, 'Этот номер телефона уже используется другим пользователем.')
            return self.form_invalid(form)

        # Generate verification code
        verification_code = ''.join(random.choices(string.digits, k=6))

        # Store phone and code in cache for verification (expires in 10 minutes)
        cache_key = f"verification_{new_phone}"
        cache.set(cache_key, {
            'code': verification_code,
            'is_registration': False,
            'is_phone_change': True,
            'user_id': self.request.user.id,
            'attempts': 0
        }, timeout=600)  # 10 minutes

        # In a real app, send SMS with the code here
        # For development, just print it
        print(f"Verification code for changing phone to {new_phone}: {verification_code}")

        # Store phone in session for the verification page
        self.request.session['phone_for_verification'] = new_phone

        return super().form_valid(form)


class VerifyPhoneChangeView(LoginRequiredMixin, FormView):
    template_name = 'verify_phone_change.html'
    form_class = VerificationCodeForm
    success_url = reverse_lazy('settings')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['phone'] = self.request.session.get('phone_for_verification', '')
        context['active_page'] = 'settings'
        return context

    def form_valid(self, form):
        phone_number = self.request.session.get('phone_for_verification', '')
        if not phone_number:
            messages.error(self.request, 'Сессия истекла. Пожалуйста, начните процесс заново.')
            return redirect('change_phone')

        # Получаем код подтверждения
        verification_code = form.cleaned_data.get('verification_code', '')

        cache_key = f"verification_{phone_number}"
        cached_data = cache.get(cache_key)

        if not cached_data or not cached_data.get('is_phone_change'):
            messages.error(self.request, 'Код подтверждения истек. Пожалуйста, запросите новый код.')
            return redirect('change_phone')

        # Increment attempt counter
        cached_data['attempts'] += 1

        # Check if too many attempts
        if cached_data['attempts'] > 3:
            cache.delete(cache_key)
            messages.error(self.request, 'Слишком много попыток. Пожалуйста, запросите новый код.')
            return redirect('change_phone')

        # Update cache with new attempt count
        cache.set(cache_key, cached_data, timeout=600)

        # Check if code is correct
        if verification_code != cached_data['code']:
            messages.error(self.request, 'Неверный код подтверждения. Пожалуйста, попробуйте еще раз.')
            return self.form_invalid(form)

        # Code is correct, update phone number
        user = self.request.user
        user.phone_number = phone_number
        user.save()

        # Clean up
        cache.delete(cache_key)
        if 'phone_for_verification' in self.request.session:
            del self.request.session['phone_for_verification']

        messages.success(self.request, 'Номер телефона успешно изменен.')
        return super().form_valid(form)


class HelpView(LoginRequiredMixin, FormView):
    template_name = 'dashboard/help.html'
    form_class = ContactSupportForm
    success_url = reverse_lazy('help')

    def form_valid(self, form):
        # In a real app, send the support message to administrators
        subject = form.cleaned_data['subject']
        message = form.cleaned_data['message']

        # Just print for development
        print(f"Support request from {self.request.user}:")
        print(f"Subject: {subject}")
        print(f"Message: {message}")

        messages.success(self.request, 'Ваше сообщение отправлено. Мы свяжемся с вами в ближайшее время.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_page'] = 'help'
        return context


class LogoutView(LoginRequiredMixin, View):
    def get(self, request):
        logout(request)
        messages.success(request, 'Вы успешно вышли из системы.')
        return redirect('landing')


class DeleteAccountView(LoginRequiredMixin, View):
    """View for deleting a user account"""

    def get(self, request, *args, **kwargs):
        user = request.user
        user.delete()
        messages.success(request, "Ваш аккаунт был успешно удален.")
        return redirect('landing')


class DeleteAvatarView(LoginRequiredMixin, View):
    """View for deleting user avatar"""

    def get(self, request, *args, **kwargs):
        user = request.user
        if user.avatar:
            # Сохраняем путь к файлу для удаления
            avatar_path = user.avatar.path

            # Очищаем поле аватара
            user.avatar = None
            user.save()

            # Удаляем файл с диска
            import os
            if os.path.exists(avatar_path):
                os.remove(avatar_path)

            messages.success(request, "Фото профиля успешно удалено.")
        else:
            messages.info(request, "У вас нет загруженного фото профиля.")

        return redirect('settings')


def handler404(request, exception):
    """Обработчик ошибки 404 (страница не найдена)"""
    return render(request, 'status/404.html', status=404)


def handler500(request):
    """Обработчик ошибки 500 (ошибка сервера)"""
    return render(request, 'status/500.html', status=500)


def handler403(request, exception):
    """Обработчик ошибки 403 (доступ запрещен)"""
    return render(request, 'status/403.html', status=403)
