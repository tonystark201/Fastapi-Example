# * coding:utf-8 *
import json

from app.depends import ClassDepends, CourseDepends, TeacherDepends
from common.orms import ClassORM, CourseORM, TeacherORM
from common.schema import ClassModel, CourseModel, TeacherModel
from starlette.responses import Response

from fastapi import APIRouter, Depends, status

router = APIRouter()


@router.post("/classes", dependencies=[Depends(ClassDepends.name_duplicated)])
async def create_class(cla: ClassModel):
    class_id = ClassORM.create_class(cla)
    return Response(json.dumps(class_id),status_code=status.HTTP_201_CREATED)


@router.post("/teachers", dependencies=[Depends(TeacherDepends.name_duplicated)])
async def create_teacher(tea: TeacherModel):
    teacher_id = TeacherORM.create_teacher(tea)
    return Response(json.dumps(teacher_id),status_code=status.HTTP_201_CREATED)


@router.post("/courses", dependencies=[Depends(CourseDepends.name_duplicated)])
async def create_course(cou: CourseModel):
    course_id = CourseORM.create_course(cou)
    return Response(json.dumps(course_id),status_code=status.HTTP_201_CREATED)
