// @ts-check

const elements = /** @type {NodeListOf<HTMLInputElement>}*/ (
  document.querySelectorAll("#guarantor input")
);

elements.forEach((e) => {
  if (e.type == "file") {
    return;
  }
  e.removeAttribute("required");
  e.setAttribute("x-bind:required", "has_guarantor");
});

const guarantorAvatar = /** @type {HTMLInputElement} */ (
  document.querySelector("#id_guarantor_avatar")
);
guarantorAvatar.addEventListener("change", (/**@type{Event}*/ e) => {
  const element = /**@type {HTMLInputElement}*/ (e.currentTarget);
  if (!element) return;

  const files = element.files;
  if (!files || files.length == 0) return;

  const imageFile = files[0];

  var reader = new FileReader();
  reader.onload = (e) => {
    var img = /**@type{HTMLImageElement}*/ (document.createElement("img"));
    img.onload = (event) => {
      var MAX_WIDTH = 64;
      var MAX_HEIGHT = 64;

      var width = img.width;
      var height = img.height;

      // Change the resizing logic
      if (width > height) {
        if (width > MAX_WIDTH) {
          height = height * (MAX_WIDTH / width);
          width = MAX_WIDTH;
        }
      } else {
        if (height > MAX_HEIGHT) {
          width = width * (MAX_HEIGHT / height);
          height = MAX_HEIGHT;
        }
      }
      // Dynamically create a canvas element
      var canvas = document.createElement("canvas");
      canvas.width = width;
      canvas.height = height;

      // var canvas = document.getElementById("canvas");
      var ctx = canvas.getContext("2d");

      // Actual resizing
      ctx?.drawImage(img, 0, 0, 64, 64);

      // Show resized image in preview element
      var dataurl = canvas.toDataURL(imageFile.type);
      /**@type{HTMLImageElement}*/ (
        document.querySelector("#guarantor_preview")
      ).src = dataurl;
    };
    img.src = /**@type{string}*/ (e.target?.result);
  };
  reader.readAsDataURL(imageFile);
});
