document.addEventListener("DOMContentLoaded", () => {
  const a = document.querySelectorAll(".toggle");
  a.forEach((e) => {
    e.addEventListener("click", function () {
      let slider = this.nextElementSibling;
      if (slider.style.height) {
        slider.style.height = null;
        e.classList.remove("highlight");
      } else {
        document.querySelectorAll(".toggle.highlight").forEach((f) => {
          f.classList.remove("highlight");
          f.nextElementSibling.style.height = null;
        });
        e.classList.add("highlight");
        slider.style.height = slider.scrollHeight + "px";
      }
    })
  })

  const table = document.querySelector(".intro table");
  if (!table) {
    return;
  }

  const headerCells = Array.from(table.rows[0].cells);
  const sortState = new WeakMap();

  const parseCellValue = (value) => {
    const normalized = value.trim();
    if (normalized === "" || normalized === "-") {
      return Number.NEGATIVE_INFINITY;
    }

    const numericValue = Number(normalized);
    return Number.isNaN(numericValue) ? normalized.toLowerCase() : numericValue;
  };

  headerCells.forEach((headerCell, columnIndex) => {
    headerCell.style.cursor = "pointer";
    headerCell.title = "Click to sort";

    headerCell.addEventListener("click", () => {
      const rows = Array.from(table.rows).slice(1);
      const isNumericColumn = rows.every((row) => {
        const cellValue = row.cells[columnIndex]?.textContent.trim() ?? "";
        return cellValue === "" || cellValue === "-" || !Number.isNaN(Number(cellValue));
      });
      const defaultDirection = isNumericColumn ? "desc" : "asc";
      const currentDirection = sortState.get(headerCell) || defaultDirection;
      const nextDirection = currentDirection === "desc" ? "asc" : "desc";
      const direction = sortState.has(headerCell) ? nextDirection : defaultDirection;

      rows.sort((leftRow, rightRow) => {
        const leftValue = parseCellValue(leftRow.cells[columnIndex]?.textContent ?? "");
        const rightValue = parseCellValue(rightRow.cells[columnIndex]?.textContent ?? "");

        if (leftValue < rightValue) {
          return direction === "asc" ? -1 : 1;
        }

        if (leftValue > rightValue) {
          return direction === "asc" ? 1 : -1;
        }

        return 0;
      });

      rows.forEach((row) => table.appendChild(row));
      sortState.set(headerCell, direction === "asc" ? "asc" : "desc");

      headerCells.forEach((cell) => {
        cell.dataset.sort = "";
      });

      headerCell.dataset.sort = direction;
      headerCell.dataset.type = isNumericColumn ? "numeric" : "text";
    });
  });
})