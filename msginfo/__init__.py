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
        return [self.uuid, self.flag, self.phone, self.kf_name, self.suppliers_name]


class DBSession(object):
    def __init__(self, test=True):
        if test:
            engine = create_engine("mysql+pymysql://test:Test.147123@172.28.143.5:3306/zz")
        else:
            engine = create_engine("mysql+pymysql://root:root@192.168.1.248:3306/zz")
        db_session = sessionmaker(bind=engine)
        self.DB_Session = db_session()
        self.infos = []

    def get_send_infos(self):
        self.infos = self.DB_Session.query(Info).filter(Info.flag.in_([2])).all()

    def insert_all_info(self):
        self.DB_Session.add_all(self.infos)
        self.DB_Session.commit()

    def transfer2success(self, msg_info: Info):
        msg_info1 = self.DB_Session.query(Info).filter_by(uuid=msg_info.uuid).first()
        msg_info1.flag = msg_info.flag
        self.DB_Session.commit()


def main() -> int:
    db = DBSession()
    db.get_send_infos()
    for i in db.infos:
        i.flag = 9
        i.phone = 13651495352
        db.transfer2success(i)
    return 0


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(e)
