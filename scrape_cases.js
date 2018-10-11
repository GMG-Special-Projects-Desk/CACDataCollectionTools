// Used to scrape cases from http://jis.36thdistrictcourt.org/ROAWEBINQ/
const puppeteer = require('puppeteer');
const fs = require('fs');

//YOU CAN HAVE UP TO 10 ASYNC BROWSER INSTANCES RUNNING AT A TIME. THIS EXAMPLE HAS 2
(async () => {
  const browser = await puppeteer.launch({
    headless: true
  });
  const page = await browser.newPage();
  page.setDefaultNavigationTimeout(150000);

  var year = 2008;
  var numConsecutiveInvalids = 0;
  var encounteredDec = false;

  var stopped = true;

  for(var i = 100000; numConsecutiveInvalids<10;i++){
    if (stopped) {
      //set i to the ID of the last case you scraped, if the script stops before finishing
      i = 141877;
      stopped = false;
    }
    await page.goto('http://jis.36thdistrictcourt.org/ROAWEBINQ/');
    for(var b = 0; b<25;b++){
      await page.keyboard.press('ArrowRight');
      await page.keyboard.press('Backspace');
    }
    var yearPrefix = year.toString().substring(2);
    var caseId = yearPrefix + i.toString();
    console.log("Searching for case ID: " + caseId);
    await page.keyboard.type(caseId);
    await page.keyboard.press('Enter');

    try {
      await page.waitForNavigation();
    } catch (error) {
      console.log("Invalid case ID: " + caseId);
      if (encounteredDec && numConsecutiveInvalids > 0) {
        numConsecutiveInvalids ++;
      }
      continue;
    }

    const pageContent = await page.content();
    var fileName = 'data/'+caseId+'.html'
    fs.writeFile(fileName, pageContent, _ => console.log('Valid case ID. Written to file ' + fileName));
    //find the span with "DATE"
    var dateSpanIndex = pageContent.indexOf("&nbsp;&nbsp;DATE");
    //get the span ID of this span
    var spanId = pageContent.substring(dateSpanIndex-200, dateSpanIndex);
    spanId = spanId.substring(spanId.indexOf("<span id=")+10);
    spanId = spanId.substring(0, spanId.indexOf("\""));
    var intSpanId = parseInt(spanId.substring(9));
    //find the current date of the case in the span that is 2 spanIds later
    var caseDateSpanIndex = "dlROA_ctl" + (intSpanId + 2) + "_lblROALINE";
    var caseDateIndex = pageContent.indexOf("id=\""+caseDateSpanIndex);
    var caseDate = new Date(pageContent.substring(caseDateIndex+120, caseDateIndex+128));
    console.log("Time now: " + new Date().toString());
    console.log("Date of case: " + caseDate.toString());
    if (!encounteredDec){
      if (caseDate.getMonth() == 11) {
        encounteredDec = true;
      }
    }
    numConsecutiveInvalids = 0;
  }
await browser.close();
})();

(async () => {
  const browser = await puppeteer.launch({
    headless: true
  });
  const page = await browser.newPage();
  page.setDefaultNavigationTimeout(150000);

  var year = 2007;
  var numConsecutiveInvalids = 0;
  var encounteredDec = false;

  var stopped = true;

  for(var i = 100000; numConsecutiveInvalids<10;i++){
    if (stopped) {
      //set i to the ID of the last case you scraped, if the script stops before finishing
      i = 142168;
      stopped = false;
    }
    await page.goto('http://jis.36thdistrictcourt.org/ROAWEBINQ/');
    for(var b = 0; b<25;b++){
      await page.keyboard.press('ArrowRight');
      await page.keyboard.press('Backspace');
    }
    var yearPrefix = year.toString().substring(2);
    var caseId = yearPrefix + i.toString();
    console.log("Searching for case ID: " + caseId);
    await page.keyboard.type(caseId);
    await page.keyboard.press('Enter');

    try {
      await page.waitForNavigation();
    } catch (error) {
      console.log("Invalid case ID: " + caseId);
      if (encounteredDec && numConsecutiveInvalids > 0) {
        numConsecutiveInvalids ++;
      }
      continue;
    }

    const pageContent = await page.content();
    var fileName = 'TODO: Where the data should be stored/'+caseId+'.html'
    fs.writeFile(fileName, pageContent, _ => console.log('Valid case ID. Written to file ' + fileName));
    //find the span with "DATE"
    var dateSpanIndex = pageContent.indexOf("&nbsp;&nbsp;DATE");
    //get the span ID of this span
    var spanId = pageContent.substring(dateSpanIndex-200, dateSpanIndex);
    spanId = spanId.substring(spanId.indexOf("<span id=")+10);
    spanId = spanId.substring(0, spanId.indexOf("\""));
    var intSpanId = parseInt(spanId.substring(9));
    //find the current date of the case in the span that is 2 spanIds later
    var caseDateSpanIndex = "dlROA_ctl" + (intSpanId + 2) + "_lblROALINE";
    var caseDateIndex = pageContent.indexOf("id=\""+caseDateSpanIndex);
    var caseDate = new Date(pageContent.substring(caseDateIndex+120, caseDateIndex+128));
    console.log("Time now: " + new Date().toString());
    console.log("Date of case: " + caseDate.toString());
    if (!encounteredDec){
      if (caseDate.getMonth() == 11) {
        encounteredDec = true;
      }
    }
    numConsecutiveInvalids = 0;
  }
await browser.close();
})();
