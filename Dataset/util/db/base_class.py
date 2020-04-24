from sqlalchemy.ext.declarative import declarative_base, declared_attr


class CustomBase(object):
    # Generate __tablename__ automatically
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    def save(self, session):
        session.add(self)
        session.commit()


Base = declarative_base(cls=CustomBase)
