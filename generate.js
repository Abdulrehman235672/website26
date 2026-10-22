const fs = require('fs');
const path = require('path');

// 1. Read the CSV file and Template
const csvData = fs.readFileSync('pseo-products.csv', 'utf8');
const template = fs.readFileSync('template.html', 'utf8');

// 2. Parse CSV rows
const lines = csvData.trim().split('\n');
const headers = lines[0].split(',').map(h => h.trim());

// 3. Ensure output directory exists
const outputDir = path.join(__dirname, 'public', 'patches');
if (!fs.existsSync(outputDir)){
    fs.mkdirSync(outputDir, { recursive: true });
}

// 4. Loop through each row and compile pages
for (let i = 1; i < lines.length; i++) {
    const values = lines[i].split(',').map(v => v.trim());
    let pageHtml = template;

    headers.forEach((header, index) => {
        const regex = new RegExp(`{{${header}}}`, 'g');
        pageHtml = pageHtml.replace(regex, values[index]);
    });

    const slugIndex = headers.indexOf('pseo_slug');
    const fileName = `${values[slugIndex]}.html`;
    
    fs.writeFileSync(path.join(outputDir, fileName), pageHtml);
    console.log(`[Generated]: /public/patches/${fileName}`);
}