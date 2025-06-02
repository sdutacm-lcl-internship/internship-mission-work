import axios from 'axios';
import readline from 'readline';
import processData from './processData.js';

const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
});

const fetch = async(handles) =>{
    const API_URL = `https://codeforces.com/api/user.info?handles=${handles}`;
    const UserAgent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36 Edg/137.0.0.0';
    
    try{
        const response = await axios.get(API_URL,{
            headers: {
                'User-Agent': UserAgent,
            }
        });
        if(response.data.status === 'OK'){
            const user = response.data.result[0];
            const result = processData(user);
            console.log(JSON.stringify(result));
        }
    }catch(e){
        if(e.request){
            if(e.response.data.status === 'FAILED'){
                console.log("No such handle.");
            }
            else {
                console.log("Error: No request made.");
            }
        }
        if(e.response){
            console.log(`Error: ${e.response.status}`);
        }
        else{
            console.log(`Error: ${e.message}`);
        }
    }
}

rl.on('line', (handle) => {
    fetch(handle).then(()=>{
        rl.close();
    });
});