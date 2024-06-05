// @ts-check

/** @type {import('alpinejs').default} */
var Alpine;

/** @type {number} */
let id = 0;

/** @type {Array<string>} */
let emailDomains = ["@gmail.com", "@yahoo.com"];

/**
 * Initialize emails autocompletes
 * @param {HTMLInputElement} input - The email field
 * */
function initEmailComponent(input) {
  // Put input value into a reactive element for real time update
  const reactInput = Alpine.reactive({ value: input.value });
  input.addEventListener("input", () => {
    reactInput.value = input.value;
  });

  // Create a datalist to use for autocomplete
  const datalist = document.createElement("datalist");
  datalist.id = `EmailAutocompleteList${id}`;

  // Append the autocomplete list to the input parent element
  const ctl = /** @type {HTMLDivElement} */ (input.parentElement);
  ctl.appendChild(datalist);

  // Use the autocomplete list to autocomplete emails domain
  input.setAttribute("list", `EmailAutocompleteList${id}`);

  // Update the options for autocomplete
  Alpine.effect(() => {
    // If the email has domain, removeit
    let email = reactInput.value;
    const lastA = email.lastIndexOf("@");
    if (lastA != -1) {
      email = email.substring(0, lastA);
    }

    // Update autocomplete options by email@domain.xxx
    const options = [];
    for (let domain of emailDomains) {
      const option = document.createElement("option");
      option.value = `${email}${domain}`;
      options.push(option);
    }
    datalist.replaceChildren(...options);
  });

  // increment the id counter
  id++;
}

/**
 * Fetch emails domains from backend
 * */
async function initEmailsDomain() {
  try {
    const response = await fetch("/erp/emails_domains");
    emailDomains = await response.json();
  } catch (e) {
    console.log(e);
  }
}

/**
 * Get all emails inputs and initialize them as autocomplete components
 * */
async function initializeAllEmails() {
  await initEmailsDomain();

  const allEmailsInput = /** @type {NodeListOf<HTMLInputElement>} */ (
    document.querySelectorAll('.input-group>input[type="email"]')
  );

  for (let emailInput of allEmailsInput) {
    initEmailComponent(emailInput);
  }
}

window.addEventListener("load", initializeAllEmails);
