const fs = require('fs');
let code = fs.readFileSync('frontend/src/app/LandingPage.tsx', 'utf8');

// The corruption turned a valid UTF-8 byte sequence like `C3 A0` into two characters: 
// The byte C3 became 'í' (U+00ED) and the byte A0 became U+00A0.
// So we just find U+00ED followed by any character from U+00A0 to U+00BF.
code = code.replace(/\xED([\xA0-\xBF])/g, (match, p1) => {
  return Buffer.from([0xC3, p1.charCodeAt(0)]).toString('utf8');
});

// Let's also do the same for C4 -> if C4 became something?
// Did đ (C4 91) become corrupted? No, đ is fine.

// Let's also do the same for E1 BB XX?
// Did 'ệ' (E1 BB 87) become corrupted? 'thế hệ' is fine.
// So only C3 was corrupted into í (U+00ED)!

// Wait! What about 'nhấpt'?
// "nhấpt" -> "nhất"
code = code.replace(/nhấpt/g, 'nhất');
// "cấpp" -> "cấp"
code = code.replace(/cấpp/g, 'cấp');
// "xuấpt" -> "xuất"
code = code.replace(/xuấpt/g, 'xuất');
// "vấpn" -> "vấn"
code = code.replace(/vấpn/g, 'vấn');

fs.writeFileSync('frontend/src/app/LandingPage.tsx', code, 'utf8');
console.log('Fixed mojibake!');
