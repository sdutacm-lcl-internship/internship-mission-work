import axios from 'axios';
import express from 'express';

const app = express();

app.get('/', async(req, res) => {
    res.setHeader('Content-Type', 'application/json')

    const URLHandles = req.query.handles;
    if (!URLHandles) {
        return res.status(200).send(JSON.stringify())
    }

    const handles = URLHandles.split(',');

    const results = handles.map(async (handle) => {
        const API_URL = `https://codeforces.com/api/user.info?handles=${handle}`;
        try {
            const response = await axios.get(API_URL);
            const data = response.data;

            if (data.status === 'OK') {
                const user = data.result[0];
                if ('rating' in user) {
                    return {
                        success: true,
                        result: {
                            handle: user.handle,
                            rating: user.rating,
                            rank: user.rank
                        }
                    };
                } else {
                    return{
                        success: true,
                        result: {
                            handle: user.handle
                        }
                    };
                }
            }
        
        } catch(err) {
            if(err.response && err.response.status === 400){
                return{
                    success: false,
                    type: 1,
                    message: 'no such handle',
                }
            }else if(err.response){
                return {
                    success: false,
                    type: 2,
                    message: 'HTTP response error',
                    details: {
                        status: err.response.status,
                    }
                };
            }else if(err.request){
                return {
                    success: false,
                    type: 3,
                    message: 'Request error',
                };
            }else{
                return {
                    success: false,
                    type: 4,
                    message: 'Internal Server Error',
                };
            }
        }
    })

    const result = await Promise.all(results);
    res.status(200).send(JSON.stringify(result,null,2));
    
})


app.listen(2333, '127.0.0.1', () => {
    console.log('Server running');
});