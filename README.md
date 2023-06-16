# Gestor

This is a custom ERP for a small trailer repair and rental business.

## Models

### Utils
This application includes two abstract models for **Transaction** and **Category**. The
**Order** model is common to [Inventory](#Inventory) and [Services](#Services). Orders can be of type *purchase* 
or *sell*.

![Utils UML diagram](https://raw.githubusercontent.com/vladimir1284/gestor/master/utils_models.png)

### Inventory
The main model in this application is the **Product** which can be either a *part* or a *consumable* that can 
be stored and counted.
The **Unit** model allows to store, buy and sell products in different measurement unit, handling automatically 
the unit conversion. Units are divided into magnitudes (Quantity), such as mass, distance etc. The base unit for conversion is always from the [ISU](https://en.wikipedia.org/wiki/International_System_of_Units).

The **ProductCategory** is used for filtering in the user interface. The **ProductTransaction** represents the *purchase* of *service* transaction within a given **Order**. There can be several **PriceReference** for a product, holding the link and price reference from and online store.

The **ProductKit** storage a set of products and services that are usually included together in *service orders*. The 
**KitElement** creates a link between a **Product** and the **ProductKit** it belongs to. The 
**KitService** creates a link between a **Service** and the **ProductKit** it belongs to.

![Inventory UML diagram](https://raw.githubusercontent.com/vladimir1284/gestor/master/inventory_models.png)

### Services
The main model in this application is the **Service**, which includes a description and a suggested price 
for a given labor. The **ServiceCategory** is used for filtering in the user interface. The **ServiceTransaction** represents a particular labor included in a *service* **Order**. 

Each **Order** has one or several **Payment** associated when completed. **PaymentCategory** divides payments into payment methods. 

The **PendingPayment** accounts the debt payment for a given client.

The **Expense** model accounts for the Third Party Services required for the given *service* **Order**. 

![Services UML diagram](https://raw.githubusercontent.com/vladimir1284/gestor/master/services_models.png)

### Users
The **UserProfile** adds the avatar image and the phone number to the [standard django user model](https://docs.djangoproject.com/en/4.1/ref/contrib/auth/). This model stores the information of the users that can access into
the system: Admins or Mechanistic.

An **Associated** can be either a *client* or a *provider*. *Service orders* can be issued to a *client* or a 
**Company**. The abstract model **Contact** defines the fields that are common to **Company** and **Associated**.
Purchase orders are linked always to a provider*.

![Users UML diagram](https://raw.githubusercontent.com/vladimir1284/gestor/master/users_models.png)

### Equipment
The **Equipment** model is the abstract model that defines the field that are common to **Vehicles** (mostly trucks) and **Trailers**. **Equipment** can be linked into *service orders* but it is not required.

![Equipment UML diagram](https://raw.githubusercontent.com/vladimir1284/gestor/master/equipment_models.png)

### Costs
The **Cost** model is the main model in this application. Costs are discounted to compute the profit in a 
period. The **CostCategory** is used for filtering in the user interface.

![Costs UML diagram](https://raw.githubusercontent.com/vladimir1284/gestor/master/costs_models.png)

### Complete scheme
This is a complete representation of the models and their relations.

![Models UML diagram](https://raw.githubusercontent.com/vladimir1284/gestor/master/models.png)
