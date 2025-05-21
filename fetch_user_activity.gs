// Configuration
const API_URL = 'your-api-url/user-activity';
const API_KEY = 'your-api-key';
const SHEET_NAME = 'User Activity'; // Name of the sheet to write to

function fetchAndWriteUserActivity() {
  try {
    // Get the active spreadsheet and create/get the target sheet
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    let sheet = ss.getSheetByName(SHEET_NAME);
    
    // Create the sheet if it doesn't exist
    if (!sheet) {
      sheet = ss.insertSheet(SHEET_NAME);
    }
    
    // Clear existing content
    sheet.clear();
    
    // Fetch data from the API
    const response = UrlFetchApp.fetch(API_URL, {
      method: 'get',
      headers: {
        'api-key': API_KEY
      },
      muteHttpExceptions: true // This helps with error handling
    });
    
    // Parse the response
    const responseData = JSON.parse(response.getContentText());
    
    if (responseData.status !== 'success') {
      throw new Error('API returned unsuccessful status');
    }
    
    const data = responseData.data;
    
    if (!data || data.length === 0) {
      throw new Error('No data returned from API');
    }
    
    // Prepare headers (column names)
    const headers = Object.keys(data[0]);
    
    // Prepare data rows
    const rows = data.map(row => headers.map(header => row[header]));
    
    // Write headers
    sheet.getRange(1, 1, 1, headers.length).setValues([headers]);
    
    // Write data
    if (rows.length > 0) {
      sheet.getRange(2, 1, rows.length, headers.length).setValues(rows);
    }
    
    // Format the sheet
    formatSheet(sheet, headers.length);
    
    Logger.log('Data successfully written to sheet');
    
  } catch (error) {
    Logger.log('Error: ' + error.toString());
    throw error;
  }
}

function formatSheet(sheet, numColumns) {
  // Format header row
  const headerRange = sheet.getRange(1, 1, 1, numColumns);
  headerRange.setBackground('#4285f4')
             .setFontColor('white')
             .setFontWeight('bold');
  
  // Auto-resize columns
  sheet.autoResizeColumns(1, numColumns);
  
  // Freeze header row
  sheet.setFrozenRows(1);
  
  // Add alternating row colors
  const dataRange = sheet.getRange(2, 1, sheet.getLastRow() - 1, numColumns);
  const rule = SpreadsheetApp.newConditionalFormatRule()
    .whenFormulaSatisfied('=ISEVEN(ROW())')
    .setBackground('#f3f3f3')
    .setRanges([dataRange])
    .build();
  
  const rules = sheet.getConditionalFormatRules();
  rules.push(rule);
  sheet.setConditionalFormatRules(rules);
}

// Function to create a time-based trigger
function createDailyTrigger() {
  // Delete any existing triggers
  const triggers = ScriptApp.getProjectTriggers();
  triggers.forEach(trigger => ScriptApp.deleteTrigger(trigger));
  
  // Create a new daily trigger
  ScriptApp.newTrigger('fetchAndWriteUserActivity')
    .timeBased()
    .everyDays(1)
    .atHour(1) // Run at 1 AM
    .create();
} 