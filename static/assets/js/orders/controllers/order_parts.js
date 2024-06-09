// @ts-check

globalThis.initController(
  "OrderParts",
  globalThis.ProductPartsUrl,
  globalThis.ProductTransactionPartsUrl,
  globalThis.OrderID,
  "alt+p",
  "part",
);

// /** @typedef {import('../models/product_transaction.js').ProductTransaction} */
// /** @typedef {import('../models/product_transaction.js').ProductTransactionCreation} */
// /** @typedef {import('../models/product.js').Product} */
//
// /** @type {import('alpinejs').default} */
// var Alpine;
//
// const EditQuantity = "QTY";
// const EditPrice = "PRICE";
// const EditTax = "TAX";
//
// document.addEventListener("alpine:init", () => {
//   Alpine.data("OrderParts", () => {
//     const productApiClient = new globalThis.ProductApiClient(
//       globalThis.ProductPartsUrl,
//     );
//     const productTransactionApiClient =
//       new globalThis.ProductTransactionApiClient(
//         globalThis.ProductTransactionPartsUrl,
//       );
//
//     return {
//       // Controller properties
//
//       /** @type {boolean} */
//       loadingPartsProducts: false,
//       /** @type {Array<Product>} */
//       partsProducts: [],
//       /** @type {string} */
//       searchNewProduct: "",
//       /** @type {number} */
//       newProductQty: 1,
//       /** @type {boolean} */
//       newProductTax: true,
//       /** @type {boolean} */
//       searchProductInputFocus: false,
//
//       /** @type {boolean} */
//       loading: false,
//
//       /** @type {Array<ProductTransaction>} */
//       parts: [],
//       /** @type {Array<ProductTransaction>} */
//       satisfied: [],
//       /** @type {Array<ProductTransaction>} */
//       unsatisfied: [],
//
//       satisfied_args: {
//         total: 0,
//         amount: 0,
//         tax: 0,
//       },
//       unsatisfied_args: {
//         total: 0,
//         amount: 0,
//         tax: 0,
//       },
//
//       selected: {
//         id: -1,
//         /** @type {ProductTransaction | undefined | null} */
//         ref: null,
//         editing: "",
//       },
//
//       toRemove: -1,
//       removing: false,
//
//       // Initialization
//       init() {
//         this.$watch("parts", (parts) => {
//           this.satisfied_args.total = 0;
//           this.satisfied_args.amount = 0;
//           this.satisfied_args.tax = 0;
//
//           this.unsatisfied_args.total = 0;
//           this.unsatisfied_args.amount = 0;
//           this.unsatisfied_args.tax = 0;
//
//           for (let p of parts) {
//             const amount = this.getAmount(p);
//             const tax = this.getTax(p);
//             const total = amount + tax;
//             if (p.satisfied) {
//               this.satisfied_args.total += total;
//               this.satisfied_args.amount += amount;
//               this.satisfied_args.tax += tax;
//             } else {
//               this.unsatisfied_args.total += total;
//               this.unsatisfied_args.amount += amount;
//               this.unsatisfied_args.tax += tax;
//             }
//           }
//         });
//         this.loadParts();
//         this.loadPartsProducts();
//
//         globalThis.bindShortcut("alt+p", () => {
//           this.$refs.searchProducts.focus();
//         });
//         globalThis.bindShortcut("escape", () => {
//           this.searchNewProduct = "";
//           this.$refs.searchProducts.blur();
//           this.editNothing();
//         });
//         globalThis.bindShortcut("enter", () => {
//           this.editNothing();
//         });
//       },
//
//       // Load data
//       async loadParts(loader = true) {
//         if (loader) this.loading = true;
//         try {
//           this.parts =
//             await productTransactionApiClient.getProductTransactionList(
//               globalThis.OrderID,
//             );
//           this.satisfied = [];
//           this.unsatisfied = [];
//           this.parts.forEach((p) => {
//             if (p.satisfied) {
//               this.satisfied.push(p);
//             } else {
//               this.unsatisfied.push(p);
//             }
//           });
//         } catch (e) {
//           console.error(e);
//           if (loader) {
//             globalThis.showNotify({
//               title: "Error",
//               msg: "Fail to load order parts",
//               status: "danger",
//             });
//           } else {
//             globalThis.showNotify({
//               title: "Error",
//               msg: "Fail to reload order parts",
//               status: "danger",
//             });
//           }
//         }
//         if (loader) this.loading = false;
//       },
//
//       // Load PartsProducts
//       async loadPartsProducts() {
//         this.loadingPartsProducts = true;
//         try {
//           this.partsProducts = await productApiClient.getProducts();
//         } catch (e) {
//           console.error(e);
//           globalThis.showNotify({
//             title: "Error",
//             msg: "Fail to load available parts",
//             status: "danger",
//           });
//         }
//         this.loadingPartsProducts = false;
//       },
//
//       // Get some data from specific part
//
//       /**
//        * @param {number} id
//        * @returns {string}
//        * */
//       transactionUrl(id) {
//         if (globalThis.Terminated) {
//           return globalThis.DetailTransUrl.replace("/0", `/${id}`);
//         }
//         return globalThis.UpdateTransUrl.replace("/0", `/${id}`);
//       },
//
//       /**
//        * @param {number} id
//        * @returns {string}
//        * */
//       productUrl(id) {
//         return globalThis.DetailProductUrl.replace("/0", `/${id}`);
//       },
//
//       /**
//        * Get total amount
//        * @param {ProductTransaction} part
//        * @returns {number}
//        * */
//       getAmount(part) {
//         return part.quantity * part.price;
//       },
//
//       /**
//        * Get total tax
//        * @param {ProductTransaction} part
//        * @param {boolean?} force - if true will return the total tax without checking if active or not
//        * @returns {number}
//        * */
//       getTax(part, force = false) {
//         if (!force && !part.active_tax) return 0;
//         return part.quantity * part.tax;
//       },
//
//       /**
//        * Get total Price
//        * @param {ProductTransaction} part
//        * @returns {number}
//        * */
//       getTotalPrice(part) {
//         return this.getAmount(part) + this.getTax(part);
//       },
//
//       // Operations
//
//       /**
//        * Find a part by ID
//        * @param {number} id
//        * @returns {ProductTransaction | undefined}
//        * */
//       findById(id) {
//         const part = this.parts.find((p) => p.id == id);
//         return part;
//       },
//
//       /**
//        * Find a part by product ID
//        * @param {number} id
//        * @returns {ProductTransaction | undefined}
//        * */
//       findByProductId(id) {
//         const part = this.parts.find((p) => p.product.id == id);
//         return part;
//       },
//
//       // Adding
//
//       /**
//        * Add new part from product
//        * @param {Product} product
//        * */
//       async addNewPart(product) {
//         /** @type {ProductTransactionCreation} */
//         this.searchNewProduct = "";
//
//         let addedPart = this.findByProductId(product.id);
//
//         if (!addedPart) {
//           try {
//             const part = {
//               product_id: product.id,
//               tax: product.sell_tax,
//               active_tax: this.newProductTax,
//               quantity: this.newProductQty,
//               price: product.sell_price,
//             };
//             console.log(part);
//             await productTransactionApiClient.addProductTransaction(
//               globalThis.OrderID,
//               part,
//             );
//           } catch (e) {
//             console.log(e);
//             // console.log(await e.text());
//             globalThis.showNotify({
//               title: "Error",
//               msg: "Fail to create the new part",
//               status: "danger",
//             });
//           }
//           await this.loadParts(false);
//
//           addedPart = this.findByProductId(product.id);
//         }
//
//         this.select(addedPart);
//       },
//
//       // Editing
//       /**
//        * Edit save
//        * @param {ProductTransaction} ref
//        * */
//       async editSave(ref) {
//         if (!ref.id) return;
//         try {
//           await productTransactionApiClient.updateProductTransaction(
//             globalThis.OrderID,
//             ref.id,
//             {
//               ...ref,
//               product_id: ref.product.id,
//             },
//           );
//         } catch (e) {
//           console.error(e);
//           // console.log(await e.text());
//           globalThis.showNotify({
//             title: "Error",
//             msg: "Fail to update the part",
//             status: "danger",
//           });
//           if (e instanceof Response) {
//             console.error(await e.text());
//           }
//         }
//         await this.loadParts(false);
//       },
//
//       /**
//        * If an element was selected saved
//        * */
//       async checkEditingSave() {
//         if (this.selected.ref) this.editSave(this.selected.ref);
//       },
//
//       /**
//        * Edit nothing
//        * */
//       editNothing() {
//         this.checkEditingSave();
//
//         this.selected.id = -1;
//         this.selected.ref = null;
//         this.selected.editing = "";
//       },
//
//       /**
//        * Select a part if exist
//        * @param {ProductTransaction | undefined} part
//        * @returns {ProductTransaction | undefined}
//        * */
//       select(part) {
//         this.checkEditingSave();
//
//         if (part && part.id && part.id != this.selected.id) {
//           this.selected.id = part.id;
//           this.selected.ref = part;
//           this.selected.editing = "";
//         }
//         return part;
//       },
//
//       /**
//        * Select a part if exist by id
//        * @param {number} id
//        * @returns {ProductTransaction | undefined}
//        * */
//       selectById(id) {
//         const part = this.findById(id);
//         return this.select(part);
//       },
//
//       /**
//        * Edit part quantity
//        * @param {number} id
//        * */
//       editQuantity(id) {
//         this.selectById(id);
//         this.selected.editing = EditQuantity;
//       },
//
//       /**
//        * Edit part price
//        * @param {number} id
//        * */
//       editPrice(id) {
//         this.selectById(id);
//         this.selected.editing = EditPrice;
//       },
//
//       /**
//        * Edit part tax
//        * @param {number} id
//        * */
//       editTax(id) {
//         this.selectById(id);
//         this.selected.editing = EditTax;
//       },
//
//       /**
//        * Check if editing part quantity
//        * @param {number} id
//        * @returns {boolean}
//        * */
//       editingQuantity(id) {
//         return this.selected.id == id && this.selected.editing == EditQuantity;
//       },
//
//       /**
//        * Check if editing part price
//        * @param {number} id
//        * @returns {boolean}
//        * */
//       editingPrice(id) {
//         return this.selected.id == id && this.selected.editing == EditPrice;
//       },
//
//       /**
//        * Check if editing part tax
//        * @param {number} id
//        * @returns {boolean}
//        * */
//       editingTax(id) {
//         return this.selected.id == id && this.selected.editing == EditTax;
//       },
//
//       // Remove
//
//       /**
//        * @param {number} id
//        * */
//       remove(id) {
//         this.toRemove = id;
//       },
//
//       removeCancel() {
//         this.toRemove = -1;
//       },
//
//       async doRemove() {
//         // this.loading = true;
//         this.removing = true;
//         try {
//           await productTransactionApiClient.removeProductTransaction(
//             globalThis.OrderID,
//             this.toRemove,
//           );
//           await this.loadParts(false);
//           this.toRemove = -1;
//         } catch (e) {
//           console.error(e);
//           globalThis.showNotify({
//             title: "Error",
//             msg: "Fail to remove the part",
//             status: "danger",
//           });
//         }
//         // this.loading = false;
//         this.removing = false;
//       },
//
//       showRemoveDialog() {
//         return this.toRemove != -1;
//       },
//
//       /**
//        * Get the name of the part marked for removal
//        * @returns {string | null}
//        * */
//       getToRemoveName() {
//         const part = this.findById(this.toRemove);
//         if (!part) {
//           return null;
//         }
//         return part.product.name;
//       },
//
//       // New products actions
//
//       /**
//        * Determinate if we are searching for new products
//        * @returns {boolean}
//        * */
//       newProductMode() {
//         return this.searchNewProduct != "" || this.searchProductInputFocus;
//       },
//
//       // Tools
//       /**
//        * Scroll to element
//        * @param {HTMLElement} el
//        * */
//       scrollTo(el) {
//         console.log(el);
//         setTimeout(() => {
//           el.scrollIntoView({ behavior: "smooth" });
//         }, 300);
//       },
//     };
//   });
// });
