// Used to scrape a set list of case IDs
const puppeteer = require('puppeteer');
const fs = require('fs');
const cases_to_rescrape = ['97106414', '97106429'];

(async () => {
  const browser = await puppeteer.launch({
    headless: true
  });
  const page = await browser.newPage();
  page.setDefaultNavigationTimeout(150000);

  for(var i = 0; i < cases_to_rescrape.length; i++){
    await page.goto('http://jis.36thdistrictcourt.org/ROAWEBINQ/');
    for(var b = 0; b<25;b++){
      await page.keyboard.press('ArrowRight');
      await page.keyboard.press('Backspace');
    }
    var caseId = cases_to_rescrape[i];
    console.log("Searching for case ID: " + caseId);
    await page.keyboard.type(caseId);
    await page.keyboard.press('Enter');

    try {
      await page.waitForNavigation();
    } catch (error) {
      console.log("Invalid case ID: " + caseId);
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
    console.log("completed " + i + " of " + cases_to_rescrape.length + " scrapes");
  }
  await browser.close();
})();
