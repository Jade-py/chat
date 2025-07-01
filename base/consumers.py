import base64
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from django.core.files.base import ContentFile


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        if self.user.is_anonymous:
            await self.close()
        else:
            self.user_department = await self.get_user_department(self.user)
            self.room_group_name = f"dept_{self.user_department.id}"
            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
            await self.accept()
            await self.send_unread_counts()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)

        if data.get("action") == "upload_file":
            event = await self.handle_file_upload(data)
            for dept_id in {event['sender_dept_id'], event['receiver_dept_id']}:
                await self.channel_layer.group_send(
                    f"dept_{dept_id}",
                    {
                        'type': 'chat_message',
                        **event
                    }
                )

            await self.channel_layer.group_send(
                f"dept_{event['receiver_dept_id']}",
                {
                    'type': 'unread_notification',
                    'sender_dept_id': event['sender_dept_id'],
                }
            )
            return

        if data.get("action") == "mark_as_read":
            dept_id = data["department_id"]
            await self.mark_messages_as_read(self.user, dept_id)
            await self.send_unread_counts()
            return

        receiver_dept_id = int(data["receiver_dept_id"])
        message_content = data["message"]

        sender = self.user
        sender_dept_name = await self.get_user_department_name(sender)
        receiver_dept = await self.get_department(receiver_dept_id)
        receiver_dept_name = receiver_dept.name

        # Save message
        await self.save_message(sender, receiver_dept, message_content)

        # Broadcast to both sender and receiver departments
        for dept_id in {self.user_department.id, receiver_dept.id}:
            await self.channel_layer.group_send(
                f"dept_{dept_id}",
                {
                    'type': 'chat_message',
                    'sender': sender.name,
                    'sender_dept': sender_dept_name,
                    'receiver_dept': receiver_dept_name,
                    'sender_dept_id': self.user_department.id,
                    'receiver_dept_id': receiver_dept.id,
                    'message': message_content,
                }
            )

        # Trigger unread update only for receiver
        await self.channel_layer.group_send(
            f"dept_{receiver_dept_id}",
            {
                'type': 'unread_notification',
                'sender_dept_id': self.user_department.id,
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'sender': event['sender'],
            'sender_dept': event['sender_dept'],
            'receiver_dept': event['receiver_dept'],
            'sender_dept_id': event['sender_dept_id'],
            'receiver_dept_id': event['receiver_dept_id'],
            'message': event['message'],
        }))

    async def unread_notification(self, event):
        # Don't refresh unread count if the message came from the chat user is currently viewing
        if str(event.get("sender_dept_id")) == str(self.user_department.id):
            return
        await self.send_unread_counts()

    async def send_unread_counts(self):
        from .models import Message, Department

        user = self.user
        user_dept = await self.get_user_department(user)
        departments = await sync_to_async(list)(Department.objects.exclude(id=user_dept.id))

        counts = {}
        for dept in departments:
            count = await sync_to_async(Message.objects.filter(
                to_department=user_dept,
                sender__userprofile__department=dept
            ).exclude(readers=user).count)()
            counts[dept.id] = count

        await self.send(text_data=json.dumps({
            'type': 'unread_counts',
            'counts': counts,
        }))

    @sync_to_async
    def handle_file_upload(self, data):
        from .models import UploadedFile, Message, Department

        file_name = data["filename"]
        file_data = data["file_data"]
        receiver_dept_id = data["receiver_dept_id"]

        format, file_str = file_data.split(';base64,')
        decoded_file = base64.b64decode(file_str)

        content_file = ContentFile(decoded_file, name=file_name)
        file_instance = UploadedFile.objects.create(file=content_file)

        sender = self.user
        to_department = Department.objects.get(id=receiver_dept_id)

        # Save message (optional to add fallback text or caption)
        file_url = file_instance.file.url
        file_name = file_instance.file.name.split("/")[-1]  # e.g., Addon.pdf
        message = Message.objects.create(
            sender=sender,
            to_department=to_department,
            content=f"<a href='{file_url}' target='_blank'>📎 {file_name}</a>"
        )

        return {
            'sender': sender.name,
            'sender_dept': sender.userprofile.department.name,
            'receiver_dept': to_department.name,
            'sender_dept_id': sender.userprofile.department.id,
            'receiver_dept_id': to_department.id,
            'message': message.content,
            'file_url': file_url,
            'file_name': file_name,
        }

    @sync_to_async
    def get_user_department(self, user):
        return user.userprofile.department

    @sync_to_async
    def get_user_department_name(self, user):
        return user.userprofile.department.name

    @sync_to_async
    def get_department(self, dept_id):
        from .models import Department
        return Department.objects.get(id=dept_id)

    @sync_to_async
    def mark_messages_as_read(self, user, from_dept_id):
        from .models import Message, UserProfile

        sender_users = UserProfile.objects.filter(department_id=from_dept_id).values_list('user_id', flat=True)

        unread_messages = Message.objects.filter(
            to_department=user.userprofile.department,
            sender_id__in=sender_users
        ).exclude(readers=user)

        for msg in unread_messages:
            msg.readers.add(user)

    @sync_to_async
    def save_message(self, sender, to_department, content):
        from .models import Message
        Message.objects.create(sender=sender, to_department=to_department, content=content)
