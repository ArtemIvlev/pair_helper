from sqlalchemy import Column, Integer, String, BigInteger, DateTime

from app.core.database import Base


class UsageEvent(Base):
	__tablename__ = "usage_events"

	id = Column(Integer, primary_key=True, index=True)
	ts = Column(DateTime, nullable=False, index=True)
	method = Column(String(length=16), nullable=False)
	route = Column(String(length=512), nullable=False, index=True)
	status = Column(Integer, nullable=False)
	duration_ms = Column(Integer, nullable=False)
	telegram_id = Column(BigInteger, nullable=True, index=True)

	def __repr__(self) -> str:
		return (
			f"<UsageEvent(id={self.id}, ts={self.ts}, method='{self.method}', route='{self.route}', "
			f"status={self.status}, duration_ms={self.duration_ms}, telegram_id={self.telegram_id})>"
		)


