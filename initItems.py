from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Department, Base, DepartmentItem

engine = create_engine('sqlite:///supermarketitems.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

session = DBSession()
department1 = Department(name="Baby Essentials")


session.add(department1)
session.commit()

departmentItem1 = DepartmentItem(
    name="Plum Organics Mighty 4",
    description="Mighty 4 pouches, a puree of organic fruits, veggies,"
    "protein and grains, are the perfect snack for toddlers. Every pouch is"
    "filled with essential nutrients from 4 food group favorites "
    "to fuel your active tot. "
    "And with amazing flavor combos squeezed into one pouch, "
    "we make it easy for your"
    "mighty one to enjoy on-the-go goodness anytime.",
    department=department1, price=1.39)

session.add(departmentItem1)
session.commit()


departmentItem2 = DepartmentItem(
    name="Nutritional Shake, Organic, Vanilla",
    description="USDA organic. Doctor developed organic nutrition. "
    "8 g protein. 3 g fiber. Gluten free. Delicious organic nutrition."
    " Doctor developed. 8 grams of organic protein. Complex carbohydrates"
    "from organic brown rice. 10 different organic fruits and veggies. "
    "21 essential vitamins & minerals. "
    "No corn syrup, artificial sweeteners, "
    "colorings, preservatives, flavors. "
    "A nutritionally complete, certified organic "
    "beverage for kids ages 1-13. Perfect for picky eaters, "
    "as a convenient breakfast, "
    "in a lunch box, or for any child that may "
    "need extra nutritional support. ",
    price=1.99, department=department1)

session.add(departmentItem2)
session.commit()


department2 = Department(name="Beer Shop")

session.add(department2)
session.commit()

departmentItem1 = DepartmentItem(
    name="Seagram's Escapes",
    description="Lemon, strawberry, watermelon & guava. "
    "Refreshing alcohol beverage. www.seagramescapes.com.",
    price=4.49, department=department2)

session.add(departmentItem1)
session.commit()


departmentItem2 = DepartmentItem(
    name="Smirnoff Ice",
    description="Made with natural lemon lime flavor "
    "and other natural flavors. "
    "Premium malt beverage with natural flavors. Please recycle. "
    "Drink responsibly. www.DRINKiQ.com. www.smirnoffice.com. "
    "Brewed and bottled by the Smirnoff Co., Plainfield, IL.",
    price=7.99,
    department=department2)

session.add(departmentItem2)
session.commit()


department3 = Department(name="Meat")

session.add(department3)
session.commit()

departmentItem1 = DepartmentItem(
    name="Boneless Beef Strip Steak 1st Cut",
    description="USDA Choice. Fresh Beef. Keeps Fresh: "
    "Air-tight packaging enables this meat to stay fresh longer, "
    "right in the fridge! We guarantee it! The Wegmans Family. "
    "Quality meats since 1916. U.S. Inspected and "
    "passed by Department of Agriculture.",
    price=8.49,
    department=department3)

session.add(departmentItem1)
session.commit()
