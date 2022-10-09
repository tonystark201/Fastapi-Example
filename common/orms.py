# * coding:utf-8 *

from typing import List


import bcrypt
import shortuuid

from common.config import get_settings
from common.exception import FastAPIError
from common.schema import ClassModel, CourseModel, StudentModel, TeacherModel, UserModel
from sqlalchemy import CHAR, Column, ForeignKey, String, create_engine
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.pool import NullPool

# load_dotenv()
# mysql_host = os.getenv("MYSQL_HOST")
# mysql_port = os.getenv("MYSQL_PORT")



dbSettings = {
    "user": "root",
    "password": "123456",
    "host": get_settings().mysql_host,
    "port": get_settings().mysql_port,
    "database": "fastapi_demo",
}

engine = create_engine(
    f"mysql+pymysql://"
    f'{dbSettings.get("user")}:'
    f'{dbSettings.get("password")}@'
    f'{dbSettings.get("host")}:'
    f'{dbSettings.get("port")}/'
    f'{dbSettings.get("database")}',
    poolclass=NullPool,
)
Session = sessionmaker(bind=engine)
db_session = Session()
Base = declarative_base()
metadata = Base.metadata


class ClassORM(Base):
    __tablename__ = "classes"
    __table_args__ = {"comment": "class table"}

    id = Column(CHAR(22, "utf8mb4_bin"), primary_key=True, comment="class id")
    name = Column(String(64, "utf8mb4_bin"), nullable=False, comment="class name")
    students = relationship("StudentORM", backref="class_")

    @classmethod
    def create_class(cls, cou: ClassModel):
        kwargs = cou.dict()
        kwargs["id"] = shortuuid.uuid()
        db_session.add(cls(**kwargs))
        db_session.commit()
        return {"id":kwargs["id"]}

    @classmethod
    def name_duplicated_for_add(cls, name):
        instance = db_session.query(cls).filter(cls.name == name).first()
        if instance:
            raise FastAPIError(1006)

    @classmethod
    def get_by_id(cls, id_):
        instance = db_session.query(cls).get(id_)
        return instance


class TeacherORM(Base):
    __tablename__ = "teachers"
    __table_args__ = {"comment": "teacher table"}

    id = Column(CHAR(22, "utf8mb4_bin"), primary_key=True, comment="teacher id")
    name = Column(String(64, "utf8mb4_bin"), nullable=False, comment="teacher name")
    students = relationship("StudentORM", backref="teacher")

    @classmethod
    def create_teacher(cls, cou: TeacherModel):
        kwargs = cou.dict()
        kwargs["id"] = shortuuid.uuid()
        db_session.add(cls(**kwargs))
        db_session.commit()
        return {"id": kwargs["id"]}

    @classmethod
    def name_duplicated_for_add(cls, name):
        instance = db_session.query(cls).filter(cls.name == name).first()
        if instance:
            raise FastAPIError(1006)

    @classmethod
    def get_by_id(cls, id_):
        instance = db_session.query(cls).get(id_)
        return instance


class CourseORM(Base):
    __tablename__ = "courses"
    __table_args__ = {"comment": "course table"}

    id = Column(CHAR(22, "utf8mb4_bin"), primary_key=True, comment="course id")
    name = Column(String(64, "utf8mb4_bin"), nullable=False, comment="course name")

    @classmethod
    def create_course(cls, cou: CourseModel):
        kwargs = cou.dict()
        kwargs["id"] = shortuuid.uuid()
        db_session.add(cls(**kwargs))
        db_session.commit()
        return {"id":kwargs["id"]}

    @classmethod
    def name_duplicated_for_add(cls, name):
        instance = db_session.query(cls).filter(cls.name == name).first()
        if instance:
            raise FastAPIError(1006)


class StuCourse(Base):
    __tablename__ = "stu_courses"
    __table_args__ = {"comment": "student course table"}

    stu_id = Column(
        CHAR(22, "utf8mb4_bin"),
        ForeignKey("StudentORM.id"),
        primary_key=True,
        nullable=False,
        comment="student id",
    )
    cou_id = Column(
        CHAR(22, "utf8mb4_bin"),
        ForeignKey("CourseORM.id"),
        primary_key=True,
        nullable=False,
        comment="course id",
    )
    score = Column(TINYINT, nullable=False, comment="score")


