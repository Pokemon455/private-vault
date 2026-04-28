const https = require('https');

exports.handler = async function(event) {
  if (event.httpMethod === 'OPTIONS') {
    return {statusCode:200,headers:{'Access-Control-Allow-Origin':'*','Access-Control-Allow-Headers':'Content-Type','Access-Control-Allow-Methods':'POST, OPTIONS'},body:''};
  }
  try {
    const {messages} = JSON.parse(event.body);
    const postData = JSON.stringify({model:'openai/gpt-oss-20b',messages,max_tokens:1024,temperature:0.7});
    return new Promise((resolve) => {
      const req = https.request({
        hostname:'integrate.api.nvidia.com',
        path:'/v1/chat/completions',
        method:'POST',
        headers:{'Content-Type':'application/json','Authorization':'Bearer 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','Content-Length':Buffer.byteLength(postData)}
      }, (res) => {
        let data='';
        res.on('data',c=>data+=c);
        res.on('end',()=>resolve({statusCode:res.statusCode,headers:{'Content-Type':'application/json','Access-Control-Allow-Origin':'*'},body:data}));
      });
      req.on('error',(e)=>resolve({statusCode:500,headers:{'Content-Type':'application/json'},body:JSON.stringify({error:{message:e.message}})}));
      req.write(postData);req.end();
    });
  } catch(e) {
    return {statusCode:500,headers:{'Content-Type':'application/json'},body:JSON.stringify({error:{message:e.message}})};
  }
};
