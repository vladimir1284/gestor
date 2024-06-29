function filter(from, showNum, filter) {
  const map = {};
  filter = filter.toLowerCase();

  let num = 0;
  for (let [name, elements] of Object.entries(from)) {
    if (name.toLowerCase().indexOf(filter) != -1) {
      map[name] = elements;
      num++;
      continue;
    }
    for (let element of elements) {
      if (element.date.toLowerCase().indexOf(filter) != -1) {
        if (map[name]) {
          map[name].push(element);
          num++;
        } else {
          map[name] = [element];
          num++;
        }
      }
    }
    if (showNum > 0 && num >= showNum) break;
  }

  return map;
}

function expand(tdcount, tdname, tableId) {
  const data = CSS.escape(tdcount.getAttribute("data"));
  const rowspan = tdcount.getAttribute("data-rowspan");
  const hidden = tdcount.getAttribute("rowspan") == 1;

  if (hidden) {
    tdcount.setAttribute("rowspan", rowspan);
    tdname.setAttribute("rowspan", rowspan);
  } else {
    tdcount.setAttribute("rowspan", 1);
    tdname.setAttribute("rowspan", 1);
  }

  const trs = document.querySelectorAll(`#${tableId} tr[data="${data}"]`);

  trs.forEach((tr) => {
    if (hidden) {
      tr.style.display = "";
      return;
    }
    tr.style.display = "none";
  });
}

function renderTable(from, tableId, expanded) {
  const body = document.querySelector(`#${tableId} tbody`);
  body.innerHTML = "";

  for (let [name, elements] of Object.entries(from)) {
    for (let [index, element] of elements.entries()) {
      const tr = document.createElement("tr");
      body.appendChild(tr);

      const date = document.createElement("td");
      tr.appendChild(date);

      if (index != 0) {
        tr.setAttribute("data", name);
        if (!expanded) tr.style.display = "none";
      } else {
        const countTD = document.createElement("td");
        const nameTD = document.createElement("td");

        tr.appendChild(nameTD);
        tr.appendChild(countTD);

        countTD.innerHTML = `${elements.length}`;
        countTD.onclick = () => {
          expand(countTD, nameTD, tableId);
        };

        countTD.className = "pointer w-3 text-primary text-center";
        countTD.setAttribute("data", name);
        countTD.setAttribute("data-rowspan", elements.length);

        if (expanded) {
          countTD.setAttribute("rowspan", elements.length);
          nameTD.setAttribute("rowspan", elements.length);
        } else {
          countTD.setAttribute("rowspan", 1);
          nameTD.setAttribute("rowspan", 1);
        }

        // nameTD.onclick = () => {
        //     expand(nameTD, tableId);
        // };

        nameTD.innerHTML = name;
      }

      const adate = document.createElement("a");
      date.appendChild(adate);
      adate.href = element.url;
      adate.innerText = element.date;

      const price = document.createElement("td");
      tr.appendChild(price);
      price.innerText = element.price;
    }
  }
}
