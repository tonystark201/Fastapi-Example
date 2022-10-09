# * coding:utf-8 *
import json

from app.depends import StudentDepends, StuQuery
from common.orms import StudentORM
from common.schema import StudentListModel, StudentModel
from starlette.responses import Response

from fastapi import APIRouter, Depends, status

router = APIRouter()


@router.post(
    "/students",
    dependencies=[
        Depends(StudentDepends.name_or_phone_duplicated),
        Depends(StudentDepends.teacher_null),
        Depends(StudentDepends.class_null),
    ],
)
async def create_student(stu: StudentModel):
    student_id = StudentORM.create_student(stu)
    return Response(json.dumps(student_id),status_code=status.HTTP_201_CREATED)


@router.get("/students", response_model=StudentListModel)
async def query_student(query: StuQuery = Depends(StuQuery)):
    """use schema to generate students list,
    can also use model.dict() and jsonresponse to return result
    """
    total, students = StudentORM.query_student(query)
    res = StudentListModel()
    if total:
        res.total = total
        res.students = [StudentModel.from_orm(stu) for stu in students]
        return res
    return res
