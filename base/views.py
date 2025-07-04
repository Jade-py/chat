from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import MessageForm, UploadFileForm
from .models import Department, UploadedFile, Message
from django.http import HttpResponse

@login_required
def chat_view(request, dept_id=None):
    try:
        my_dept = request.user.userprofile.department # Try to get dept associated with user
    except AttributeError:
        return HttpResponse("Your account is not linked to any department.", status=403)

    departments = Department.objects.exclude(id=my_dept.id) # Get all the depts except the current user's to show on left side
    selected_dept = None
    messages = []
    file_form = UploadFileForm()
    form = MessageForm()

    # Handle file uploads
    if request.method == 'POST' and 'upload_file' in request.POST:
        file_form = UploadFileForm(request.POST, request.FILES)
        if file_form.is_valid():
            file_form.save()
            return redirect("chat")

    files = UploadedFile.objects.all().order_by('-uploaded_at')

    if dept_id: # If dept_id is in url, get previous messages between user and selected dept
        selected_dept = get_object_or_404(Department, id=dept_id)
        user_dept = request.user.userprofile.department

        messages = Message.objects.filter(
            to_department=selected_dept,
            sender__userprofile__department=user_dept
        ) | Message.objects.filter(
            to_department=user_dept,
            sender__userprofile__department=selected_dept
        )

        messages = messages.order_by("timestamp")

        # Mark messages as read for induvidual users
        unread_msgs = Message.objects.filter(
            to_department=user_dept,
            sender__userprofile__department=selected_dept
        ).exclude(readers=request.user)

        for msg in unread_msgs:
            msg.readers.add(request.user)

    return render(request, 'chat.html', {
        'departments': departments, # list of depts to be shown on left side
        'selected_dept': selected_dept, # selected dept the user wants to chat with
        'messages': messages, # All messages between user and selected dept
        'file_form': file_form,  # File form where user uploads file
        'files': files, # uploaded file info
        'message_form': form # Message form where users send message
    })
