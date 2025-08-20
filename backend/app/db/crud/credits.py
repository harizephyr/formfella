#CRUD operations for credits
from app.db.models.credits import Credits

#Get credits
def get_credits(email: str, db):
    user = db.query(Credits).filter(Credits.email == email).first()
    if user:
        return {"credits": user.credits}
    return {"credits": 0}

#Update credits
def update_credits(amount: int, email: str, db):
    user = db.query(Credits).filter(Credits.email == email).first()
    if not user:
        return {"credits": 0}
    user.credits = amount
    db.add(user)
    db.commit()
    return {"credits": user.credits}

#Add credits

def add_credits(amount: int, email: str, db):
    user = db.query(Credits).filter(Credits.email == email).first()
    if not user:
        return {"credits": 0}
    user.credits += amount
    db.add(user)
    db.commit()
    return {"credits": user.credits}
