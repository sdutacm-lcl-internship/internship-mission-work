import axios from 'axios';
import readline from 'readline';
import processData from './processData.js';

const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
});

const fetch = async(handles) =>{
    const API_URL = `https://codeforces.com/api/user.info`;
    const UserAgent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36 Edg/137.0.0.0';
    
    try{
        const response = await axios.get(API_URL,{
            headers: {
                'User-Agent': UserAgent,
            },
            params: {
                handles: handles.split(' ').join(';'),
            }
        });
        if(response.data.status === 'OK'){
            const user = response.data.result;
            const result = user.map(user => processData(user));
            console.log(JSON.stringify(result, null, 2));
        }
    }catch(e){
        if(e.code){
            if(e.code === 'ECONNABORTED'){
                console.error(`Request aborted\nStatus: ${e.status}`);
            }else if(e.code === 'ERR_BAD_REQUEST'){
                console.error(`Bad request\nStatus: ${e.status}`);
            }else if(e.code === 'ERR_NETWORK'){
                console.error(`Network error\nSatus: ${e.status}`);
            }else if(e.code === 'ERR_BAD_RESPONSE'){
                console.error(`Bad response from server\nStatus: ${e.status}`);
            }else if(e.code === 'ERR_CANCELED'){
                console.error(`Request canceled\nStatus: ${e.status}`);
            }
        }
        if(e instanceof EvalError){
            console.error(`Eval error: ${e.message}`);
        }else if(e instanceof RangeError){
            console.error(`Range error: ${e.message}`);
        }else if(e instanceof ReferenceError){
            console.error(`Reference error: ${e.message}`);
        }else if(e instanceof SyntaxError){
            console.error(`Syntax error: ${e.message}`);
        }else if(e instanceof TypeError){
            console.error(`Type error: ${e.message}`); 
        }else if(e instanceof URIError){
            console.error(`URI error: ${e.message}`);
        }else{
            console.error(`Unknown error: ${e.message}`);
        }
    }
}

rl.on('line', (handle) => {
    fetch(handle).then(()=>{
        rl.close();
    });
});