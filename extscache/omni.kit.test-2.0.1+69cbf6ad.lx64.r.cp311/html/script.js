function init() {
  // open results tab
  document.getElementById("defaultTab").click();

  // table is sorted by extension name initially
  this.asc = true;
  document.getElementById('ext_name').setAttribute('ov-down-arrow', '')

  // Teamcity adds a scrollbar (despite trying not to), hack to remove it when in iFrame
  if (window !== window.parent) {
    document.getElementById('ext_results').style.overflowY = 'hidden';
  }

  // report colors on by default
  toggleColors()
}
window.onload = init;

const getCellValue = (tr, idx) => tr.children[idx].innerText || tr.children[idx].textContent;

const comparer = (idx, asc) => (a, b) => ((v1, v2) =>
  v1 !== '' && v2 !== '' && !isNaN(v1) && !isNaN(v2) ? v1 - v2 : v1.toString().localeCompare(v2)
)(getCellValue(asc ? a : b, idx), getCellValue(asc ? b : a, idx));

// Sort table headers on click
document.querySelectorAll('th[ov-sortable]').forEach(th => th.addEventListener('click', (() => {
  // remove/update arrows
  document.querySelectorAll('th[ov-sortable]').forEach(th => th.removeAttribute("ov-up-arrow"));
  document.querySelectorAll('th[ov-sortable]').forEach(th => th.removeAttribute("ov-down-arrow"));
  if (this.asc == true) {
    th.setAttribute('ov-up-arrow', '')
  }
  else {
    th.setAttribute('ov-down-arrow', '')
  }
  // sort tbody tr elements
  Array.from(th.closest("table").querySelectorAll("tbody tr"))
    .sort(comparer(Array.from(th.parentNode.children).indexOf(th), this.asc = !this.asc))
    .forEach(tr => tr.parentElement.appendChild(tr));
})));

// add/remove background colors
function toggleColors() {
  document.querySelectorAll('td[ov-red]').forEach(
    td => td.classList.toggle('add-red-color')
  );
  document.querySelectorAll('td[ov-green]').forEach(
    td => td.classList.toggle('add-green-color')
  );
  document.querySelectorAll('td[ov-yellow]').forEach(
    td => td.classList.toggle('add-yellow-color')
  );
}

// toggle show failed tests vs show all test
function toggleShowSuccessful() {
  document.querySelectorAll('li.add-green-color').forEach(
    li => {
      li.style.display = li.style.display === 'none' ? '' : 'none';
    }
  );
}

// Quick and simple export a table into a csv
function download_table_as_csv(separator = ';') {
  // Select rows from table_id
  var rows = document.querySelectorAll('table[ov-results] tr');
  // Construct csv
  var csv = [];
  csv.push("sep=" + separator) // override system setting ("list separator character") in Excel
  for (var i = 0; i < rows.length; i++) {
    var row = [], cols = rows[i].querySelectorAll('td, th');
    for (var j = 0; j < cols.length; j++) {
      // Clean innertext to remove multiple spaces and jumpline (break csv)
      var data = cols[j].innerText.replace(/(\r\n|\n|\r)/gm, '').replace(/(\s\s)/gm, ' ')
      // Escape double-quote with double-double-quote (see https://stackoverflow.com/questions/17808511/properly-escape-a-double-quote-in-csv)
      data = data.replace(/"/g, '""');
      // Push escaped string
      row.push('"' + data + '"');
      // colSpan support
      if (cols[j].colSpan > 1) {
        row.push(...Array(cols[j].colSpan - 1).fill('""'))
      }
    }
    csv.push(row.join(separator));
  }
  var csv_string = csv.join('\n');
  // Download it
  var filename = 'ext_test_results_' + new Date().toLocaleDateString() + '.csv';
  var link = document.createElement('a');
  link.style.display = 'none';
  link.setAttribute('target', '_blank');
  link.setAttribute('href', 'data:text/csv;charset=utf-8,' + encodeURIComponent(csv_string));
  link.setAttribute('download', filename);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

function openTab(evt, tabName) {
  var i, tabcontent, tablinks;

  // Get all elements with class="tabcontent" and hide them
  tabcontent = document.getElementsByClassName("tabcontent");
  for (i = 0; i < tabcontent.length; i++) {
    tabcontent[i].style.display = "none";
  }

  // Get all elements with class="tablinks" and remove the class "active"
  tablinks = document.getElementsByClassName("tablinks");
  for (i = 0; i < tablinks.length; i++) {
    tablinks[i].className = tablinks[i].className.replace(" active", "");
  }

  // Show the current tab, and add an "active" class to the button that opened the tab
  document.getElementById(tabName).style.display = "block";
  evt.currentTarget.className += " active";
}
