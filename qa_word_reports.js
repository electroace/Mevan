const fs=require('fs'),vm=require('vm'),path=require('path');

function extractMainScript(html){
 const scripts=[...html.matchAll(/<script\b[^>]*>([\s\S]*?)<\/script\s*>/gi)]
  .map(match=>match[1]).filter(source=>source.includes('const CRITERIA=')&&source.includes('function exportDOCX('));
 if(scripts.length!==1)throw Error('Nije pronađena tačno jedna glavna skripta za Word izvoz.');
 // Compile the entire actual script; never truncate at a startup call.
 new vm.Script(scripts[0]);
 return scripts[0];
}

async function generate(outputDir){
 const html=fs.readFileSync(path.join(__dirname,'index.html'),'utf8');
 const main=extractMainScript(html);
 if(fs.existsSync(outputDir)&&fs.readdirSync(outputDir).some(name=>name.endsWith('.docx')))
  throw Error('Odredište već sadrži Word izvještaje. Odaberite novi direktorij da sačuvate prethodne rezultate.');
 const outputs=[];let lastBlob;
 const element=()=>({innerHTML:'',value:'',hidden:false,classList:{toggle(){},add(){},remove(){}},append(){},replaceChildren(){},addEventListener(){},querySelectorAll:()=>[]});
 const document={querySelector:()=>element(),querySelectorAll:()=>[],getElementById:()=>element(),createElement:()=>({...element(),click(){outputs.push({name:this.download,blob:lastBlob})}})};
 const storage={getItem:()=>null,setItem:()=>{},removeItem:()=>{}};
 const ctx={document,localStorage:storage,sessionStorage:storage,console,Blob,Uint8Array,TextEncoder,Date,Math,JSON,Number,String,Array,Promise,
  URL:{createObjectURL(b){lastBlob=b;return 'blob:mock'},revokeObjectURL(){}},setTimeout(){return 1},clearTimeout(){},
  alert(){},confirm(){return true},prompt(){return ''},fetch:async()=>({ok:true,status:200,json:async()=>({workspace:null,version:'empty'})}),location:{href:''}};
 vm.createContext(ctx);vm.runInContext(main,ctx,{timeout:10000});
 await Promise.resolve();await Promise.resolve();
 vm.runInContext(`for(const d of [...DIMS,'ALL'])for(const detailed of [false,true])exportDOCX(d,detailed);`,ctx,{timeout:20000});
 if(outputs.length!==12||new Set(outputs.map(o=>o.name)).size!==12)
  throw Error('Očekivano je 12 različitih Word izvještaja.');
 fs.mkdirSync(outputDir,{recursive:true});
 for(const output of outputs)fs.writeFileSync(path.join(outputDir,output.name),Buffer.from(await output.blob.arrayBuffer()),{flag:'wx'});
 console.log('GENERISANO',outputs.length,'DOCX izvještaja');
}

module.exports={extractMainScript};
if(require.main===module)generate(process.env.MEVAN_WORD_QA_DIR||path.join(__dirname,'qa_docx')).catch(error=>{console.error(error);process.exitCode=1});
