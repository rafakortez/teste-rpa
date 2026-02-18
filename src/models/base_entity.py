from sqlalchemy.orm import DeclarativeBase

# todo model que herdar daqui vira uma tabela no banco automaticamente
# exigencia do framework
class BaseEntity(DeclarativeBase):
    pass
