import express from 'express';
import axios from 'axios';
import db from '../db.js';


export default function (UserInfoCache) {
    const router = express.Router();


    router.get('/', async (req, res) => {
        const URLHandles = req.query.handles;

        if (!URLHandles) {
            return res.status(200).json();
        }

        const handles = URLHandles.split(',');

        const results = handles.map(async (handle) => {
            // 查询缓存
            const cached = UserInfoCache.get(handle);
            if (cached && cached.timez > Date.now()) {
                return cached.value;
            }

            // 查询数据库
            try {
                const [rows] = await db.query(
                    `SELECT rating, \`rank\`, updated_at 
                    FROM user_info
                    WHERE handle = ?
                    AND updated_at >= NOW() -INTERVAL 30 SECOND`,
                    [handle]
                );
                if (rows.length > 0) {
                    let userInfo;
                    if (rows[0].rating !== null && rows[0].rank !== null) {
                        userInfo = {
                            success: true,
                            result: {
                                handle,
                                rating: rows[0].rating,
                                rank: rows[0].rank
                            },
                            source: 'database',
                        };
                    }else{
                        userInfo = {
                            success: true,
                            result: {
                                handle
                            },
                            source: 'database',
                        };
                    }
                    UserInfoCache.set(handle, {
                        value: userInfo,
                        timez: new Date(rows[0].updated_at).getTime() + 30000,
                    });
                    return userInfo;
                }
            } catch (e) {
                console.error(e);
                return res.status(500).json({ message: 'db error' });
            }



            // 查询 API
            const API_URL = `https://codeforces.com/api/user.info?handles=${handle}`;
            try {
                const response = await axios.get(API_URL);
                const data = response.data;

                if (data.status === 'OK') {
                    const user = data.result[0];
                    let userInfo;
                    if ('rating' in user) {
                        userInfo = {
                            success: true,
                            result: {
                                handle: user.handle,
                                rating: user.rating,
                                rank: user.rank
                            },
                            source: 'api',
                        };
                    } else {
                        userInfo = {
                            success: true,
                            result: {
                                handle: user.handle
                            },
                            source: 'api',
                        };
                    }
                    UserInfoCache.set(handle, {
                        value: userInfo,
                        timez: Date.now() + 30000,
                    });
                    await db.query(
                        `INSERT INTO user_info 
                        (handle, rating, \`rank\`, updated_at)
                        VALUES (?, ?, ?, NOW())
                        ON DUPLICATE KEY UPDATE
                        rating = VALUES(rating),
                        \`rank\`= VALUES(\`rank\`),
                        updated_at = NOW()`,
                        [handle, user.rating, user.rank]
                    );
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
                    console.error(err)
                    return {
                        success: false,
                        type: 4,
                        message: 'Internal Server Error',
                    };
                }
                UserInfoCache.set(handle, {
                    value: errorResponse,
                    timez: Date.now() + 30000,
                });
                return errorResponse;
            }
        })

        const result = await Promise.all(results);
        res.status(200).json(result);
    });
    return router;
}