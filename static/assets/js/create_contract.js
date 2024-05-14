// @ts-check

/** @type {import('alpinejs').default} */
var Alpine;

const contractType = document.getElementById("id_contract_type");
const totalAmount = document.getElementById("div_id_total_amount");
const label = document.querySelector('label[for="id_security_deposit"]');
const version = document.querySelector("#div_id_template_version");

contractType?.setAttribute("x-model", "contractType");
totalAmount?.setAttribute("x-show", "contractType == 'lto'");
totalAmount?.setAttribute("x-cloak", "true");
label?.setAttribute(
  "x-text",
  "contractType == 'lto' ? 'Down payment*' : 'Security deposit*'",
);
version?.setAttribute("x-show", 'contractType == "rent"');
version?.setAttribute("x-cloak", "true");

document.addEventListener("alpine:init", () => {
  Alpine.data("createContract", () => {
    return {
      contractType: "rent",
    };
  });
});
