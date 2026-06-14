"""Settings API routes (LLM config)."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.llm_config import LLMConfig
from ..services.ai_service import AIService
from ..schemas.llm_config import LLMConfigUpdate
from ..schemas.common import success, error
from ..utils.crypto import encrypt

router = APIRouter(prefix="/api/settings", tags=["settings"])
ai_service = AIService()


@router.get("/llm")
def get_llm_config(db: Session = Depends(get_db)):
    config = db.query(LLMConfig).filter(LLMConfig.id == 1).first()
    if not config:
        config = LLMConfig(id=1)
        db.add(config)
        db.commit()
        db.refresh(config)

    masked_key = ""
    if config.api_key:
        masked_key = config.api_key[:4] + "****" if len(config.api_key) > 4 else "****"

    return success(data={
        "id": config.id,
        "provider": str(config.provider) if hasattr(config.provider, "value") else config.provider,
        "base_url": config.base_url,
        "api_key": masked_key,
        "model": config.model,
        "enabled": config.enabled,
    })


@router.put("/llm")
def update_llm_config(data: LLMConfigUpdate, db: Session = Depends(get_db)):
    config = db.query(LLMConfig).filter(LLMConfig.id == 1).first()
    if not config:
        config = LLMConfig(id=1)
        db.add(config)

    config.provider = data.provider
    config.base_url = data.base_url
    if data.api_key:
        config.api_key = encrypt(data.api_key)
    elif data.api_key == "":
        config.api_key = ""
    config.model = data.model
    config.enabled = data.enabled
    db.commit()
    db.refresh(config)
    return success(message="LLM 配置已更新")


@router.post("/llm/test")
def test_llm(db: Session = Depends(get_db)):
    try:
        ok = ai_service.health_check(db)
        if ok:
            return success(message="LLM 连接成功")
        return error(message="LLM 连接失败，请检查配置")
    except ValueError as e:
        return error(message=str(e))
