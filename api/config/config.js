module.exports = {
  development: {
    username: 'root',
    password: 'root',
    database: 'tts',
    host: 'mysql',
    dialect: 'mysql',
    port: process.env.DB_PORT,
  },
  production: {
    username: 'root',
    password: 'root',
    database: 'tts',
    host: 'mysql',
    dialect: 'mysql',
    port: process.env.DB_PORT,
  },
};
