from typing import List
from sqlalchemy import Boolean, Column, Float, Integer, String, Enum, DateTime, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..core.db import session as _database
from datetime import datetime
from enum import Enum as PyEnum
from app.Exercise.models import ExerciseType,Intensity,VisibleFor


class WorkoutGoal(PyEnum):
    lose_weight = "Lose Weight"
    build_muscle = "Build Muscle"
    improved_well_being = "Improved well being"
    improve_performance = "Improve Performance"
    rehabilitation = "Rehabilitation"
    get_fit = "Get Fit"
    shape_and_tone = "Shape and Tone"

class WorkoutLevel(PyEnum):
    novice = "Novice"
    beginner = "Beginner"
    intermediate = "Intermediate"
    advanced = "Advanced"
    expert = "Expert"



class WorkoutLogs():
    create_user_type: Mapped[String] = mapped_column(String, nullable=False)
    update_user_type: Mapped[String] = mapped_column(String, nullable=True)
    created_by: Mapped[int] = mapped_column(Integer)
    updated_by: Mapped[int] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now())
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)

class Workout(_database.Base, WorkoutLogs):
    __tablename__ = "workout"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    org_id: Mapped[int] = mapped_column(Integer)
    workout_name: Mapped[str] = mapped_column(String, nullable=True)
    description: Mapped[str] = mapped_column(String, nullable=True)
    visible_for: Mapped[VisibleFor] = mapped_column(Enum(VisibleFor), nullable=True)
    goals: Mapped[WorkoutGoal] = mapped_column(Enum(WorkoutGoal), nullable=True)
    level: Mapped[WorkoutLevel] = mapped_column(Enum(WorkoutLevel), nullable=True)
    notes: Mapped[str] = mapped_column(String, nullable=True)
    weeks: Mapped[int] = mapped_column(Integer, nullable=True)
    img_url: Mapped[str] = mapped_column(String, nullable=True)

    days = relationship(
        "WorkoutDay",
        primaryjoin="Workout.id == foreign(WorkoutDay.workout_id)",
        lazy='noload',
        back_populates="workout",
    )

class WorkoutDay(_database.Base, WorkoutLogs):
    __tablename__ = "workout_day"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    workout_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    day_name: Mapped[str] = mapped_column(String, nullable=False)
    week: Mapped[int] = mapped_column(Integer, nullable=False)
    day: Mapped[int] = mapped_column(Integer, nullable=False)

    workout = relationship(
        "Workout",
        primaryjoin="Workout.id == foreign(WorkoutDay.workout_id)",
        lazy='noload',
        back_populates="days",
    )
    exercises = relationship(
        "WorkoutDayExercise",
        primaryjoin="WorkoutDay.id == foreign(WorkoutDayExercise.workout_day_id)",
        lazy='noload',
        back_populates="workout_day",
    )

class WorkoutDayExercise(_database.Base, WorkoutLogs):
    __tablename__ = "workout_day_exercise"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    workout_day_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    exercise_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    exercise_type: Mapped[ExerciseType] = mapped_column(Enum(ExerciseType), nullable=False)
    sets: Mapped[int] = mapped_column(Integer, nullable=False)
    seconds_per_set: Mapped[List[int]] = mapped_column(ARRAY(Integer), nullable=True)
    repetitions_per_set: Mapped[List[int]] = mapped_column(ARRAY(Integer), nullable=True)
    rest_between_set: Mapped[List[int]] = mapped_column(ARRAY(Integer), nullable=True)
    intensity_type: Mapped[Intensity] = mapped_column(Enum(Intensity))
    intensity_value: Mapped[float] = mapped_column(Float, nullable=True)
    distance: Mapped[float] = mapped_column(Float, nullable=True)
    speed: Mapped[float] = mapped_column(Float, nullable=True)
    met_value: Mapped[float] = mapped_column(Float, nullable=True)
    notes: Mapped[str] = mapped_column(String, nullable=True)

    workout_day = relationship(
        "WorkoutDay",
        primaryjoin="WorkoutDay.id == foreign(WorkoutDayExercise.workout_day_id)",
        lazy="noload",
        back_populates="exercises",
    )

    exercise = relationship(
        "Exercise",
        primaryjoin="Exercise.id == foreign(WorkoutDayExercise.exercise_id)",
        lazy="noload",
        back_populates=None,
    )


class MemberWorkout(_database.Base, WorkoutLogs):
    __tablename__ = "member_workout"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    member_id: Mapped[int] = mapped_column(Integer, nullable=False)
    workout_id: Mapped[int] = mapped_column(Integer, nullable=False)
