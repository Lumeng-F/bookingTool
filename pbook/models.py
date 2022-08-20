from pbook import db, loginMana
from flask_login import UserMixin


class Customers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), default="No Name")
    phone = db.Column(db.VARCHAR(12), nullable=False)
    timeVisted = db.Column(db.Integer, nullable=False, default=1)
    timeCancelled = db.Column(db.Integer, nullable=False, default=0)
    avgSpent = db.Column(db.Integer, nullable=False, default=0)
    totalSpent = db.Column(db.Integer, nullable=False, default=0)
    description = db.Column(db.String(120), nullable=True, default="Des here")
    storeID = db.Column(db.Integer, db.ForeignKey('stores.id'), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'phone': self.phone,
            'timeVisted': self.timeVisted,
            'timeCancelled': self.timeCancelled,
            'avgSpent': self.avgSpent,
            'totalSpent': self.totalSpent,
            'description': self.description
        }


class Stores(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    storeName = db.Column(db.String(20), nullable=False)
    password = db.Column(db.VARCHAR(50), nullable=False)
    debit = db.Column(db.Integer)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'debit': self.debit
        }


class Setting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    g1 = db.Column(db.String(20), default="Anna")
    g2 = db.Column(db.String(20), default="Betty")
    g3 = db.Column(db.String(20), default="Case")
    g4 = db.Column(db.String(20), default="Dora")

    t130 = db.Column(db.Integer, nullable=False, default=200)
    t160 = db.Column(db.Integer, nullable=False, default=300)
    t170 = db.Column(db.Integer, nullable=False, default=400)
    t190 = db.Column(db.Integer, nullable=False, default=500)
    t1120 = db.Column(db.Integer, nullable=False, default=800)

    t230 = db.Column(db.Integer, nullable=False, default=220)
    t260 = db.Column(db.Integer, nullable=False, default=320)
    t270 = db.Column(db.Integer, nullable=False, default=500)
    t290 = db.Column(db.Integer, nullable=False, default=800)
    t2120 = db.Column(db.Integer, nullable=False, default=1000)

    t130Comp = db.Column(db.Integer, nullable=False, default=100)
    t160Comp = db.Column(db.Integer, nullable=False, default=180)
    t170Comp = db.Column(db.Integer, nullable=False, default=200)
    t190Comp = db.Column(db.Integer, nullable=False, default=300)
    t1120Comp = db.Column(db.Integer, nullable=False, default=400)

    t230Comp = db.Column(db.Integer, nullable=False, default=120)
    t260Comp = db.Column(db.Integer, nullable=False, default=220)
    t270Comp = db.Column(db.Integer, nullable=False, default=300)
    t290Comp = db.Column(db.Integer, nullable=False, default=450)
    t2120Comp = db.Column(db.Integer, nullable=False, default=600)

    d1 = db.Column(db.String(20), default="device 1")
    d2 = db.Column(db.String(20), default="device 2")
    d3 = db.Column(db.String(20), default="device 3")
    d4 = db.Column(db.String(20), default="device 4")

    storeID = db.Column(db.Integer, db.ForeignKey('stores.id'), nullable=False)


@loginMana.user_loader
def loadUser(storeID):
    return Stores.query.get(int(storeID))


db.create_all()
