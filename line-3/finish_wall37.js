'use strict';
// Use only the generated addition; preserve ancestral wall pixels exactly.
const fs=require('fs'),crypto=require('crypto'),assert=require('assert');
const {readPNG,writePNG}=require('./finish_wall36.js');
const jpeg=require('./tools/corpus-change-receipt/vendor/jpeg-js/lib/encoder.js');
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const path='artifacts/line-3/wall-v18.png';
const original=fs.readFileSync('artifacts/line-3/wall-v17.png');
const draftBytes=fs.readFileSync(path),old=readPNG(original),draft=readPNG(draftBytes);
assert.deepEqual([old.width,old.height],[1254,1254]);
assert.deepEqual([draft.width,draft.height],[1254,1254]);
assert(!fs.existsSync('dist/line-3/37.json'));
const rect=[950,150,140,85],pixels=Buffer.from(old.pixels);
let changed=0;
for(let y=150;y<235;y++)for(let x=950;x<1090;x++) {
 const at=(y*1254+x)*3;
 const [r,g,b]=draft.pixels.subarray(at,at+3),[or,og,ob]=old.pixels.subarray(at,at+3);
 let color;
 if(r>65&&r>g*1.65&&g>b*1.16&&r-g>or-og+10)color=[139,55,29];
 else if(r<72&&g<62&&b<53&&or-r>30&&og-g>20)color=[38,29,23];
 else if(r>145&&g>130&&b>100&&g>og*1.3&&b>ob*1.3)color=[206,191,165];
 else continue;
 for(let c=0;c<3;c++)pixels[at+c]=Math.round(old.pixels[at+c]*.24+color[c]*.76);
}
let outside=0;
for(let i=0;i<1254*1254;i++)if(!pixels.subarray(i*3,i*3+3).equals(old.pixels.subarray(i*3,i*3+3))) {
 changed++;let x=i%1254,y=Math.floor(i/1254);
 if(x<950||x>=1090||y<150||y>=235)outside++;
}
assert(changed>0);assert.equal(outside,0);
const png=writePNG(1254,1254,pixels);assert(readPNG(png).pixels.equals(pixels));
const rgba=Buffer.alloc(512*512*4);
for(let y=0;y<512;y++)for(let x=0;x<512;x++) {
 const xa=Math.floor(x*1254/512),xb=Math.floor((x+1)*1254/512);
 const ya=Math.floor(y*1254/512),yb=Math.floor((y+1)*1254/512);
 for(let c=0;c<3;c++) {
  let sum=0;for(let yy=ya;yy<yb;yy++)for(let xx=xa;xx<xb;xx++)sum+=pixels[(yy*1254+xx)*3+c];
  rgba[(y*512+x)*4+c]=Math.round(sum/((xb-xa)*(yb-ya)));
 }
 rgba[(y*512+x)*4+3]=255;
}
const thumb=jpeg({data:rgba,width:512,height:512},77).data;
assert(thumb.length<100000);
fs.writeFileSync(path,png);
fs.unlinkSync('artifacts/line-3/wall.png');fs.symlinkSync('wall-v18.png','artifacts/line-3/wall.png');
fs.writeFileSync('dist/line-3/37.jpg',thumb,{flag:'wx'});
const record={name:'The Remembered Pair',image:'https://api.imd.fun/artifacts/'+sha(png),attributes:[
 ['Cave','Crystal'],['Wall','Line 3'],['Number',37],['Left behind','Search Replay'],
 ['Meaning','Two ochre stones inside a charcoal loop recall a saved search checked against its source snapshot.'],
 ['One thing','Offline document search with exact source line citations']
].map(([trait_type,value])=>({trait_type,value}))};
fs.writeFileSync('dist/line-3/37.json',JSON.stringify(record,null,2)+'\n',{flag:'wx'});
const report={wall:path,format:'PNG',dimensions:[1254,1254],mode:'RGB',bytes:png.length,sha256:sha(png),
 ancestor_sha256:sha(original),generated_draft_sha256:sha(draftBytes),new_mark_rectangle:rect,
 changed_pixels:changed,changed_pixels_outside_rectangle:outside,
 thumbnail:{path:'dist/line-3/37.jpg',format:'JPEG',dimensions:[512,512],bytes:thumb.length},
 hand_review:{new_hands:0,new_handprints:0,inherited_main_spread_hand_visible_digits:5,inherited_gripping_hand_total_digits:'unverified due to occlusion; unchanged'},
 visual_review:'Pending final inspection',unmet_visual_requirements:['An inherited partly occluded gripping hand cannot be confirmed to have five digits; preserved unchanged.']};
fs.writeFileSync('line-3/IMAGE-37.json',JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify(report,null,2));
