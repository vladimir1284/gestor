const isNumericInput = (event) => {
  const key = event.keyCode;
  return (
    (key >= 48 && key <= 57) || // Allow number line
    (key >= 96 && key <= 105) // Allow number pad
  );
};

const isModifierKey = (event) => {
  const key = event.keyCode;
  return (
    event.shiftKey === true ||
    key === 187 ||
    key === 35 ||
    key === 36 || // Allow Shift, Home, End
    key === 8 ||
    key === 9 ||
    key === 13 ||
    key === 46 || // Allow Backspace, Tab, Enter, Delete
    (key > 36 && key < 41) || // Allow left, up, right, down
    // Allow Ctrl/Command + A,C,V,X,Z
    ((event.ctrlKey === true || event.metaKey === true) &&
      (key === 65 || key === 67 || key === 86 || key === 88 || key === 90))
  );
};

const enforceFormat = (event) => {
  console.log(event.keyCode);
  // Input must be of a valid number format or a modifier key, and not longer than ten digits
  if (!isNumericInput(event) && !isModifierKey(event)) {
    event.preventDefault();
  }
};

const formatToPhone = (event) => {
  if (event.target.value.startsWith("+")) return;

  if (isModifierKey(event)) {
    return;
  }

  const input = event.target.value.replace(/\D/g, "").substring(0, 10); // First ten digits of input only
  const areaCode = input.substring(0, 3);
  const middle = input.substring(3, 6);
  const last = input.substring(6, 10);

  if (input.length > 6) {
    event.target.value = `(${areaCode}) ${middle} - ${last}`;
  } else if (input.length > 3) {
    event.target.value = `(${areaCode}) ${middle}`;
  } else if (input.length > 0) {
    event.target.value = `(${areaCode}`;
  }
};

const setInputPhoneFormatter = (input) => {
  input.addEventListener("keydown", enforceFormat);
  input.addEventListener("keyup", formatToPhone);
};

function init() {
  const phones = document.querySelectorAll('input[type="tel"]');
  phones.forEach((p) => {
    setInputPhoneFormatter(p);
  });
}

window.addEventListener("load", init);
// const inputElement = document.getElementById("phoneNumber");
// inputElement.addEventListener("keydown", enforceFormat);
// inputElement.addEventListener("keyup", formatToPhone);
