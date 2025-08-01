import express from 'express';
import batchGetUserInfo from './routes/batchGetUserInfo.js';
import getUserRatings from './routes/getUserRatings.js';


const app = express();
app.use(express.json());
app.set('json spaces', 2);


const UserInfoCache = new Map();
const UserRatingsCache = new Map();


app.use('/batchGetUserInfo', batchGetUserInfo(UserInfoCache));
app.use('/getUserRatings', getUserRatings(UserRatingsCache));
app.use(express.static('dist'));

app.listen(2333, '127.0.0.1', () => {
    console.log('Server running');
});