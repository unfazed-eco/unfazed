models 和 序列化器
=====

在前两节中，我们成功创建了项目和应用，并且跑起了 hello,world 服务，本节将介绍如何使用 tortoise-orm 创建数据模型以及对应的序列化器

第二节创建的应用为 enroll，接下来的几节我们将演示如何实现学生选课这个过程的业务逻辑

### 数据模型定义

数据模型定义在 models.py 中，定义以下两个模型

```python

# src/backend/enroll/models.py

class Student(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255)
    age = fields.IntField()
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    courses = fields.ManyToManyField(
        "models.Course", related_name="students", through="course_student"
    )


class Course(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255)
    description = fields.TextField()
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    students: fields.ManyToManyRelation[Student]


```

对其中一些关键字段介绍

- id: 主键 id
- Student.courses 定义多对多关系，表示某个学生选的所有课程
- Course.stundets 使用类型注释告诉解释器，Course 会有 students 字段，表示某门课被哪些学生选上了


### 在数据库中建表


1、在 entry/settings/__init__.py 配置 DATABASE，方便起见，这些使用 sqlite3 作为数据库，配置如下

```python

# src/backend/enroll/settings/__init__.py
"DATABASE": {
        "CONNECTIONS": {
            "default": {
                "ENGINE": "tortoise.backends.sqlite",
                "CREDENTIALS": {
                    "PATH": os.path.join(PROJECT_DIR, "db.sqlite3"),
                },
            }
        }
    },


```


### 建表


使用 aerich migrate 工具进行建表操作


```bash

python manage.py init-db
python manage.py migrate


```

