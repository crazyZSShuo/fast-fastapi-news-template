from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from datetime import datetime, timedelta
import requests
from app.crud.base import CRUDBase
from app.models.visit import Visit
from app.schemas.visit import VisitCreate, VisitUpdate

class CRUDVisit(CRUDBase[Visit, VisitCreate, VisitUpdate]):
    def get_location_by_ip(self, ip: str) -> str:
        """通过 IP 获取地理位置"""
        try:
            response = requests.get(f"http://ip-api.com/json/{ip}")
            data = response.json()
            if data["status"] == "success":
                return f"{data['country']}, {data['city']}"
        except:
            pass
        return "Unknown"

    def create_with_location(self, db: Session, *, obj_in: VisitCreate) -> Visit:
        """创建访问记录并自动获取地理位置"""
        location = self.get_location_by_ip(obj_in.ip)
        db_obj = Visit(
            ip=obj_in.ip,
            location=location,
            user_agent=obj_in.user_agent,
            path=obj_in.path
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_visit_stats(self, db: Session) -> Dict[str, Any]:
        """获取访问统计信息"""
        # 总访问量
        total_visits = db.query(func.count(Visit.id)).scalar()

        # 按地理位置统计
        visits_by_location = dict(
            db.query(
                Visit.location,
                func.count(Visit.id)
            ).group_by(Visit.location).all()
        )

        # 按路径统计
        visits_by_path = dict(
            db.query(
                Visit.path,
                func.count(Visit.id)
            ).group_by(Visit.path).all()
        )

        # 最近7天的访问趋势
        seven_days_ago = datetime.now() - timedelta(days=7)
        trend_data = db.query(
            func.date(Visit.created_at).label('date'),
            func.count(Visit.id).label('count')
        ).filter(
            Visit.created_at >= seven_days_ago
        ).group_by(
            func.date(Visit.created_at)
        ).order_by(
            text('date')
        ).all()

        visits_trend = [
            {
                'date': date.strftime('%Y-%m-%d'),
                'count': count
            }
            for date, count in trend_data
        ]

        return {
            "total_visits": total_visits,
            "visits_by_location": visits_by_location,
            "visits_by_path": visits_by_path,
            "visits_trend": visits_trend
        }

visit = CRUDVisit(Visit)
