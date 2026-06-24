from tortoise.models import Model
from tortoise.fields import IntField,CharField,TextField,DatetimeField,ForeignKeyField
from tortoise import fields,models

class User(Model):
    id = IntField(pk = True)
    username = CharField(unique = True,index = True,max_length = 50)
    password = CharField(max_length = 255)

class Document(Model):
    id = IntField(pk = True)
    title = CharField(max_length = 255)
    content = TextField()
    created_at = DatetimeField(auto_now_add = True)
    User = ForeignKeyField("models.User",related_name = "documents",on_delete = fields.CASCADE)
    class Meta:
        ordering = ["-created_at"]

class TokenLog(Model):
    id = IntField(pk=True)
    user = ForeignKeyField("models.User", related_name="token_logs", on_delete=fields.CASCADE)
    action = CharField(max_length=50)  # 例如 "summary"
    prompt_tokens = IntField()       # 输入消耗
    completion_tokens = IntField()   # 输出消耗
    total_tokens = IntField()        # 总计消耗
    created_at = DatetimeField(auto_now_add=True)
    class Meta:
        ordering = ["-created_at"]

class ChatHistory(Model):
    id = IntField(pk = True)
    user = ForeignKeyField("models.User",related_name="chat_history",on_delete=fields.CASCADE)
    doc = ForeignKeyField("models.Document",related_name="chat_history",on_delete=fields.CASCADE)
    role = CharField(max_length = 20,description = "角色")
    content = TextField(description = "消息内容")
    created_at = DatetimeField(auto_now_add = True)
    class Meta:
        ordering = ["-created_at"]
        table_description = "AI多轮对话历史记录表"