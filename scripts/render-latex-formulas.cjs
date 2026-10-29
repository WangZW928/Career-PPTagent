// NODE_PATH points to the platform-specific MathJax installation.
const fs = require('fs');
const {mathjax} = require('mathjax-full/js/mathjax.js');
const {TeX} = require('mathjax-full/js/input/tex.js');
const {SVG} = require('mathjax-full/js/output/svg.js');
const {liteAdaptor} = require('mathjax-full/js/adaptors/liteAdaptor.js');
const {RegisterHTMLHandler} = require('mathjax-full/js/handlers/html.js');
const {AllPackages} = require('mathjax-full/js/input/tex/AllPackages.js');
const adaptor=liteAdaptor();RegisterHTMLHandler(adaptor);
const doc=mathjax.document('',{InputJax:new TeX({packages:AllPackages}),OutputJax:new SVG({fontCache:'local'})});
const [src,dest]=process.argv.slice(2);fs.mkdirSync(dest,{recursive:true});
for(const [id,tex] of Object.entries(JSON.parse(fs.readFileSync(src,'utf8')))){
 const container=doc.convert(tex,{display:true});
 const svg=adaptor.outerHTML(adaptor.firstChild(container)).replaceAll('currentColor','#172F4C');
 if(svg.includes('data-mjx-error'))throw new Error('TeX rendering error: '+id);
 fs.writeFileSync(dest+'/'+id+'.svg',svg);
}
