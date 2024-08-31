from unfazed.orm import tortoise as tt


class User(tt.Model):
    id = tt.IntField(primary_key=True)
    username = tt.CharField(max_length=255)
    email = tt.CharField(max_length=255)
    uid = tt.IntField()
    # sex = tt.IntField(default=0)
