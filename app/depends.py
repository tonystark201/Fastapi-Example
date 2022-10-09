# * coding:utf-8 *


from typing import List

import shortuuid
from common.exception import FastAPIError
from common.orms import ClassORM, CourseORM, StudentORM, TeacherORM, UserORM
from common.schema import ClassModel, CourseModel, StudentModel, TeacherModel, UserModel

from fastapi import Depends


class UserDepends(object):
    @staticmethod
    def name_duplicated(user: UserModel, user_id: str = ""):
        if user_id:
            UserORM.user_name_duplicated_for_update(user_id=user_id, name=user.name)
        else:
            UserORM.user_name_duplicated_for_add(user.name)

    @staticmethod
    def bluk_name_duplicated(users: List[UserModel]):
        UserORM.user_name_duplicated_for_add([user.name for user in users])


class ClassDepends(object):
    @staticmethod
    def name_duplicated(cla: ClassModel):
        ClassORM.name_duplicated_for_add(cla.name)


class TeacherDepends(object):
    @staticmethod
    def name_duplicated(tea: TeacherModel):
        TeacherORM.name_duplicated_for_add(tea.name)


class CourseDepends(object):
    @staticmethod
    def name_duplicated(cou: CourseModel):
        CourseORM.name_duplicated_for_add(cou.name)


class UUIDCheck(object):
    @staticmethod
    def stu(stu: StudentModel):
        try:
            shortuuid.ShortUUID(stu.teacher.id)
            shortuuid.ShortUUID(stu.class_.id)
        except ValueError:
            raise FastAPIError(1004)
        return stu


class StudentDepends(object):
    @staticmethod
    def name_or_phone_duplicated(stu: StudentModel):
        StudentORM.name_or_phone_duplicated(name=stu.name, phone=stu.phone)
        return stu

    @staticmethod
    def teacher_null(stu: StudentModel = Depends(UUIDCheck.stu)):
        if not TeacherORM.get_by_id(stu.teacher.id):
            raise FastAPIError(1007)
        return stu

    @staticmethod
    def class_null(stu: StudentModel = Depends(UUIDCheck.stu)):
        if not ClassORM.get_by_id(stu.class_.id):
            raise FastAPIError(1008)
        return stu


class StuQuery(object):
    def __init__(
        self, name: str = None, phone: str = None, offset: int = 0, limit: int = 100
    ):
        self.name = name
        self.phone = phone
        self.offset = offset
        self.limit = limit
