import axios from 'axios';
import dayjs from 'dayjs';
import express from 'express';
import utc from 'dayjs/plugin/utc.js';
import timezone from 'dayjs/plugin/timezone.js';
import fs from 'fs';

dayjs.extend(utc);
dayjs.extend(timezone);

const app = express();

app.use(express.json());
app.use(express.urlencoded({ extended: true}));


const UserInfoCache = new Map();
const UserRatingsCache = new Map();


function lodafile(file, callback){
    fs.readFile(file, 'utf-8', (err, data) =>{
        if(err) return callback({});
        try{
            const Data = JSON.parse(data);
            callback(Data);
        }catch{
            callback({});
        }
    })
}

function savefile (file, data){
    fs.writeFile(file, JSON.stringify(data, null, 2), 'utf-8', (err)=>{
        if(err){
            console.error('写入失败', err);
        }else{
            console.log('写入成功');
            
        }
    })
}

// 在程序启动时加载缓存
lodafile('./data-user-info.json', (Data)=>{
    for(const key in Data){
        UserInfoCache.set(key,Data[key]);
    }
});

lodafile('./data-user-ratings.json', (Data)=>{
    for(const key in Data){
        UserRatingsCache.set(key, Data[key]);
    }
})


app.get('/batchGetUserInfo', async (req, res) => {
    res.setHeader('Content-Type', 'application/json')

    const URLHandles = req.query.handles;
    if (!URLHandles) {
        return res.status(200).send(JSON.stringify())
    }

    const handles = URLHandles.split(',');

    const results = handles.map(async (handle) => {
        const cached = UserInfoCache.get(handle);
        if(cached && cached.timez > Date.now()){
            return cached.value;
        }
        const API_URL = `https://codeforces.com/api/user.info?handles=${handle}`;
        try {
            const response = await axios.get(API_URL);
            const data = response.data;

            if (data.status === 'OK') {
                const user = data.result[0];
                let userInfo;
                if ('rating' in user) {
                    userInfo =  {
                        success: true,
                        result: {
                            handle: user.handle,
                            rating: user.rating,
                            rank: user.rank
                        }
                    };
                } else {
                    userInfo = {
                        success: true,
                        result: {
                            handle: user.handle
                        }
                    };
                }
                UserInfoCache.set(handle,{
                    value: userInfo,
                    timez: Date.now() + 30000,
                });

                savefile('./data-user-info.json', Object.fromEntries(UserInfoCache));

                return userInfo;
            }

        } catch (err) {
            let errorResponse;
            if (err.response && err.response.status === 400) {
                errorResponse = {
                    success: false,
                    type: 1,
                    message: 'no such handle',
                }
            } else if (err.response) {
                return {
                    success: false,
                    type: 2,
                    message: 'HTTP response error',
                    details: {
                        status: err.response.status,
                    }
                };
            } else if (err.request) {
                return {
                    success: false,
                    type: 3,
                    message: 'Request error',
                };
            } else {
                return {
                    success: false,
                    type: 4,
                    message: 'Internal Server Error',
                };
            }
            UserInfoCache.set(handle,{
                value: errorResponse,
                timez: Date.now() + 30000,
            });
            savefile('./data-user-info.json', Object.fromEntries(UserInfoCache));
            return errorResponse;
        }
    })

    const result = await Promise.all(results);
    res.status(200).send(JSON.stringify(result, null, 2));
});




app.get('/getUserRatings', async (req, res) => {
    res.setHeader('Content-Type', 'application/json')

    const handle = req.query.handle;
    if (!handle) {
        return res.status(200).send({ message: 'No handle provided' });
    }
    const cached = UserRatingsCache.get(handle);
    if(cached && cached.timez > Date.now()){
        return res.status(200).send(JSON.stringify(cached.value, null, 2));
    }
    const API_URL = `https://codeforces.com/api/user.rating?handle=${handle}`;
    try {
        const response = await axios.get(API_URL);
        const data = response.data;

        if (data.status !== 'OK') {
            return res.status(404).send({ message: 'No such handle' });
        }
        const result = data.result.map((user) => ({
            handle: user.handle,
            contestId: user.contestId,
            contestName: user.contestName,
            rank: user.rank,
            ratingUpdatedAt: dayjs(user.ratingUpdateTimeSeconds * 1000).tz('Asia/Shanghai').format('YYYY-MM-DD HH:mm:ssZ'),
            oldRating: user.oldRating,
            newRating: user.newRating,
        }));

        UserRatingsCache.set(handle,{
            value: result,
            timez: Date.now() + 30000,
        })

        savefile('./data-user-ratings.json', Object.fromEntries(UserRatingsCache));
        return res.status(200).send(JSON.stringify(result, null, 2));

    } catch (err) {
        let errorResponse;
        let statusCode;
        if(err.response && err.response.status === 400){
            errorResponse = {message: 'No such handle'};
            statusCode = 404;
        }else if(err.response){
            return res.status(404).send({message: 'HTTP response error'});
        }else if(err.request){
            return res.status(404).send({message: 'Request error'});
        }else{
            return res.status(500).send({message: 'Internal Server Error'});
        }
        UserRatingsCache.set(handle, {
            value: errorResponse,
            timez: Date.now() + 30000
        });
        savefile('./data-user-ratings.json', Object.fromEntries(UserRatingsCache));
        return res.status(statusCode).send(errorResponse);
    }

})


/*
app.post('/clearCache', (req, res)=>{
    const { cacheType, handles } = req.body;

    if(cacheType !== 'userInfo' && cacheType !== 'userRatings' ){
        return res.status(400).send({message: 'invalid request' });
    }

    const cache = cacheType === 'userInfo' ? UserInfoCache : UserRatingsCache;

    if(!handles){
        cache.clear();
    }else if(Array.isArray(handles) && handles.every(x => typeof x === 'string')){
        for(let handle of handles){
            cache.delete(handle);
        }
    }else{
        return res.status(400).send({message: 'invalid request'});
    }
    return res.status(200).send({message: 'ok'});
});
*/


app.listen(2333, '127.0.0.1', () => {
    console.log('Server running');
});