class StudentORM(Base):
    __tablename__ = "students"
    __table_args__ = {"comment": "student table"}

    id = Column(CHAR(22, "utf8mb4_bin"), primary_key=True, comment="user id")
    name = Column(String(64, "utf8mb4_bin"), nullable=False, comment="user name")
    phone = Column(CHAR(11, "utf8mb4_bin"), nullable=False, comment="user phone")
    teacher_id = Column(
        CHAR(22, "utf8mb4_bin"),
        ForeignKey(TeacherORM.id),
        nullable=False,
        comment="teacher id",
    )
    class_id = Column(
        CHAR(22, "utf8mb4_bin"),
        ForeignKey(ClassORM.id),
        nullable=False,
        comment="class id",
    )

    @classmethod
    def create_student(cls, stu: StudentModel):
        kwargs = {
            "id": shortuuid.uuid(),
            "name": stu.name,
            "phone": stu.phone,
            "teacher_id": stu.teacher.id,
            "class_id": stu.class_.id,
        }
        db_session.add(cls(**kwargs))
        db_session.commit()
        return {"id": kwargs["id"]}

    @classmethod
    def query_student(cls, query):
        count = db_session.query(cls).count()
        if count:
            queryset = db_session.query(cls)
            if query.name:
                queryset = queryset.filter(cls.name.like(query.name))
            if query.phone:
                queryset = queryset.filter(cls.phone.like(query.phone))
            queryset = queryset.limit(query.limit).offset(query.offset).all()
            return count, queryset
        return 0, []

    @classmethod
    def name_or_phone_duplicated(cls, name=None, phone=None):
        if name or phone:
            if name:
                instance = db_session.query(cls).filter(cls.name == name).first()
                if instance:
                    raise FastAPIError(1006)
            if phone:
                instance = db_session.query(cls).filter(cls.phone == phone).first()
                if instance:
                    raise FastAPIError(1006)
        else:
            raise ValueError("name or phone both None")


class UserORM(Base):
    __tablename__ = "users"
    __table_args__ = {"comment": "user table"}

    id = Column(CHAR(22, "utf8mb4_bin"), primary_key=True, comment="user id")
    name = Column(String(64, "utf8mb4_bin"), nullable=False, comment="user name")
    password = Column(
        String(512, "utf8mb4_bin"), nullable=False, comment="user password"
    )

    @classmethod
    def create_user(cls, user: UserModel):
        kwargs = user.dict()
        kwargs["id"] = shortuuid.uuid()
        kwargs["password"] = bcrypt.hashpw(
            kwargs["password"].encode(), bcrypt.gensalt()
        )
        db_session.add(cls(**kwargs))
        db_session.commit()
        return {"id":kwargs["id"]}

    @classmethod
    def update_user(cls, user_id: str, user: UserModel):
        kwargs = user.dict()
        kwargs.pop("id", None)
        if kwargs.get("password", None):
            kwargs["password"] = bcrypt.hashpw(
                kwargs["password"].encode(), bcrypt.gensalt()
            )
        instance = db_session.query(cls).filter(cls.id == user_id)
        if instance:
            instance.update(kwargs)
        db_session.commit()

    @classmethod
    def delete_user(cls, user_id: str):
        instance = db_session.query(cls).filter(cls.id == user_id)
        if instance:
            instance.delete()
        db_session.commit()

    @classmethod
    def create_users(cls, users: List[UserModel]):
        bulk = []
        for user in users:
            kwargs = user.dict()
            kwargs["id"] = shortuuid.uuid()
            kwargs["password"] = bcrypt.hashpw(
                kwargs["password"].encode(), bcrypt.gensalt()
            )
            bulk.append(cls(**kwargs))
        db_session.bulk_save_objects(bulk)
        db_session.commit()

    @classmethod
    def user_login(cls, user: UserModel):
        instance = db_session.query(cls).filter(cls.name == user.name).first()
        if instance:
            if bcrypt.checkpw(user.password.encode(), instance.password.encode()):
                return instance.id
        return False

    @classmethod
    def user_name_duplicated_for_add(cls, name):
        if isinstance(name, list):
            queryset = db_session.query(cls).filter(cls.name.in_(name))
            if queryset:
                raise FastAPIError(1006)
        else:
            instance = db_session.query(cls).filter(cls.name == name).first()
            if instance:
                raise FastAPIError(1006)

    @classmethod
    def user_name_duplicated_for_update(cls, name, user_id):
        instance = (
            db_session.query(cls).filter(cls.name == name, cls.id != user_id).first()
        )
        if instance:
            raise FastAPIError(1006)
