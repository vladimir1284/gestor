# Gestor

This is a custom ERP for a small trailer repair business.

## Models

### Utils

This application includes two abstract models for **Transaction** and **Category**. The
**Order** model is common to [Inventory](#Inventory) and [Services](#Services)

![Utils UML diagram](https://raw.githubusercontent.com/vladimir1284/gestor/master/utils_models.png)

### Inventory
The main model in this application is the **Product** which can be either a *part* or a *consumable* that can 
be stored and counted.
The **Unit** model allows to store, buy and sell products in different measurement unit, handling automatically 
the unit conversion. Units are divided into magnitudes (Quantity), such as mass, distance etc. The base unit for conversion is always from the [ISU](https://en.wikipedia.org/wiki/International_System_of_Units).

The **ProductCategory** is used for filtering in the user interface. The **ProductTransaction** represents the buy of sell transaction within a given **Order**. There can be several **PriceReference** for a product, holding 
the link and price reference form and online store.

![Inventory UML diagram](https://raw.githubusercontent.com/vladimir1284/gestor/master/inventory_models.png)

### Services

![Services UML diagram](https://raw.githubusercontent.com/vladimir1284/gestor/master/services_models.png)

### Complete scheme
This is a complete representation of models in the system
![Models UML diagram](https://raw.githubusercontent.com/vladimir1284/gestor/master/models.png)