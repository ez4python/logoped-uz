from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Max, F, OuterRef, Subquery, Count
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, FormView

from apps.chats.forms import ChatMessageForm
from apps.chats.models import ChatMessage
from apps.exercises.models import Assignment

User = get_user_model()


class ChatListView(LoginRequiredMixin, ListView):
    model = User
    template_name = 'dashboard/chat_list.html'
    context_object_name = 'chat_users'
    login_url = reverse_lazy('login')

    def get_queryset(self):
        user = self.request.user

        # Get the latest message for each conversation
        latest_messages = ChatMessage.objects.filter(
            (Q(sender=OuterRef('pk')) & Q(receiver=user)) |
            (Q(sender=user) & Q(receiver=OuterRef('pk')))
        ).order_by('-timestamp').values('timestamp')[:1]

        # Get unread message count for each user
        unread_count = ChatMessage.objects.filter(
            sender=OuterRef('pk'),
            receiver=user,
            is_read=False
        ).values('sender').annotate(count=Count('id')).values('count')

        if user.is_student:
            # Students can chat with their therapists
            queryset = User.objects.filter(
                is_staff=True
            ).distinct().annotate(
                last_message_time=Subquery(latest_messages),
                unread_messages=Subquery(unread_count)
            ).order_by('-last_message_time', 'full_name')
            # elif user.is_therapist:
            #     # Therapists can chat with their students
            #     queryset = User.objects.filter(
            #         student_assignments__therapist=user
            #     ).distinct().annotate(
            #         last_message_time=Subquery(latest_messages),
            #         unread_messages=Subquery(unread_count)
            #     ).order_by('-last_message_time', 'full_name')
        elif user.is_staff:
            # Admins can chat with everyone
            queryset = User.objects.exclude(
                id=user.id
            ).annotate(
                last_message_time=Subquery(latest_messages),
                unread_messages=Subquery(unread_count)
            ).order_by('-last_message_time', 'full_name')
        else:
            queryset = User.objects.none()

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add last message for each chat
        for chat_user in context['chat_users']:
            last_message = ChatMessage.objects.filter(
                (Q(sender=self.request.user) & Q(receiver=chat_user)) |
                (Q(sender=chat_user) & Q(receiver=self.request.user))
            ).order_by('-timestamp').first()

            chat_user.last_message = last_message

        context['active_page'] = 'chats'
        return context


class ChatDetailView(LoginRequiredMixin, FormView):
    template_name = 'dashboard/chat_detail.html'
    form_class = ChatMessageForm
    login_url = reverse_lazy('login')

    def get_success_url(self):
        return reverse_lazy('chat_detail', kwargs={'user_id': self.kwargs['user_id']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get the chat partner
        chat_partner = get_object_or_404(User, id=self.kwargs['user_id'])
        context['chat_partner'] = chat_partner

        # Get messages between the users
        messages = ChatMessage.objects.filter(
            (Q(sender=self.request.user) & Q(receiver=chat_partner)) |
            (Q(sender=chat_partner) & Q(receiver=self.request.user))
        ).order_by('timestamp')

        # Mark messages as read
        unread_messages = messages.filter(sender=chat_partner, receiver=self.request.user, is_read=False)
        unread_messages.update(is_read=True)

        context['chat_messages'] = messages
        context['active_page'] = 'chats'
        return context

    def form_valid(self, form):
        # Get the chat partner
        chat_partner = get_object_or_404(User, id=self.kwargs['user_id'])

        # Check if users can chat with each other
        can_chat = False

        if self.request.user.is_staff or chat_partner.is_staff:
            # Admins can chat with everyone
            can_chat = True
        elif self.request.user.is_student and chat_partner.is_therapist:
            # Check if therapist is assigned to student
            can_chat = Assignment.objects.filter(
                student=self.request.user,
                therapist=chat_partner
            ).exists()
        elif self.request.user.is_therapist and chat_partner.is_student:
            # Check if student is assigned to therapist
            can_chat = Assignment.objects.filter(
                student=chat_partner,
                therapist=self.request.user
            ).exists()

        if not can_chat:
            messages.error(self.request, 'Вы не можете отправлять сообщения этому пользователю.')
            return redirect('chat_list')

        # Create the message
        message = form.save(commit=False)
        message.sender = self.request.user
        message.receiver = chat_partner

        # Handle file uploads
        if 'image' in self.request.FILES:
            message.image = self.request.FILES['image']
        if 'video' in self.request.FILES:
            message.video = self.request.FILES['video']
        if 'file' in self.request.FILES:
            message.file = self.request.FILES['file']

        message.save()

        return super().form_valid(form)
