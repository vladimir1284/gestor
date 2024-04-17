let tables = document.getElementsByTagName("tbody");
window.onload = function() {
  let add = document.getElementsByClassName("add")[0];
  if (add.style.visibility != "hidden") {
    $(add).tooltip("show");
  }
};
function filterTag(tagName) {
  let i, j;

  let title_tag = document.getElementById("filter_tag");
  if (tagName == "all") {
    title_tag.innerHTML = "";
    let search = document.getElementById("search");
    search.value = "";
  } else {
    title_tag.innerHTML = "(" + tagName + ")";
  }
  let tables = document.getElementsByTagName("tbody");
  for (j = 0; j < tables.length; j++) {
    let tr = tables[j].getElementsByTagName("tr");
    for (i = 0; i < tr.length; i++) {
      if (tr[i].dataset["tag"] == tagName || tagName == "all") {
        tr[i].style.display = "";
      } else {
        tr[i].style.display = "none";
      }
    }
  }
}

function sort(th) {
  // const th = e.target;
  // if TH, then sort
  // cellIndex is the number of th:
  //   0 for the first column
  //   1 for the second column, etc
  const tableElement = th.closest("table");

  const ths = tableElement.querySelectorAll("th");
  ths.forEach((e) => {
    const sortables = e.querySelectorAll(".sortable");
    sortables.forEach((s) => {
      s.classList.remove(SortClass);
    });

    if (e === th) {
      return;
    }
    e.dataset.order = 0;
  });

  // Get the tbody element associated with the table
  const tbodyElement = tableElement.querySelector("tbody");

  const sorted = sortGrid(tbodyElement, th, th.cellIndex, th.dataset.type);

  if (sorted == 1) {
    let sortable = undefined;
    if (th.dataset.reversed == 1) {
      sortable = th.querySelector(".sortable.up");
    } else {
      sortable = th.querySelector(".sortable.down");
    }
    sortable.classList.add(SortClass);
    th.dataset.order = 1;
  }
}

const SortClass = "text-primary";

let grids = document.getElementsByTagName("table");
const ths = document.querySelectorAll("table th");
ths.forEach((th) => {
  if (!th.dataset.type) return;

  const sortable = document.createElement("span");
  sortable.className = "sortable-box d-flex flex-column text-light";

  const up = document.createElement("i");
  sortable.appendChild(up);
  up.className = "sortable up p-0 m-0 bx bxs-up-arrow";

  const down = document.createElement("i");
  sortable.appendChild(down);
  down.className = "sortable down p-0 m-0 bx bxs-down-arrow";

  const content = document.createElement("div");
  content.classList.add("flex-fill");
  content.classList.add("pe-2");
  content.innerHTML = th.innerHTML;
  th.innerHTML = "";

  const box = document.createElement("div");
  box.className = "d-flex align-items-center";
  box.appendChild(content);
  box.appendChild(sortable);
  th.appendChild(box);
  th.classList.add("cursor-pointer");

  th.onclick = (e) => {
    sort(th);
  };
  if (th.dataset.defsort == "+" || th.dataset.defsort == "-") {
    if (th.dataset.defsort == "-") {
      th.dataset.order = 1;
    }
    sort(th);
  }
});

function sortGrid(tbody, th, colNum, type) {
  let rowsArray = Array.from(tbody.rows);

  // compare(a, b) compares two rows, need for sorting
  let compare;

  let reversed = 0;

  switch (type) {
    case "amount":
      reversed = 1;
      compare = function(rowA, rowB) {
        return (
          rowA.cells[colNum].innerHTML.replace("$", "") -
          rowB.cells[colNum].innerHTML.replace("$", "")
        );
      };
      break;
    case "days":
      reversed = 1;
      compare = function(rowA, rowB) {
        const d =
          rowA.cells[colNum].dataset.days - rowB.cells[colNum].dataset.days;
        if (d == 0) return 1;
        return d;
      };
      break;
    case "number":
      compare = function(rowA, rowB) {
        return rowA.cells[colNum].innerHTML - rowB.cells[colNum].innerHTML;
      };
      break;
    case "custom-number":
      compare = function(rowA, rowB) {
        return (
          rowA.cells[colNum].dataset["custom"] -
          rowB.cells[colNum].dataset["custom"]
        );
      };
      break;
    case "string":
      compare = function(rowA, rowB) {
        return rowA.cells[colNum].innerHTML > rowB.cells[colNum].innerHTML
          ? 1
          : -1;
      };
      break;
    case "custom-string":
      compare = function(rowA, rowB) {
        return rowA.cells[colNum].dataset["custom"] >
          rowB.cells[colNum].dataset["custom"]
          ? 1
          : -1;
      };
      break;
    default:
      return 0;
  }

  if (th.dataset.order == 1) {
    reversed = 1 - th.dataset.reversed;
  }
  th.dataset.reversed = reversed;

  // sort
  rowsArray.sort(compare);
  if (reversed == 1) {
    console.log("reversed");
    let reversedArray = rowsArray.reverse();
    tbody.append(...reversedArray);
  } else {
    console.log("normal");
    tbody.append(...rowsArray);
  }

  return 1;
}
