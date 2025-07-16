import axios from 'axios';
import dayjs from 'dayjs';
import express from 'express';
import utc from 'dayjs/plugin/utc.js';
import timezone from 'dayjs/plugin/timezone.js';

dayjs.extend(utc);
dayjs.extend(timezone);

const app = express();

const UserInfoCache = new Map();
const UserRatingsCache = new Map();

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
                    timez: Date.now() + 15000,
                });

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
                errorResponse = {
                    success: false,
                    type: 2,
                    message: 'HTTP response error',
                    details: {
                        status: err.response.status,
                    }
                };
            } else if (err.request) {
                errorResponse = {
                    success: false,
                    type: 3,
                    message: 'Request error',
                };
            } else {
                errorResponse = {
                    success: false,
                    type: 4,
                    message: 'Internal Server Error',
                };
            }
            UserInfoCache.set(handle,{
                value: errorResponse,
                timez: Date.now() + 15000,
            });
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
            timez: Date.now() + 15000,
        })

        return res.status(200).send(JSON.stringify(result, null, 2));

    } catch (err) {
        if(err.response && err.response.status === 400){
            return res.status(404).send({message: 'No such handle'});
        }else if(err.response){
            return res.status(404).send({message: 'HTTP response error'});
        }else if(err.request){
            return res.status(404).send({message: 'Request error'});
        }else{
            return res.status(500).send({message: 'Internal Server Error'});
        }
    }

})
app.listen(2333, '127.0.0.1', () => {
    console.log('Server running');
});