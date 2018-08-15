from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, Category, Item, User

engine = create_engine('sqlite:///categories-menu.db')

# Clear database
Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)

Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

session = DBSession()

# item for Category 1

FirstCategory = Category(user_id=1, name="Soccer")

session.add(FirstCategory)
session.commit()

item1 = Item(user_id=1, name="Soccer Cleats",
             description="Cleats or studs are protrusions on the sole of \
a shoe, or on an external attachment to a shoe, that provide additional \
traction on a soft or slippery surface. They can be conical or blade-like \
in shape, and made of plastic, rubber or metal.",
             item_category=FirstCategory)

session.add(item1)
session.commit()

item2 = Item(user_id=1, name="Jersey", description="The Laws of the Game \
set out the basic equipment which must be worn by all players in Law 4:\
The Players Equipment. Five separate items are specified: shirt \
(also known as a jersey), shorts, socks (also known as stockings),\
footwear and shin pads Goalkeepers are allowed to wear tracksuit \
bottoms instead of shorts", item_category=FirstCategory)

session.add(item2)
session.commit()

item3 = Item(user_id=1, name="Shinguard", description=" shin guard or shin\
pad is a piece of equipment worn on the front of a players shin to protect\
... Different player positions in association football require their shin \
guards to provide different types of protection and fit.",
             item_category=FirstCategory)

session.add(item3)
session.commit()

item4 = Item(user_id=1, name="Two Shinguard", description="Shin guards are\
as much a part of the players uniform as cleats or a jersey.  A required \
piece of equipment, it can be hard to decide which shinguard is right for \
you. For example, a midfielder may not require the same type of guard as a \
forward. A youth player will not wear the same type guard as an older \
player.", item_category=FirstCategory)

session.add(item4)
session.commit()

# Item for Category 2

SecondCategory = Category(user_id=1, name="Basketball")

session.add(SecondCategory)
session.commit()


# item for Category 3

ThirdCategory = Category(user_id=1, name="Baseball")

session.add(ThirdCategory)
session.commit()

item1 = Item(user_id=1, name="Bat", description="The Basketball Arbitral\
Tribunal (BAT) is an independent body, officially recognised by FIBA and \
outlined by the FIBA General Statutes, providing services for the rapid \
and simple resolution of disputes between players, agents, coaches and \
clubs through arbitration.", item_category=ThirdCategory)

session.add(item1)
session.commit()


# item for Category 4

FourthCategory = Category(user_id=1, name="Frisbee")

session.add(FourthCategory)
session.commit()

item1 = Item(user_id=1, name="Frisbee", description="A frisbee is a \
gliding toy or sporting item that is generally plastic and roughly 20 to \
25 centimetres (8 to 10 in) in diameter with a lip",
             item_category=FourthCategory)

session.add(item1)
session.commit()

# item for Category 5

FifthCategory = Category(user_id=1, name="Snowboarding")

session.add(FifthCategory)
session.commit()

item1 = Item(user_id=1, name="Goggles", description="All ski and \
snowboard goggles will offer some basic protection from wind and cold.",
             item_category=FifthCategory)

session.add(item1)
session.commit()

item2 = Item(user_id=1, name="Snowboard", description="Snowboarding is a \
winter sport that involves descending a slope that is covered with snow \
while standing on a board attached to a riders feet, using a special boot \
set onto a mounted binding.", item_category=FifthCategory)

session.add(item2)
session.commit()

# item for Category 6

SixthCategory = Category(user_id=1, name="Hockey")

session.add(SixthCategory)
session.commit()

item1 = Item(user_id=1, name="Stick", description="A hockey stick is a \
piece of equipment used by the players in most forms of hockey to move \
the ball or puck", item_category=SixthCategory)

session.add(item1)
session.commit()


print "added categories items !"
