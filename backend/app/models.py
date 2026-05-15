from sqlalchemy import String, Float, Integer, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from .database import Base


class Region(Base):
    __tablename__ = "regions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ExpertSurveyUpload(Base):
    __tablename__ = "expert_survey_uploads"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    file_name: Mapped[str] = mapped_column(String(255))
    sheet_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    response_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Dataset(Base):
    __tablename__ = "datasets"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    region_id: Mapped[int] = mapped_column(ForeignKey("regions.id"))
    name: Mapped[str] = mapped_column(String(255), default="default")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class DatasetRow(Base):
    __tablename__ = "dataset_rows"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    dataset_id: Mapped[int] = mapped_column(ForeignKey("datasets.id"), index=True)
    project_id: Mapped[str] = mapped_column(String(100))
    project_name: Mapped[str] = mapped_column(String(255))
    region_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    wave_height: Mapped[float | None] = mapped_column(Float, nullable=True)
    tide_mode: Mapped[float | None] = mapped_column(Float, nullable=True)
    wind_speed: Mapped[float | None] = mapped_column(Float, nullable=True)
    storm_level: Mapped[float | None] = mapped_column(Float, nullable=True)
    soil_type: Mapped[float | None] = mapped_column(Float, nullable=True)
    weak_layer: Mapped[float | None] = mapped_column(Float, nullable=True)
    slide_risk: Mapped[float | None] = mapped_column(Float, nullable=True)
    survey_quality: Mapped[float | None] = mapped_column(Float, nullable=True)
    tech_complex: Mapped[float | None] = mapped_column(Float, nullable=True)
    construction_diff: Mapped[float | None] = mapped_column(Float, nullable=True)
    equipment_depend: Mapped[float | None] = mapped_column(Float, nullable=True)
    tech_error: Mapped[float | None] = mapped_column(Float, nullable=True)
    material_supply: Mapped[float | None] = mapped_column(Float, nullable=True)
    equipment_mobilize: Mapped[float | None] = mapped_column(Float, nullable=True)
    transport_risk: Mapped[float | None] = mapped_column(Float, nullable=True)
    resource_shortage: Mapped[float | None] = mapped_column(Float, nullable=True)
    site_manage: Mapped[float | None] = mapped_column(Float, nullable=True)
    coordination_risk: Mapped[float | None] = mapped_column(Float, nullable=True)
    schedule_risk: Mapped[float | None] = mapped_column(Float, nullable=True)
    issue_handling: Mapped[float | None] = mapped_column(Float, nullable=True)
    labor_safety: Mapped[float | None] = mapped_column(Float, nullable=True)
    marine_safety: Mapped[float | None] = mapped_column(Float, nullable=True)
    environment_risk: Mapped[float | None] = mapped_column(Float, nullable=True)
    emergency_response: Mapped[float | None] = mapped_column(Float, nullable=True)
    payload_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    risk_score: Mapped[float] = mapped_column(Float)
    risk_level: Mapped[str] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class TrainedModel(Base):
    __tablename__ = "trained_models"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    region_id: Mapped[int] = mapped_column(ForeignKey("regions.id"), index=True)
    model_name: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    model_type: Mapped[str] = mapped_column(String(100), default="ANFIS-Sugeno")
    metrics_json: Mapped[str] = mapped_column(Text)
    artifact_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class PredictionHistory(Base):
    __tablename__ = "prediction_history"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    region_id: Mapped[int] = mapped_column(ForeignKey("regions.id"), index=True)
    model_id: Mapped[int | None] = mapped_column(ForeignKey("trained_models.id"), nullable=True)
    project_name: Mapped[str] = mapped_column(String(255))
    project_location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    input_json: Mapped[str] = mapped_column(Text)
    result_json: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
