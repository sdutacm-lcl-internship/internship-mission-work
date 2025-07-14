import puppeteer from 'puppeteer';
import readline from 'readline';

const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
});

rl.on('line', async (input) => {
    const handles = input.split(/\s+/);
    let Error = false;
    const browser = await puppeteer.launch();
    const page = await browser.newPage();
    await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36 Edg/136.0.0.0');

    for(const handle of handles){
        const url = `https://codeforces.com/profile/${handle}`;
        try {
            await page.goto(url, {
                waitUntil: 'domcontentloaded'
            });
    
            const user = await page.$('.info .user-rank');
            if (!user) {
                console.log('no such handle');
                Error = true;
                continue;
            }

            const rating = await page.$eval('.info ul li span',el => el.textContent);
            const rank = await page.$eval('.info .user-rank span',el => el.textContent);
            const result = { handle };
            if(rating!=0){
                result.span = Number(rating);
                result.rank = rank.trim();
            }
    
            console.log(JSON.stringify(result));
        } catch (error) {
            console.error(`Error: ${error.message}`);
            Error = true;
        }
    }
    
        await browser.close();
        rl.close();
        if(Error){
            process.exit(1);
        }
        else{
            process.exit(0);
        }
});