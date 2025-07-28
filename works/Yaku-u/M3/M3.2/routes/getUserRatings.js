import express, { json } from 'express';
import axios from 'axios';
import dayjs from 'dayjs';
import utc from 'dayjs/plugin/utc.js';
import timezone from 'dayjs/plugin/timezone.js';
import db from '../db.js';

dayjs.extend(utc);
dayjs.extend(timezone);

export default function (UserRatingsCache) {
    const router = express.Router();


    router.get('/', async (req, res) => {
        const handle = req.query.handle;
        if (!handle) {
            return res.status(200).send({ message: 'No handle provided' });
        }
        // 查询缓存
        const cached = UserRatingsCache.get(handle);
        if (cached && cached.timez > Date.now()) {
            return res.status(200).json(cached.value);
        }

        // 查询数据库
        let rows = [];
        try {
            [rows] = await db.query(
                `SELECT handle, contest_id, contest_name, \`rank\`, rating_updated_at, old_rating, new_rating
                FROM user_ratings
                WHERE handle = ?
                AND updated_at >= NOW() - INTERVAL 30 SECOND
                ORDER BY rating_updated_at ASC`,
                [handle]
            );
            if (rows.length > 0) {
                const result = rows.map(row => ({
                    handle: row.handle,
                    contestId: row.contest_id,
                    contestName: row.contest_name,
                    rank: row.rank,
                    ratingUpdatedAt: dayjs(row.rating_updated_at).tz('Asia/Shanghai').format('YYYY-MM-DD HH:mm:ssZ'),
                    oldRating: row.old_rating,
                    newRating: row.new_rating,
                    source: 'database',
                }));

                UserRatingsCache.set(handle, {
                    value: result,
                    timez: Date.now() + 30000,
                });

                return res.status(200).json(result);
            }
        } catch (e) {
            console.error(e);
            return res.status(500).json({ message: 'db error' });
        }


        // 查询 API
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
                source: 'api',
            }));
            UserRatingsCache.set(handle, {
                value: result,
                timez: Date.now() + 30000,
            });
            // 先插入 user_info
            const lates = result[result.length - 1];
            const latestRank = lates.rank;
            const latestRating = lates.newRating;
            await db.query(
                `INSERT INTO user_info
                (handle, rating, \`rank\`, updated_at)
                VALUES (?, ?, ?, NOW())
                ON DUPLICATE KEY UPDATE rating = VALUES(rating), \`rank\` = VALUES(\`rank\`), updated_at = NOW()`,
                [handle, latestRating, latestRank]
            );
            // 批量写入 user_ratings
            const insertPromises = result.map(r =>
                db.query(
                    `REPLACE INTO user_ratings
                    (handle, contest_id, contest_name, \`rank\`, old_rating, new_rating, rating_updated_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, NOW())`,
                    [r.handle, r.contestId, r.contestName, r.rank, r.oldRating, r.newRating, r.ratingUpdatedAt]
                )
            );
            await Promise.all(insertPromises);

            return res.status(200).json(result);
        } catch (err) {
            let errorResponse;
            let statusCode;
            if (err.response && err.response.status === 400) {
                errorResponse = { message: 'No such handle' };
                statusCode = 404;
            } else if (err.response) {
                return res.status(404).send({ message: 'HTTP response error' });
            } else if (err.request) {
                return res.status(404).send({ message: 'Request error' });
            } else {
                console.error(err);
                return res.status(500).send({ message: 'Internal Server Error' });
            }
            UserRatingsCache.set(handle, {
                value: errorResponse,
                timez: Date.now() + 30000
            });
            return res.status(statusCode).send(errorResponse);
        }
    });
    return router;
}