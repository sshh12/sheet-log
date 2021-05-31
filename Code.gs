function strip(text) {
  return text.toLowerCase().replace(/[_\-\s]/g, "");
}

function getHeaderCol(sheet, title) {
  var header = sheet.getRange("A1:Z1");
  var lastCol = 999;
  for (var i = 1; i <= 26; i++) {
    var val = header.getCell(1, i).getValue();
    if (strip(val) == strip(title)) {
      return i;
    }
    if (val == "") {
      lastCol = Math.min(lastCol, i);
    }
  }
  header.getCell(1, lastCol).setFormula('"' + title + '"');
  return lastCol;
}

function findUpdateRow(sheet, key, value) {
  let col = getHeaderCol(sheet, key);
  for (let row = 1; row < sheet.getLastRow(); row++) {
    let cell = sheet.getRange(row, col);
    if (cell.getValue() == value) {
      return row;
    }
  }
  return 0;
}

function serveJSON(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(
    ContentService.MimeType.JSON
  );
}

function writeRow(sheet, row, payload) {
  for (let part of payload) {
    let col = getHeaderCol(sheet, part.key);
    if (part.type == "image_b64") {
      var data = Utilities.base64Decode(part.value);
      var blob = Utilities.newBlob(data, part.content_type, part.name);
      var img = sheet.insertImage(blob, row, col, 0, 0);
    } else if (part.type == "string") {
      var cell = sheet.getRange(row, col);
      cell.setFormula('"' + part.value + '"');
    } else if (part.type == "number") {
      var cell = sheet.getRange(row, col);
      cell.setFormula(part.value);
    }
  }
}

function writeTab(spreadsheet, name, payload) {
  var sheet = spreadsheet.insertSheet(name);
}

function doPost(e) {
  var req = JSON.parse(e.postData.contents);
  var spreadsheetId = req.spreadsheet_id;
  var spreadsheet = SpreadsheetApp.openById(spreadsheetId);
  var hasSheetLog = false;
  var sheet = null;
  for (var s of spreadsheet.getSheets()) {
    if (s.getName() == "sheetlog") {
      hasSheetLog = true;
    }
    if (s.getName() == req.sheet) {
      sheet = s;
    }
  }
  if (!hasSheetLog) {
    return serveJSON({ status: "error", error: "Permission denied." });
  }
  if (!sheet) {
    sheet = spreadsheet.insertSheet(req.sheet);
  }
  if (req.mode == "check") {
    return serveJSON({ status: "ok" });
  }
  var payload = req.payload;
  if (req.mode == "update" || req.mode == "append") {
    var row = Math.max(sheet.getLastRow() + 1, 2);
    if (req.mode == "update") {
      row = findUpdateRow(sheet, req.search_key, req.search_value);
    }
    writeRow(sheet, row, payload);
  } else if (req.mode == "append-tab") {
    writeTab(spreadsheet, req.tab_name, payload);
  }
  return serveJSON({ status: "ok" });
}
