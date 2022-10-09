# * coding:utf-8 *


from typing import List, Optional

from pydantic import BaseModel as BM
from pydantic import Field, validator


class UserModel(BM):
    id: Optional[str] = Field(default=None, regex="^[0-9A-Za-z]{22}$")
    name: Optional[str] = Field(default=None, max_length=32)
    password: Optional[str] = Field(default=None, regex="^[0-9A-Za-z]{8,16}$")

    class Config:
        orm_mode = True


class BaseModel(BM):
    id: Optional[str] = Field(default=None, regex="^[0-9A-Za-z]{22}$")
    name: Optional[str] = Field(default=None, regex=r"^[0-9A-Za-z_]{0,64}$")

    @validator("name")
    def dummy_validation(cls, value):
        """this is a dummy validation for name"""
        return value

    class Config:
        orm_mode = True


class TeacherModel(BaseModel):
    pass


class ClassModel(BaseModel):
    pass


class CourseModel(BaseModel):
    pass


class StudentModel(BM):
    id: Optional[str] = Field(default=None, regex="^[0-9A-Za-z]{22}$")
    name: Optional[str] = Field(default=None, max_length=64)
    phone: Optional[str] = Field(default=None, regex=r"^[0-9]{11}$")
    teacher: TeacherModel
    class_: ClassModel

    class Config:
        orm_mode = True


class StudentListModel(BM):
    total: int = 0
    students: List[StudentModel] = []

    class Config:
        orm_mode = True
