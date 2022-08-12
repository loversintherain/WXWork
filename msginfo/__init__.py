from sqlalchemy import create_engine, Column, VARCHAR, DATETIME, INT
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()


class Info(Base):
    __tablename__ = "msg_detail"
    message_detail = Column(VARCHAR(6000))
    phone = Column(VARCHAR(255))
    kf_name = Column(VARCHAR(255))
    suppliers_name = Column(VARCHAR(255))
    flag = Column(INT())
    uuid = Column(VARCHAR(255), primary_key=True)
    creat_date = DATETIME
    update_date = DATETIME
    msg_type = Column(VARCHAR(255))

    def __call__(self, *args, **kwargs) -> list:
        return [self.message_detail, self.uuid, self.flag, self.phone, self.kf_name, self.suppliers_name]


def get_session(test: bool = True):
    if test:
        engine = create_engine("mysql+pymysql://test:Test.147123@172.23.147.170:3306/zz")
    else:
        engine = create_engine("mysql+pymysql://root:root@192.168.1.248:3306/zz")
    db_session = sessionmaker(bind=engine)
    return db_session()


if __name__ == '__main__':
    session = get_session()
    infos = session.query(Info)
    for info in infos:
        info()
        msg = info.message_detail
        print(msg)
        newInfo = session.query(Info).filter_by(uuid=info.uuid).first()
        newInfo.flag = 2
        session.commit()



