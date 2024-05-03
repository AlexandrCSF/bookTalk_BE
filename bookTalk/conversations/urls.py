from django.urls import path
from conversations.views import ConversationListCreateView, MessageListCreateView, MessageDestroyView

urlpatterns = [
    path('conversation/', ConversationListCreateView.as_view(), name='club'),
    path('conversation/messages', MessageListCreateView.as_view(), name='messages'),
]
