import mysql from 'mysql2/promise';

const connection = await mysql.createConnection({
    host: 'localhost',
    port: 3306,
    user: 'root',
    password: '123456',
    database: 'cf',
});

console.log('db connected');

export default connection;