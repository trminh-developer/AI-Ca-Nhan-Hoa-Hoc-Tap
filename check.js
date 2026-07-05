const css = require('fs').readFileSync('current_css.css', 'utf8'); console.log(css.includes('.font-bricolage') ? 'HAS bricolage' : 'NO bricolage');
