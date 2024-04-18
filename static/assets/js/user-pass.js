function randomChar(map) {
  const idx = Math.floor(Math.random() * map.length);
  return map.charAt(idx);
}

function choiceEle(els) {
  const idx = Math.floor(Math.random() * els.length);
  return els.splice(idx, 1);
}

function choice(els, map) {
  if (Math.random() < 0.3) {
    return choiceEle(els);
  }
  return randomChar(map);
}

function autoGenPass() {
  const length = 10;
  const letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz";
  const digits = "0123456789";
  const spec = "+-@#/.&";
  const all = letters + digits;

  const els = [randomChar(letters), randomChar(digits), randomChar(spec)];

  let pass = "";

  while (pass.length + els.length < length) {
    pass += choice(els, all);
  }

  while (els.length > 0) {
    pass += choiceEle(els);
  }

  return pass;
}

document.addEventListener("alpine:init", () => {
  Alpine.data("userPass", () => ({
    passOShow: false,
    pass1Show: false,
    pass2Show: false,

    togglePassO() {
      this.passOShow = !this.passOShow;
    },
    togglePass1() {
      this.pass1Show = !this.pass1Show;
    },
    togglePass2() {
      this.pass2Show = !this.pass2Show;
    },

    randomPass() {
      const pass = autoGenPass();
      this.$refs.pass1.value = pass;
      this.$refs.pass2.value = pass;
    },
  }));

  // pass inputs
  Alpine.bind("passO", () => ({
    "x-ref": "passO",
    ":type"() {
      return this.passOShow ? "text" : "password";
    },
  }));

  Alpine.bind("pass1", () => ({
    "x-ref": "pass1",
    ":type"() {
      return this.pass1Show ? "text" : "password";
    },
  }));

  Alpine.bind("pass2", () => ({
    "x-ref": "pass2",
    ":type"() {
      return this.pass2Show ? "text" : "password";
    },
  }));

  // pass buttons
  Alpine.bind("butPassO", () => ({
    ":class"() {
      return this.passOShow ? "bx bx-show" : "bx bx-hide";
    },
    "@click"() {
      this.togglePassO();
    },
  }));

  Alpine.bind("butPass1", () => ({
    ":class"() {
      return this.pass1Show ? "bx bx-show" : "bx bx-hide";
    },
    "@click"() {
      this.togglePass1();
    },
  }));

  Alpine.bind("butPass2", () => ({
    ":class"() {
      return this.pass2Show ? "bx bx-show" : "bx bx-hide";
    },
    "@click"() {
      this.togglePass2();
    },
  }));
});
